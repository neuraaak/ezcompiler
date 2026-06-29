# ///////////////////////////////////////////////////////////////
# TEST SERVICES AND FACTORIES - Unit tests for service/factory behavior
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Unit tests improving coverage for services and configuration parsing."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ezcompiler.adapters import BaseFileWriter, CompilerFactory
from ezcompiler.adapters._cx_freeze_compiler import CxFreezeCompiler
from ezcompiler.adapters._disk_file_writer import DiskFileWriter
from ezcompiler.adapters._nuitka_compiler import NuitkaCompiler
from ezcompiler.adapters._pyinstaller_compiler import PyInstallerCompiler
from ezcompiler.services import (
    CompilerService,
    ConfigService,
    PipelineService,
    TemplateService,
)
from ezcompiler.shared import (
    CompilationError,
    CompilerConfig,
    ConfigurationError,
    VersionError,
)

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _build_config(temp_dir: Path) -> CompilerConfig:
    """Create a minimal valid CompilerConfig for tests."""
    main_file = temp_dir / "main.py"
    main_file.write_text("print('ok')", encoding="utf-8")

    return CompilerConfig(
        version="1.0.0",
        project_name="FactoryTests",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=temp_dir / "dist",
    )


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER FACTORY
# ///////////////////////////////////////////////////////////////


class TestCompilerFactory:
    """Test CompilerFactory behavior."""

    def test_should_create_cx_freeze_compiler_when_name_is_cx_freeze(
        self, temp_dir
    ) -> None:
        config = _build_config(temp_dir)
        with patch.object(CompilerFactory, "_check_compiler_available"):
            compiler = CompilerFactory.create_compiler(config, "Cx_Freeze")
        assert isinstance(compiler, CxFreezeCompiler)

    def test_should_create_pyinstaller_compiler_when_name_is_pyinstaller(
        self, temp_dir
    ) -> None:
        config = _build_config(temp_dir)
        with patch.object(CompilerFactory, "_check_compiler_available"):
            compiler = CompilerFactory.create_compiler(config, "PyInstaller")
        assert isinstance(compiler, PyInstallerCompiler)

    def test_should_raise_compilation_error_when_compiler_name_is_unknown(
        self, temp_dir
    ) -> None:
        config = _build_config(temp_dir)
        with pytest.raises(CompilationError):
            CompilerFactory.create_compiler(config, "unknown")


# ///////////////////////////////////////////////////////////////
# TESTS - CONFIG SERVICE + COMPILER CONFIG
# ///////////////////////////////////////////////////////////////


