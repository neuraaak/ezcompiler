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
