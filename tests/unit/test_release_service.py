from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.services.release_service import ReleaseService


class _FakeReleaser:
    def release(self, bundle_dir, app_name, version, repo_dir, *, patch=True) -> Path:
        out = repo_dir / "repository"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def get_releaser_name(self) -> str:
        return "fake"


def test_release_without_publish(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _FakeReleaser(),
    )
    uploads: list[tuple] = []
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
    monkeypatch.setattr(
        "ezcompiler.services.release_service.UploaderService.upload",
        lambda **kwargs: uploads.append(kwargs),
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
    assert uploads[0]["source_path"] == tmp_path / "repo" / "repository"


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