class TestConfigAndCompilerService:
    """Test ConfigService and CompilerService integration points."""

    def test_should_build_compiler_config_when_loading_from_json_file(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "app.py"
        main_file.write_text("print('hello')", encoding="utf-8")

        config_file = temp_dir / "ezcompiler.json"
        config_file.write_text(
            json.dumps(
                {
                    "version": "1.2.3",
                    "project_name": "JsonProject",
                    "main_file": str(main_file),
                    "include_files": {"files": [], "folders": []},
                    "output_folder": str(temp_dir / "out"),
                }
            ),
            encoding="utf-8",
        )

        config = ConfigService.build_compiler_config(config_path=config_file)

        assert config.project_name == "JsonProject"
        assert config.version == "1.2.3"

    def test_should_raise_configuration_error_when_include_files_files_is_not_list(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("print('x')", encoding="utf-8")

        with pytest.raises(ConfigurationError):
            CompilerConfig.from_dict(
                {
                    "version": "1.0.0",
                    "project_name": "InvalidIncludeFiles",
                    "main_file": str(main_file),
                    "include_files": {"files": "not-a-list", "folders": []},
                    "output_folder": str(temp_dir / "dist"),
                }
            )

    def test_should_create_compiler_instance_when_service_receives_supported_name(
        self, temp_dir
    ) -> None:
        config = _build_config(temp_dir)
        service = CompilerService(config)

        with patch.object(CompilerFactory, "_check_compiler_available"):
            compiler = service._create_compiler("Nuitka")

        assert isinstance(compiler, NuitkaCompiler)


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER FACTORY (extended)
# ///////////////////////////////////////////////////////////////


class TestCompilerFactoryExtended:
    """Test CompilerFactory edge cases and auxiliary methods."""

    def test_should_create_nuitka_compiler_when_name_is_nuitka(self, temp_dir) -> None:
        config = _build_config(temp_dir)
        with patch.object(CompilerFactory, "_check_compiler_available"):
            compiler = CompilerFactory.create_compiler(config, "Nuitka")
        assert isinstance(compiler, NuitkaCompiler)

    def test_should_return_cx_freeze_when_create_from_config_with_auto(
        self, temp_dir
    ) -> None:
        config = _build_config(temp_dir)  # compiler defaults to "auto"
        with patch.object(CompilerFactory, "_check_compiler_available"):
            compiler = CompilerFactory.create_from_config(config)
        assert isinstance(compiler, CxFreezeCompiler)

    def test_should_return_pyinstaller_when_create_from_config_with_explicit_compiler(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("print('ok')", encoding="utf-8")
        config = CompilerConfig(
            version="1.0.0",
            project_name="ExplicitCompiler",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=temp_dir / "dist",
            compiler="PyInstaller",
        )
        with patch.object(CompilerFactory, "_check_compiler_available"):
            compiler = CompilerFactory.create_from_config(config)
        assert isinstance(compiler, PyInstallerCompiler)

    def test_should_return_supported_compiler_names_when_get_supported_compilers_is_called(
        self,
    ) -> None:
        names = CompilerFactory.get_supported_compilers()
        assert set(names) == {"Cx_Freeze", "PyInstaller", "Nuitka"}


# ///////////////////////////////////////////////////////////////
# TESTS - DISK FILE WRITER
# ///////////////////////////////////////////////////////////////


class TestDiskFileWriter:
    """Test DiskFileWriter behavior."""

    def test_should_write_content_when_file_path_exists(self, temp_dir: Path) -> None:
        writer = DiskFileWriter()
        output = temp_dir / "output.txt"

        writer.write_text(output, "hello world")

        assert output.read_text(encoding="utf-8") == "hello world"

    def test_should_create_parent_dirs_when_they_do_not_exist(
        self, temp_dir: Path
    ) -> None:
        writer = DiskFileWriter()
        output = temp_dir / "nested" / "deep" / "file.txt"

        writer.write_text(output, "content")

        assert output.exists()
        assert output.read_text(encoding="utf-8") == "content"

    def test_should_respect_encoding_when_writing_file(self, temp_dir: Path) -> None:
        writer = DiskFileWriter()
        output = temp_dir / "encoded.txt"

        writer.write_text(output, "éàü", encoding="utf-8")

        assert output.read_text(encoding="utf-8") == "éàü"


# ///////////////////////////////////////////////////////////////
# TESTS - PIPELINE SERVICE
# ///////////////////////////////////////////////////////////////


class TestPipelineService:
    """Test PipelineService orchestration logic."""

    def test_should_return_true_when_zip_artifact_is_needed(
        self, temp_dir: Path
    ) -> None:
        config = _build_config(temp_dir)

        mock_compiler_service = MagicMock(spec=CompilerService)
        mock_compilation_result = MagicMock()
        mock_compilation_result.zip_needed = True

        service = PipelineService()
        result = service.zip_artifact(
            config=config,
            compiler_service=mock_compiler_service,
            compilation_result=mock_compilation_result,
        )

        assert result is True
        mock_compiler_service._zip_artifact.assert_called_once()

    def test_should_return_false_when_zip_artifact_is_not_needed(
        self, temp_dir: Path
    ) -> None:
        config = _build_config(temp_dir)

        mock_compiler_service = MagicMock(spec=CompilerService)
        mock_compilation_result = MagicMock()
        mock_compilation_result.zip_needed = False

        service = PipelineService()
        result = service.zip_artifact(
            config=config,
            compiler_service=mock_compiler_service,
            compilation_result=mock_compilation_result,
        )

        assert result is False
        mock_compiler_service._zip_artifact.assert_not_called()

    def test_should_call_uploader_service_when_upload_artifact_is_called(
        self, temp_dir: Path
    ) -> None:
        config = _build_config(temp_dir)

        mock_compilation_result = MagicMock()
        mock_compilation_result.zip_needed = False

        service = PipelineService()
        with patch(
            "ezcompiler.services.pipeline_service.UploaderService.upload"
        ) as mock_upload:
            service.upload_artifact(
                config=config,
                structure="disk",
                destination="releases/",
                compilation_result=mock_compilation_result,
            )
            mock_upload.assert_called_once()


# ///////////////////////////////////////////////////////////////
# TESTS - TEMPLATE SERVICE
# ///////////////////////////////////////////////////////////////


class TestTemplateService:
    """Test TemplateService with injected mock file writer."""

    def _make_service(self) -> tuple[TemplateService, MagicMock, MagicMock]:
        """Create a TemplateService with a mock writer and a mock template loader."""
        mock_writer = MagicMock(spec=BaseFileWriter)
        mock_loader = MagicMock()
        service = TemplateService(file_writer=mock_writer)
        service._template_loader = mock_loader  # type: ignore[assignment]
        return service, mock_writer, mock_loader

    # --- __init__ ---

    def test_should_use_disk_file_writer_when_no_writer_is_provided(self) -> None:
        from ezcompiler.adapters._disk_file_writer import DiskFileWriter

        service = TemplateService()
        assert isinstance(service._file_writer, DiskFileWriter)

    def test_should_use_injected_writer_when_file_writer_is_provided(self) -> None:
        mock_writer = MagicMock(spec=BaseFileWriter)
        service = TemplateService(file_writer=mock_writer)
        assert service._file_writer is mock_writer

    # --- generate_config_file ---

    def test_should_write_yaml_file_when_format_is_yaml(self, temp_dir: Path) -> None:
        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_config_template.return_value = "yaml: content"
        out = temp_dir / "ezcompiler.yaml"

        service.generate_config_file({}, out, format_type="yaml")

        mock_writer.write_text.assert_called_once_with(
            out, "yaml: content", encoding="utf-8"
        )

    def test_should_write_json_file_when_format_is_json(self, temp_dir: Path) -> None:
        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_config_template.return_value = '{"key": "val"}'
        out = temp_dir / "ezcompiler.json"

        service.generate_config_file({}, out, format_type="json")

        mock_writer.write_text.assert_called_once()

    def test_should_raise_template_error_when_writer_fails_in_config(
        self, temp_dir: Path
    ) -> None:
        from ezcompiler.shared.exceptions import TemplateError

        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_config_template.return_value = "content"
        mock_writer.write_text.side_effect = OSError("disk full")

        with pytest.raises(TemplateError):
            service.generate_config_file({}, temp_dir / "out.yaml")

    # --- generate_setup_file ---

    def test_should_write_setup_py_when_output_path_is_given(
        self, temp_dir: Path
    ) -> None:
        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_setup_template.return_value = "# setup"
        out = temp_dir / "setup.py"

        result = service.generate_setup_file({}, output_path=out)

        assert result == out
        mock_writer.write_text.assert_called_once_with(out, "# setup", encoding="utf-8")

    def test_should_write_setup_py_to_dir_when_output_dir_is_given(
        self, temp_dir: Path
    ) -> None:
        service, _, mock_loader = self._make_service()
        mock_loader.process_setup_template.return_value = "# setup"
        out_dir = temp_dir / "build"
        out_dir.mkdir()

        result = service.generate_setup_file({}, output_dir=out_dir)

        assert result == out_dir / "setup.py"

    def test_should_raise_template_error_when_writer_fails_in_setup(
        self, temp_dir: Path
    ) -> None:
        from ezcompiler.shared.exceptions import TemplateError

        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_setup_template.return_value = "# setup"
        mock_writer.write_text.side_effect = OSError("disk full")

        with pytest.raises(TemplateError):
            service.generate_setup_file({}, output_path=temp_dir / "setup.py")

    # --- generate_version_file ---

    def test_should_write_version_file_when_output_path_is_provided(
        self, temp_dir: Path
    ) -> None:
        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_version_template.return_value = "v1.0.0"
        out = temp_dir / "version_info.txt"

        result = service.generate_version_file({}, output_path=out)

        assert result == out
        mock_writer.write_text.assert_called_once_with(out, "v1.0.0", encoding="utf-8")

    def test_should_build_path_from_config_when_output_path_is_none(
        self, temp_dir: Path
    ) -> None:
        service, _, mock_loader = self._make_service()
        mock_loader.process_version_template.return_value = "v1.0.0"
        config = {
            "version": "1.0.0",
            "version_filename": "ver.txt",
            "output_folder": str(temp_dir / "dist"),
        }

        result = service.generate_version_file(config)

        assert result == temp_dir / "dist" / "ver.txt"

    def test_should_raise_version_error_when_writer_fails_in_version(
        self, temp_dir: Path
    ) -> None:
        service, mock_writer, mock_loader = self._make_service()
        mock_loader.process_version_template.return_value = "v1.0.0"
        mock_writer.write_text.side_effect = OSError("disk full")

        with pytest.raises(VersionError):
            service.generate_version_file({}, output_path=temp_dir / "ver.txt")

    # --- list_available_templates ---

    def test_should_return_dict_when_list_available_templates_is_called(self) -> None:
        service, _, mock_loader = self._make_service()
        mock_loader.list_available_templates.return_value = {"config": ["yaml", "json"]}

        result = service.list_available_templates()

        assert isinstance(result, dict)
        mock_loader.list_available_templates.assert_called_once()

    # --- validate_template ---

    def test_should_return_true_when_template_type_and_format_are_valid(self) -> None:
        service, _, mock_loader = self._make_service()
        mock_loader.validate_template.return_value = True

        assert service.validate_template("config", "yaml") is True

    def test_should_return_false_when_template_type_or_format_is_invalid(
        self,
    ) -> None:
        service, _, mock_loader = self._make_service()
        mock_loader.validate_template.return_value = False

        assert service.validate_template("unknown", "xyz") is False

    # --- generate_mockup_template ---

    def test_should_call_template_loader_when_generating_mockup(
        self, temp_dir: Path
    ) -> None:
        service, _, mock_loader = self._make_service()
        out = temp_dir / "mockup.yaml"

        service.generate_mockup_template("config", "yaml", out)

        mock_loader.generate_template_with_mockup.assert_called_once_with(
            "config", "yaml", out
        )

    def test_should_raise_template_error_when_mockup_loader_fails(
        self, temp_dir: Path
    ) -> None:
        from ezcompiler.shared.exceptions import TemplateError

        service, _, mock_loader = self._make_service()
        mock_loader.generate_template_with_mockup.side_effect = RuntimeError("boom")

        with pytest.raises(TemplateError):
            service.generate_mockup_template("config", "yaml", temp_dir / "out.yaml")

    # --- generate_raw_template ---

    def test_should_call_template_loader_when_generating_raw_template(
        self, temp_dir: Path
    ) -> None:
        service, _, mock_loader = self._make_service()
        out = temp_dir / "raw.yaml"

        service.generate_raw_template("config", "yaml", out)

        mock_loader.generate_raw_template.assert_called_once_with("config", "yaml", out)


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER SERVICE (compile / determine / interactive)
# ///////////////////////////////////////////////////////////////


class TestCompilerServiceCompile:
    """Test CompilerService compile orchestration with mocks."""

    def _build_config(self, temp_dir: Path) -> CompilerConfig:
        main_file = temp_dir / "main.py"
        main_file.write_text("print('ok')", encoding="utf-8")
        return CompilerConfig(
            version="1.0.0",
            project_name="CSTest",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=temp_dir / "dist",
        )

    # --- __init__ ---

    def test_should_raise_configuration_error_when_config_is_none(self) -> None:
        with pytest.raises(ConfigurationError):
            CompilerService(None)  # type: ignore[arg-type]

    # --- compiler_instance property ---

    def test_should_return_none_before_compilation(self, temp_dir: Path) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)
        assert service.compiler_instance is None

    # --- compile() happy path ---

    def test_should_return_compilation_result_when_compiler_succeeds(
        self, temp_dir: Path
    ) -> None:
        from ezcompiler.shared import CompilationResult

        config = self._build_config(temp_dir)
        service = CompilerService(config)
        mock_compiler = MagicMock()
        mock_compiler.zip_needed = True

        with patch(
            "ezcompiler.services.compiler_service.CompilerFactory.create_compiler",
            return_value=mock_compiler,
        ):
            result = service.compile(console=False, compiler="PyInstaller")

        assert isinstance(result, CompilationResult)
        assert result.zip_needed is True
        assert result.compiler_name == "PyInstaller"

    def test_should_set_compiler_instance_after_successful_compile(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)
        mock_compiler = MagicMock()
        mock_compiler.zip_needed = False

        with patch(
            "ezcompiler.services.compiler_service.CompilerFactory.create_compiler",
            return_value=mock_compiler,
        ):
            service.compile(console=True, compiler="Cx_Freeze")

        assert service.compiler_instance is mock_compiler

    # --- compile() — invalid compiler ---

    def test_should_raise_compilation_error_when_compiler_name_is_invalid(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with pytest.raises(CompilationError):
            service.compile(compiler="BadCompiler")  # type: ignore[arg-type]

    # --- compile() — unexpected exception wrapping ---

    def test_should_wrap_unexpected_exception_in_compilation_error(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with (
            patch(
                "ezcompiler.services.compiler_service.CompilerFactory.create_compiler",
                side_effect=RuntimeError("unexpected boom"),
            ),
            pytest.raises(CompilationError, match="unexpected boom"),
        ):
            service.compile(compiler="Cx_Freeze")

    # --- _determine_compiler ---

    def test_should_return_explicit_compiler_when_provided_and_not_auto(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)
        assert service._determine_compiler("PyInstaller") == "PyInstaller"

    def test_should_return_config_compiler_when_no_explicit_and_config_has_one(
        self, temp_dir: Path
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("x", encoding="utf-8")
        config = CompilerConfig(
            version="1.0.0",
            project_name="P",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=temp_dir / "dist",
            compiler="Nuitka",
        )
        service = CompilerService(config)
        assert service._determine_compiler(None) == "Nuitka"

    # --- _choose_compiler_interactively via argv ---

    def test_should_return_cx_freeze_when_argv_contains_cxf_flag(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with patch("sys.argv", ["prog", "-cxf"]):
            assert service._choose_compiler_interactively() == "Cx_Freeze"

    def test_should_return_pyinstaller_when_argv_contains_pyi_flag(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with patch("sys.argv", ["prog", "-pyi"]):
            assert service._choose_compiler_interactively() == "PyInstaller"

    def test_should_return_nuitka_when_argv_contains_nka_flag(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with patch("sys.argv", ["prog", "-nka"]):
            assert service._choose_compiler_interactively() == "Nuitka"

    def test_should_raise_compilation_error_when_prompt_fails(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with (
            patch("sys.argv", ["prog"]),
            patch(
                "ezcompiler.services.compiler_service.prompt",
                side_effect=RuntimeError("no TTY"),
            ),
            pytest.raises(CompilationError),
        ):
            service._choose_compiler_interactively()

    # --- zip_artifact ---

    def test_should_delegate_to_zip_utils_when_zip_artifact_called(
        self, temp_dir: Path
    ) -> None:
        config = self._build_config(temp_dir)
        service = CompilerService(config)

        with patch(
            "ezcompiler.services.compiler_service.ZipUtils.create_zip_archive"
        ) as mock_zip:
            service._zip_artifact(output_path=temp_dir / "out.zip")
            mock_zip.assert_called_once()
