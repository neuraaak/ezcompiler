from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ezcompiler.services.release_service import ReleaseService


class _FakeReleaser:
    def release(
        self, bundle_dir, app_name, version, repo_dir, *, patch=True, required=False
    ) -> Path:
        out = repo_dir / "repository"
        (out / "metadata").mkdir(parents=True, exist_ok=True)
        (out / "metadata" / "root.json").write_text("{}", encoding="utf-8")
        return out

    def get_releaser_name(self) -> str:
        return "fake"


def test_release_without_publish(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _FakeReleaser(),
    )
    uploads: list[dict[str, Any]] = []
    monkeypatch.setattr(
        "ezcompiler.services.release_service.UploaderService.upload",
        lambda **kwargs: uploads.append(kwargs),
        raising=False,
    )

    result = ReleaseService().release_and_publish(
        bundle_dir=tmp_path / "bundle",
        app_name="MyApp",
        version="1.0.0",
        repo_dir=tmp_path / "repo",
    )

    assert result == tmp_path / "repo" / "repository"
    assert uploads == []


def test_release_with_publish_delegates_to_uploader(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _FakeReleaser(),
    )
    uploads: list[dict] = []

    def _record(**kwargs) -> None:
        src: Path = kwargs["source_path"]
        files = {p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()}
        uploads.append({**kwargs, "files": files})

    monkeypatch.setattr(
        "ezcompiler.services.release_service.UploaderService.upload",
        _record,
        raising=False,
    )

    ReleaseService().release_and_publish(
        bundle_dir=tmp_path / "bundle",
        app_name="MyApp",
        version="1.0.0",
        repo_dir=tmp_path / "repo",
        publish=True,
        upload_type="server",
        destination="https://updates.example.com",
    )

    assert len(uploads) == 1
    assert uploads[0]["upload_type"] == "server"
    assert uploads[0]["destination"] == "https://updates.example.com"
    # Copie filtrée (jamais l'arbre brut), même disposition.
    assert uploads[0]["source_path"] != tmp_path / "repo" / "repository"
    assert uploads[0]["files"] == {"metadata/root.json"}


class _FakeReleaserWithInit:
    def release(
        self, bundle_dir, app_name, version, repo_dir, *, patch=True, required=False
    ) -> Path:
        return repo_dir / "repository"

    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        return True

    def get_releaser_name(self) -> str:
        return "fake"


class _FakeReleaserInitAlreadyPresent:
    def release(
        self, bundle_dir, app_name, version, repo_dir, *, patch=True, required=False
    ) -> Path:
        return repo_dir / "repository"

    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        return False

    def get_releaser_name(self) -> str:
        return "fake-skip"


def test_init_release_returns_true_when_init_done(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _FakeReleaserWithInit(),
    )
    result = ReleaseService.init_release(
        app_name="MyApp",
        repo_dir=tmp_path / "repo",
        keys_dir=tmp_path / "keystore",
    )
    assert result is True


def test_init_release_returns_false_when_already_present(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _FakeReleaserInitAlreadyPresent(),
    )
    result = ReleaseService.init_release(
        app_name="MyApp",
        repo_dir=tmp_path / "repo",
        keys_dir=tmp_path / "keystore",
    )
    assert result is False


def test_publish_requires_destination(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _FakeReleaser(),
    )
    with pytest.raises(ValueError, match="destination"):
        ReleaseService().release_and_publish(
            bundle_dir=tmp_path / "bundle",
            app_name="MyApp",
            version="1.0.0",
            repo_dir=tmp_path / "repo",
            publish=True,
            upload_type="server",
        )


class _RecordingReleaser:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def release(
        self, bundle_dir, app_name, version, repo_dir, *, patch=True, required=False
    ) -> Path:
        self.calls.append({"version": version, "required": required})
        return repo_dir

    def get_releaser_name(self) -> str:
        return "recording"


def test_release_should_refuse_a_withdrawn_version_before_signing(
    monkeypatch, tmp_path: Path
) -> None:
    from ezcompiler.services.tuf_service import TufService
    from ezcompiler.shared.exceptions import ReleaseError

    releaser = _RecordingReleaser()
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: releaser,
    )
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    TufService.record_withdrawn(repo_dir, "1.0.1")

    with pytest.raises(ReleaseError, match="retirée"):
        ReleaseService.release_and_publish(
            bundle_dir=tmp_path, app_name="App", version="1.0.1", repo_dir=repo_dir
        )

    assert releaser.calls == []


def test_release_should_forward_required(monkeypatch, tmp_path: Path) -> None:
    releaser = _RecordingReleaser()
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: releaser,
    )

    ReleaseService.release_and_publish(
        bundle_dir=tmp_path,
        app_name="App",
        version="1.0.2",
        repo_dir=tmp_path / "repo",
        required=True,
    )

    assert releaser.calls == [{"version": "1.0.2", "required": True}]


class _PatchRecordingReleaser:
    def __init__(self) -> None:
        self.patch: bool | None = None

    def release(
        self, bundle_dir, app_name, version, repo_dir, *, patch=True, required=False
    ) -> Path:
        self.patch = patch
        return repo_dir

    def get_releaser_name(self) -> str:
        return "fake"


@pytest.mark.parametrize(("needs_full", "patch"), [(True, False), (False, True)])
def test_release_should_skip_the_patch_only_after_a_withdrawal(
    monkeypatch, tmp_path: Path, needs_full: bool, patch: bool
) -> None:
    releaser = _PatchRecordingReleaser()
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: releaser,
    )
    monkeypatch.setattr(
        "ezcompiler.services.release_service.TufService.needs_full_archive",
        lambda *_a: needs_full,
    )

    ReleaseService.release_and_publish(
        bundle_dir=tmp_path / "bundle",
        app_name="MyApp",
        version="1.0.2",
        repo_dir=tmp_path / "repo",
    )

    assert releaser.patch is patch
