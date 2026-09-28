# ///////////////////////////////////////////////////////////////
# TEST_ISCC_REAL - Installer builds against a real Inno Setup compiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Verify that real ISCC accepts generated scripts, including UTF-8 and braces."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import shutil
from pathlib import Path

import pytest

from ezcompiler.adapters import InstallerFactory
from ezcompiler.shared import InstallerConfig

# ///////////////////////////////////////////////////////////////
# MARKERS
# ///////////////////////////////////////////////////////////////

pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_iscc,
    pytest.mark.skipif(
        shutil.which("ISCC.exe") is None and shutil.which("ISCC") is None,
        reason="ISCC.exe (Inno Setup 6) not installed on PATH",
    ),
]

# ///////////////////////////////////////////////////////////////
# TESTS
# ///////////////////////////////////////////////////////////////


def test_should_build_setup_when_real_iscc_compiles_a_generated_script(
    tmp_path: Path,
) -> None:
    """Catch scripts that mocked subprocess calls accept but ISCC rejects."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "MyApp.exe").write_bytes(b"MZ" + b"\x00" * 128)
    installer = InstallerFactory.create_installer(
        "innosetup", InstallerConfig(enabled=True, per_user=True)
    )

    setup_exe = installer.build(bundle, "MyApp", "1.2.3", tmp_path / "out")

    assert setup_exe.is_file()


def test_should_build_setup_when_app_name_contains_accents_and_braces(
    tmp_path: Path,
) -> None:
    """Catch missing UTF-8 BOM and invalid literal-brace escaping end to end."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "app.exe").write_bytes(b"MZ" + b"\x00" * 128)
    installer = InstallerFactory.create_installer(
        "innosetup", InstallerConfig(enabled=True, per_user=True)
    )

    setup_exe = installer.build(bundle, "Éditeur{X}", "1.2.3", tmp_path / "out")

    assert setup_exe.is_file()


def test_should_build_setup_when_add_to_path_emits_its_code_helper(
    tmp_path: Path,
) -> None:
    """The NeedsAddPath guard is Pascal Script: only real ISCC compiles it."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "MyApp.exe").write_bytes(b"MZ" + b"\x00" * 128)
    installer = InstallerFactory.create_installer(
        "innosetup",
        InstallerConfig(
            enabled=True,
            per_user=True,
            add_to_path=True,
            extra_sections={"Code": ["procedure Unused; begin end;"]},
        ),
    )

    setup_exe = installer.build(bundle, "MyApp", "1.2.3", tmp_path / "out")

    assert setup_exe.is_file()
