# ///////////////////////////////////////////////////////////////
# TEST_SKIP_BUILD - Resuming the pipeline from an existing bundle
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Verify that --skip-build reuses a compiled bundle instead of rebuilding."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ezcompiler.adapters.compiler_factory import CompilerFactory
from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.services.compiler_service import CompilerService
from ezcompiler.services.pipeline_service import PipelineService
from ezcompiler.shared._compiler_config import CompilerConfig
from ezcompiler.shared._installer_config import InstallerConfig
from ezcompiler.shared.exceptions import CompilationError


@pytest.fixture(autouse=True)
def _compilers_available(monkeypatch) -> None:
    """The adapters shell out to their compiler, so they need no import of it.

    Stub the availability probe: these tests exercise use_existing_build, not
    the install state of the optional compiler extras (absent in the docs CI
    job, which syncs only [test]).
    """
    monkeypatch.setattr(
        CompilerFactory,
        "_check_compiler_available",
        staticmethod(lambda _name: None),
    )


def _config(tmp_path: Path, *, built: bool = True, **extra) -> CompilerConfig:
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")
    output_folder = tmp_path / "dist"
    output_folder.mkdir()
    if built:
        (output_folder / "MyApp.exe").write_bytes(b"MZ")
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=output_folder,
        **extra,
    )


# ///////////////////////////////////////////////////////////////
# CompilerService.use_existing_build
# ///////////////////////////////////////////////////////////////


def test_should_reuse_build_without_compiling_when_output_exists(
    tmp_path: Path,
) -> None:
    service = CompilerService(_config(tmp_path, compiler="Cx_Freeze"))

    result = service.use_existing_build()

    assert result.compiler_name == "Cx_Freeze"
    assert result.zip_needed is True
    assert service.compiler_instance is not None


@pytest.mark.parametrize("compiler", ["PyInstaller", "Nuitka"])
def test_should_not_need_zip_when_onefile_mode(
    monkeypatch, tmp_path: Path, compiler: str
) -> None:
    monkeypatch.setattr(sys, "argv", ["ezcompiler", "--onefile"])
    service = CompilerService(_config(tmp_path))

    result = service.use_existing_build(compiler=compiler)  # type: ignore[arg-type]

    assert result.zip_needed is False


@pytest.mark.parametrize("compiler", ["PyInstaller", "Nuitka"])
def test_should_need_zip_when_not_onefile_mode(
    monkeypatch, tmp_path: Path, compiler: str
) -> None:
    monkeypatch.setattr(sys, "argv", ["ezcompiler"])
    service = CompilerService(_config(tmp_path))

    result = service.use_existing_build(compiler=compiler)  # type: ignore[arg-type]

    assert result.zip_needed is True


def test_should_raise_when_output_folder_is_empty(tmp_path: Path) -> None:
    service = CompilerService(_config(tmp_path, built=False, compiler="Cx_Freeze"))

    with pytest.raises(CompilationError, match="No existing build"):
        service.use_existing_build()


def test_should_raise_when_output_folder_is_missing(tmp_path: Path) -> None:
    config = _config(tmp_path, compiler="Cx_Freeze")
    (config.output_folder / "MyApp.exe").unlink()
    config.output_folder.rmdir()

    with pytest.raises(CompilationError, match="No existing build"):
        CompilerService(config).use_existing_build()


# ///////////////////////////////////////////////////////////////
# PipelineService
# ///////////////////////////////////////////////////////////////


def test_should_replace_version_and_compile_stages_when_build_skipped(
    tmp_path: Path,
) -> None:
    stages = PipelineService.build_stages(
        _config(tmp_path), should_zip=True, should_build=False
    )

    names = [s["name"] for s in stages]
    assert names == ["main", "compile", "zip"]
    assert "Reusing existing build" in stages[1]["description"]


def test_should_delegate_reuse_build_to_compiler_service(tmp_path: Path) -> None:
    fake_service = MagicMock()
    pipeline = PipelineService(compiler_service_factory=lambda _cfg: fake_service)

    service, result = pipeline.reuse_build(_config(tmp_path), compiler="Nuitka")

    assert service is fake_service
    assert result is fake_service.use_existing_build.return_value
    fake_service.use_existing_build.assert_called_once_with(compiler="Nuitka")


# ///////////////////////////////////////////////////////////////
# EzCompiler.run_pipeline(skip_build=True)
# ///////////////////////////////////////////////////////////////


def _make_compiler(config: CompilerConfig) -> tuple[EzCompiler, MagicMock]:
    fake_service = MagicMock()
    fake_service.use_existing_build.return_value = MagicMock(zip_needed=True)
    compiler = EzCompiler(
        config=config,
        compiler_service_factory=lambda _cfg: fake_service,
    )
    compiler._template_service = MagicMock()
    compiler._printer = MagicMock()
    return compiler, fake_service


def test_should_skip_version_and_compile_when_skip_build(tmp_path: Path) -> None:
    config = _config(tmp_path, installer=InstallerConfig(enabled=True))
    compiler, fake_service = _make_compiler(config)
    # Bound through locals: reading the assertions back off the patched
    # attributes would type-check against their real declared types.
    template_service = MagicMock()
    build_installer = MagicMock(return_value=None)
    compiler._template_service = template_service
    compiler._pipeline_service.build_installer = build_installer

    compiler.run_pipeline(skip_build=True)

    fake_service.compile.assert_not_called()
    template_service.generate_version_file.assert_not_called()
    fake_service.use_existing_build.assert_called_once()
    fake_service._zip_artifact.assert_called_once()
    build_installer.assert_called_once()


def test_should_propagate_error_when_no_existing_build(tmp_path: Path) -> None:
    compiler, fake_service = _make_compiler(_config(tmp_path, built=False))
    fake_service.use_existing_build.side_effect = CompilationError(
        "No existing build found"
    )

    with pytest.raises(CompilationError, match="No existing build"):
        compiler.run_pipeline(skip_build=True)
