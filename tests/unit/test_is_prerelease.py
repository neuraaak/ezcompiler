from __future__ import annotations

import pytest

from ezcompiler.utils import is_prerelease


@pytest.mark.parametrize(
    "version",
    [
        "1.0.0",
        "4.1.0",
        "10.20.30",
        "2026.9.30",
        "1.0.0+build.5",
        "1.0.0+alpha",
        "1.0.0+beta.1",
        "1.0.0+rc1",
    ],
)
def test_should_not_flag_stable_versions(version: str) -> None:
    assert is_prerelease(version) is False


@pytest.mark.parametrize(
    "version",
    [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-beta",
        "1.0.0-rc.1",
        "1.0.0rc1",
        "1.0.0.dev0",
        "1.0.0a0",
        "1.0.0b1",
        "1.0.0a12",
    ],
)
def test_should_flag_prerelease_versions(version: str) -> None:
    assert is_prerelease(version) is True


def test_should_be_case_insensitive() -> None:
    assert is_prerelease("1.0.0-BETA") is True


def test_should_not_flag_empty_version() -> None:
    assert is_prerelease("") is False
