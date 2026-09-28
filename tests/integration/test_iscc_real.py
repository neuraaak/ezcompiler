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
import subprocess
from pathlib import Path

import pytest

from ezcompiler.adapters import InstallerFactory
from ezcompiler.services.installer_service import InstallerService
from ezcompiler.shared import CompilerConfig, InstallerConfig

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


def test_should_compile_the_standalone_script_as_generated(tmp_path: Path) -> None:
    """Success criterion 6: `generate iss` output compiles as-is. It differs
    from the ephemeral script by the #ifndef block and the verbatim icon."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "MyApp.exe").write_bytes(b"MZ" + b"\x00" * 128)
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")
    config = CompilerConfig(
        version="1.2.3",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=bundle,
        installer=InstallerConfig(enabled=True, per_user=True, add_to_path=True),
    )
    script = InstallerService.generate_iss_script(
        config, tmp_path / "setup.iss", force=True
    )
    out_dir = tmp_path / "out"

    iscc = shutil.which("ISCC.exe") or shutil.which("ISCC")
    assert iscc is not None
    result = subprocess.run(  # noqa: S603
        [
            iscc,
            f"/DMyAppVersion={config.version}",
            "/DVersionInfo=1.2.3.0",
            f"/DBundleDir={bundle.resolve()}",
            f"/DOutputDir={out_dir.resolve()}",
            "/DMainExe=MyApp.exe",
            str(script),
        ],
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout.decode("utf-8", "replace")
    assert list(out_dir.glob("*.exe"))
