# ///////////////////////////////////////////////////////////////
# TEST CORE - Unit tests for core module
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Unit tests for core modules (configuration, exceptions).

Tests the basic functionality of core classes.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import pytest

from ezcompiler.shared import (
    CompilationError,
    CompilerConfig,
    ConfigurationError,
    EzCompilerError,
)
from ezcompiler.shared.exceptions import CompilerServiceError

# ///////////////////////////////////////////////////////////////
# TESTS - EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class TestExceptions:
    """Test exception classes."""

    def test_should_be_importable_when_ezcompiler_error_is_loaded(self) -> None:
        """Test that EzCompilerError can be imported."""
        assert EzCompilerError is not None

    def test_should_be_subclass_of_compiler_service_error_when_compilation_error_is_raised(
        self,
    ) -> None:
        """Test that CompilationError is subclass of CompilerServiceError."""
        assert issubclass(CompilationError, CompilerServiceError)

    def test_should_be_subclass_of_compiler_service_error_when_configuration_error_is_raised(
        self,
    ) -> None:
        """Test that ConfigurationError is subclass of CompilerServiceError."""
        assert issubclass(ConfigurationError, CompilerServiceError)

    def test_should_raise_when_ezcompiler_error_is_triggered(self) -> None:
        """Test that EzCompilerError can be raised."""
        with pytest.raises(EzCompilerError):
            raise EzCompilerError("Test error")


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER CONFIG
# ///////////////////////////////////////////////////////////////


class TestCompilerConfig:
    """Test CompilerConfig class."""

    def test_should_be_importable_when_compiler_config_is_loaded(self) -> None:
        """Test that CompilerConfig can be imported."""
        assert CompilerConfig is not None

    def test_should_create_config_when_minimal_fields_are_provided(
        self, temp_dir
    ) -> None:
        """Test creating CompilerConfig with minimal required fields."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        assert config is not None
        assert config.version == "1.0.0"
        assert config.project_name == "TestProject"
        assert config.main_file == str(main_file)
        assert str(config.output_folder) == str(temp_dir / "dist")

    def test_should_create_config_when_all_fields_are_provided(self, temp_dir) -> None:
        """Test creating CompilerConfig with all fields."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="2.0.0",
            project_name="FullTestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
            project_description="A test project",
            company_name="TestCorp",
            author="Test Author",
            packages=["requests", "pandas"],
            includes=["encodings"],
            excludes=["debugpy", "test"],
            console=False,
            compiler="PyInstaller",
            optimize=True,
            strip=False,
            debug=False,
            repo_destination="disk",
        )
        assert config.version == "2.0.0"
        assert config.project_name == "FullTestProject"
        assert config.company_name == "TestCorp"
        assert config.author == "Test Author"
        assert config.console is False
        assert config.compiler == "PyInstaller"

    def test_should_return_dict_when_to_dict_is_called(self, temp_dir) -> None:
        """Test converting CompilerConfig to dictionary."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.5.0",
            project_name="DictTestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["version"] == "1.5.0"
        assert config_dict["project_name"] == "DictTestProject"

    def test_should_create_config_when_from_dict_is_called(self, temp_dir) -> None:
        """Test creating CompilerConfig from dictionary."""
        app_file = temp_dir / "app.py"
        app_file.write_text("# test")

        config_dict = {
            "version": "1.2.3",
            "project_name": "FromDictProject",
            "main_file": str(app_file),
            "include_files": {"files": [], "folders": []},
            "output_folder": str(temp_dir / "output"),
        }
        config = CompilerConfig.from_dict(config_dict)
        assert config.version == "1.2.3"
        assert config.project_name == "FromDictProject"
        assert config.main_file == str(app_file)

    def test_should_use_defaults_when_optional_fields_are_omitted(
        self, temp_dir
    ) -> None:
        """Test that CompilerConfig has proper defaults."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="DefaultTest",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        assert config.console is True
        assert config.compiler == "auto"
        assert config.optimize is True
        assert config.strip is False
        assert config.debug is False
        assert config.tuf_enabled is False
        assert config.repo_destination == "disk"
        assert config.release_destination == "disk"

    def test_should_raise_configuration_error_when_include_files_contains_empty_string(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        with pytest.raises(ConfigurationError):
            CompilerConfig(
                version="1.0.0",
                project_name="P",
                main_file=str(main_file),
                include_files={"files": [""], "folders": []},
                output_folder=str(temp_dir / "dist"),
            )

    def test_should_raise_configuration_error_when_include_folders_contains_empty_string(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        with pytest.raises(ConfigurationError):
            CompilerConfig(
                version="1.0.0",
                project_name="P",
                main_file=str(main_file),
                include_files={"files": [], "folders": [""]},
                output_folder=str(temp_dir / "dist"),
            )

    def test_should_raise_configuration_error_when_compiler_is_unknown(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        with pytest.raises(ConfigurationError):
            CompilerConfig(
                version="1.0.0",
                project_name="P",
                main_file=str(main_file),
                include_files={"files": [], "folders": []},
                output_folder=str(temp_dir / "dist"),
                compiler="NotACompiler",
            )

    def test_should_serialize_output_folder_as_string_in_to_dict(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")
        config = CompilerConfig(
            version="1.0.0",
            project_name="P",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )

        d = config.to_dict()

        assert isinstance(d["output_folder"], str)

    def test_should_return_nested_sections_in_to_dict(self, temp_dir) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")
        config = CompilerConfig(
            version="1.0.0",
            project_name="P",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )

        d = config.to_dict()

        assert "compilation" in d
        assert "upload" in d
        assert "advanced" in d
        assert "console" in d["compilation"]
        assert "repo_destination" in d["upload"]
        assert "release_destination" in d["upload"]

    def test_should_raise_when_legacy_structure_key_in_from_dict(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        with pytest.raises(ConfigurationError, match="upload_structure"):
            CompilerConfig.from_dict(
                {
                    "version": "1.0.0",
                    "project_name": "P",
                    "main_file": str(main_file),
                    "include_files": {"files": [], "folders": []},
                    "output_folder": str(temp_dir / "dist"),
                    "upload": {
                        "structure": "server",
                        "repo_path": "rel",
                        "server_url": "",
                    },
                }
            )

    def test_should_handle_version_file_backward_compatibility_in_from_dict(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig.from_dict(
            {
                "version": "1.0.0",
                "project_name": "P",
                "main_file": str(main_file),
                "include_files": {"files": [], "folders": []},
                "output_folder": str(temp_dir / "dist"),
                "version_file": "custom_ver.txt",
            }
        )

        assert config.version_filename == "custom_ver.txt"

    def test_should_return_version_file_path_combining_output_folder(
        self, temp_dir
    ) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")
        config = CompilerConfig(
            version="1.0.0",
            project_name="P",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
            version_filename="ver.txt",
        )

        assert config.version_file == config.output_folder / "ver.txt"

    def test_should_return_zip_file_path_next_to_output_folder(self, temp_dir) -> None:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")
        config = CompilerConfig(
            version="1.0.0",
            project_name="MyApp",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )

        assert config.zip_file_path == temp_dir / "MyApp.zip"
