from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler._types import ReleaserPort
from ezcompiler.adapters.base_releaser import BaseReleaser
from ezcompiler.shared.exceptions import BundleBuildError


class _Dummy(BaseReleaser):
    def release(self, bundle_dir, app_name, version, repo_dir, *, patch=True):
        self._validate_bundle_dir(bundle_dir)
        return repo_dir

    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        return True

    def refresh_expiration(
        self, app_name, repo_dir, keys_dir, *, roles=(...), days=None
    ):
        return repo_dir

    def get_releaser_name(self) -> str:
        return "dummy"


def test_base_releaser_conforms_to_port() -> None:
    assert isinstance(_Dummy(), ReleaserPort)


def test_validate_bundle_dir_rejects_missing(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    with pytest.raises(BundleBuildError):
        _Dummy().release(missing, "app", "1.0.0", tmp_path / "repo")


def test_validate_bundle_dir_rejects_empty(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(BundleBuildError):
        _Dummy().release(empty, "app", "1.0.0", tmp_path / "repo")
