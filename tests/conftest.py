# ///////////////////////////////////////////////////////////////
# CONFTEST - Pytest configuration and fixtures
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Pytest configuration and shared fixtures for EzCompiler tests.

This module provides common fixtures and pytest configuration used across
all test suites (unit, integration, robustness) for consistent test execution.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import tempfile
from collections.abc import Generator
from pathlib import Path

# Third-party imports
import pytest

# ///////////////////////////////////////////////////////////////
# FIXTURES - TEMPORARY RESOURCES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """
    Create a temporary directory for tests.

    Automatically creates and cleans up a temporary directory for each test,
    ensuring isolation and cleanup between tests.

    Yields:
        Path: Temporary directory path (created and accessible during test)

    Example:
        >>> def test_with_temp_dir(temp_dir):
        ...     test_file = temp_dir / "test.txt"
        ...     test_file.write_text("content")
        ...     assert test_file.exists()
    """
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """
    Provide a temporary file path inside the temporary directory.

    The file path is created but the file itself is not created automatically.
    Tests can decide how to use the path (create the file, or just use the path).

    Args:
        temp_dir: Temporary directory fixture (injected by pytest)

    Returns:
        Path: Path to a temporary file (not yet created)

    Example:
        >>> def test_temp_file(temp_file):
        ...     # File doesn't exist yet
        ...     assert not temp_file.exists()
        ...     # Test can create it
        ...     temp_file.write_text("test")
        ...     assert temp_file.exists()
    """
    return temp_dir / "temp_file"


# ///////////////////////////////////////////////////////////////
# FIXTURES - REAL TUF TREE
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def make_tuf_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build a real, signed tufup repository under ``tmp_path``.

    tufup writes ``.tufup-repo-config`` in the current directory during
    init, so the test runs from ``tmp_path``.
    """
    pytest.importorskip("tufup")
    monkeypatch.chdir(tmp_path)
    from ezcompiler.adapters._tufup_releaser import TufupReleaser  # noqa: PLC0415

    def _make(
        versions: list[str],
        *,
        app: str = "App",
        required: tuple[str, ...] = (),
    ) -> tuple[Path, Path]:
        repo_dir = tmp_path / "repo"
        keys_dir = tmp_path / "keystore"
        releaser = TufupReleaser({"keys_dir": keys_dir})
        releaser.init_keys(app, repo_dir, keys_dir)
        for version in versions:
            bundle = tmp_path / f"bundle-{version}"
            bundle.mkdir()
            (bundle / "app.exe").write_bytes(version.encode() * 1000)
            releaser.release(
                bundle, app, version, repo_dir, required=version in required
            )
        return repo_dir, keys_dir

    return _make
