from __future__ import annotations

from pathlib import Path

from ezcompiler._types import PublisherPort


class _Conforming:
    def preflight(self) -> None:
        return None

    def exists(self, tag: str) -> bool:
        return False

    def publish(
        self,
        assets: list[Path],
        *,
        tag: str,
        title: str,
        notes: str | None = None,
        prerelease: bool = False,
        draft: bool = False,
    ) -> str:
        return f"https://example.test/releases/{tag}"

    def get_publisher_name(self) -> str:
        return "fake"


class _NotConforming:
    def get_publisher_name(self) -> str:
        return "nope"


class _MissingExists:
    def publish(
        self,
        assets: list[Path],
        *,
        tag: str,
        title: str,
        notes: str | None = None,
        prerelease: bool = False,
        draft: bool = False,
    ) -> str:
        return ""

    def get_publisher_name(self) -> str:
        return "partial"


def test_conforming_object_is_a_publisher_port() -> None:
    assert isinstance(_Conforming(), PublisherPort)


def test_object_without_publish_is_not_a_publisher_port() -> None:
    assert not isinstance(_NotConforming(), PublisherPort)


def test_object_missing_exists_is_not_a_publisher_port() -> None:
    assert not isinstance(_MissingExists(), PublisherPort)
