from __future__ import annotations

import sys
import types as _types
from pathlib import Path

import pytest

from ezcompiler.adapters._tufup_releaser import TufupReleaser
from ezcompiler.shared.exceptions import ReleaseError, SigningKeyError


def _make_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "MyApp"
    bundle.mkdir()
    (bundle / "MyApp.exe").write_bytes(b"binary")
    return bundle


def test_release_raises_when_tufup_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setitem(sys.modules, "tufup.repo", None)  # type: ignore[arg-type]
    bundle = _make_bundle(tmp_path)
    keys = tmp_path / "keystore"
    keys.mkdir()
    with pytest.raises(ReleaseError, match="tufup"):
        TufupReleaser({"keys_dir": keys}).release(
            bundle, "MyApp", "1.0.0", tmp_path / "repo"
        )


def test_release_raises_when_keys_dir_missing(tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path)
    with pytest.raises(SigningKeyError):
        TufupReleaser({"keys_dir": tmp_path / "absent"}).release(
            bundle, "MyApp", "1.0.0", tmp_path / "repo"
        )


def test_release_calls_tufup_and_returns_repository(
    monkeypatch, tmp_path: Path
) -> None:
    calls: dict[str, object] = {}

    class _FakeRepo:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def add_bundle(self, new_bundle_dir, new_version=None, **_):
            calls["add_bundle"] = (Path(new_bundle_dir), new_version)

        def publish_changes(self, private_key_dirs=None, **_):
            calls["publish"] = private_key_dirs

    fake_repo_mod = _types.ModuleType("tufup.repo")
    fake_repo_mod.Repository = _FakeRepo  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tufup.repo", fake_repo_mod)

    bundle = _make_bundle(tmp_path)
    keys = tmp_path / "keystore"
    keys.mkdir()
    repo_dir = tmp_path / "repo"

    result = TufupReleaser({"keys_dir": keys}).release(
        bundle, "MyApp", "1.0.0", repo_dir
    )

    assert result == repo_dir / "repository"
    assert calls["add_bundle"][1] == "1.0.0"
    assert calls["publish"] == [keys]


def test_get_releaser_name() -> None:
    assert TufupReleaser().get_releaser_name() == "Tufup"


def test_init_keys_skips_when_keys_already_present(tmp_path: Path) -> None:
    keys = tmp_path / "keystore"
    keys.mkdir()
    (keys / "root.pem").write_bytes(b"fake-key")

    result = TufupReleaser().init_keys("MyApp", tmp_path / "repo", keys)

    assert result is False


def test_init_keys_raises_signing_key_error_when_keys_dir_not_creatable(
    monkeypatch, tmp_path: Path
) -> None:
    keys = tmp_path / "keystore"

    original_mkdir = Path.mkdir

    def _bad_mkdir(self: Path, **kwargs: object) -> None:
        if self == keys:
            raise OSError("permission denied")
        original_mkdir(self, **kwargs)

    monkeypatch.setattr(Path, "mkdir", _bad_mkdir)
    with pytest.raises(SigningKeyError, match="keystore"):
        TufupReleaser().init_keys("MyApp", tmp_path / "repo", keys)


def test_init_keys_calls_tufup_repository_and_returns_true(
    monkeypatch, tmp_path: Path
) -> None:
    calls: dict[str, object] = {}

    class _FakeRepo:
        def __init__(self, **kwargs: object) -> None:
            calls["init"] = kwargs

        def save_config(self) -> None:
            calls["save_config"] = True

        def initialize(self) -> None:
            calls["initialize"] = True

    fake_repo_mod = _types.ModuleType("tufup.repo")
    fake_repo_mod.Repository = _FakeRepo  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tufup.repo", fake_repo_mod)

    keys = tmp_path / "keystore"
    repo_dir = tmp_path / "repo"

    result = TufupReleaser().init_keys("MyApp", repo_dir, keys)

    assert result is True
    assert calls.get("save_config") is True
    assert calls.get("initialize") is True


def test_init_keys_wraps_tufup_exception_as_release_error(
    monkeypatch, tmp_path: Path
) -> None:
    class _BadRepo:
        def __init__(self, **_: object) -> None:
            pass

        def save_config(self) -> None:
            raise RuntimeError("disk full")

        def initialize(self) -> None:
            pass

    fake_repo_mod = _types.ModuleType("tufup.repo")
    fake_repo_mod.Repository = _BadRepo  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tufup.repo", fake_repo_mod)

    keys = tmp_path / "keystore"
    with pytest.raises(ReleaseError, match="disk full"):
        TufupReleaser().init_keys("MyApp", tmp_path / "repo", keys)
