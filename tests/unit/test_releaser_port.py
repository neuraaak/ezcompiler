from __future__ import annotations

from pathlib import Path

from ezcompiler.types import ReleaserPort


class _Conforming:
    def release(
        self,
        bundle_dir: Path,
        app_name: str,
        version: str,
        repo_dir: Path,
        *,
        patch: bool = True,
    ) -> Path:
        return repo_dir

    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        return True

    def get_releaser_name(self) -> str:
        return "fake"


class _NotConforming:
    def get_releaser_name(self) -> str:
        return "nope"


class _MissingInitKeys:
    def release(
        self,
        bundle_dir: Path,
        app_name: str,
        version: str,
        repo_dir: Path,
        *,
        patch: bool = True,
    ) -> Path:
        return repo_dir

    def get_releaser_name(self) -> str:
        return "partial"


def test_conforming_object_is_a_releaser_port() -> None:
    assert isinstance(_Conforming(), ReleaserPort)


def test_missing_release_method_is_not_a_port() -> None:
    assert not isinstance(_NotConforming(), ReleaserPort)


def test_missing_init_keys_is_not_a_port() -> None:
    assert not isinstance(_MissingInitKeys(), ReleaserPort)
