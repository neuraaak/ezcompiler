from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared._compiler_config import CompilerConfig
from ezcompiler.shared.exceptions import InstallerError


def _base_kwargs(tmp_path: Path) -> dict:
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")
    output_folder = tmp_path / "dist"
    output_folder.mkdir()
    return {
        "version": "1.0.0",
        "project_name": "MyApp",
        "main_file": str(main_file),
        "include_files": {"files": [], "folders": []},
        "output_folder": output_folder,
    }


def _make_compiler(config: CompilerConfig) -> EzCompiler:
    fake_compiler_service = MagicMock()
    fake_compiler_service.compile.return_value = MagicMock(zip_needed=False)
    compiler = EzCompiler(
        config=config,
        compiler_service_factory=lambda _cfg: fake_compiler_service,
    )
    compiler._template_service = MagicMock()
    compiler._printer = MagicMock()
    return compiler


def test_run_pipeline_skips_installer_when_disabled(tmp_path: Path) -> None:
    config = CompilerConfig(**_base_kwargs(tmp_path))
    compiler = _make_compiler(config)
    compiler._pipeline_service.build_installer = MagicMock()

    compiler.run_pipeline(skip_zip=True)

    compiler._pipeline_service.build_installer.assert_not_called()


def test_run_pipeline_builds_installer_when_enabled(tmp_path: Path) -> None:
    kwargs = _base_kwargs(tmp_path)
    kwargs["installer_enabled"] = True
    config = CompilerConfig(**kwargs)
    compiler = _make_compiler(config)
    compiler._pipeline_service.build_installer = MagicMock(
        return_value=tmp_path / "installer" / "MyApp-1.0.0-setup.exe"
    )

    compiler.run_pipeline(skip_zip=True)

    compiler._pipeline_service.build_installer.assert_called_once()


def test_run_pipeline_propagates_installer_error(tmp_path: Path) -> None:
    kwargs = _base_kwargs(tmp_path)
    kwargs["installer_enabled"] = True
    config = CompilerConfig(**kwargs)
    compiler = _make_compiler(config)
    compiler._pipeline_service.build_installer = MagicMock(
        side_effect=InstallerError("ISCC.exe not found")
    )

    with pytest.raises(InstallerError, match="ISCC.exe"):
        compiler.run_pipeline(skip_zip=True)
