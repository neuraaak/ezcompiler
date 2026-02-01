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

# ///////////////////////////////////////////////////////////////
# TESTS - EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class TestExceptions:
    """Test exception classes."""

    def test_ezcompiler_error_exists(self) -> None:
        """Test that EzCompilerError can be imported."""
        assert EzCompilerError is not None

    def test_compilation_error_is_subclass(self) -> None:
        """Test that CompilationError is subclass of Exception."""
        # CompilationError inherits from CompilerServiceError, not EzCompilerError
        assert issubclass(CompilationError, Exception)

    def test_configuration_error_is_subclass(self) -> None:
        """Test that ConfigurationError is subclass of Exception."""
        # ConfigurationError inherits from CompilerServiceError, not EzCompilerError
        assert issubclass(ConfigurationError, Exception)

    def test_raise_ezcompiler_error(self) -> None:
        """Test that EzCompilerError can be raised."""
        with pytest.raises(EzCompilerError):
            raise EzCompilerError("Test error")


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER CONFIG
# ///////////////////////////////////////////////////////////////


class TestCompilerConfig:
    """Test CompilerConfig class."""

    def test_compiler_config_import(self) -> None:
        """Test that CompilerConfig can be imported."""
        assert CompilerConfig is not None

    def test_compiler_config_creation_minimal(self, temp_dir) -> None:
        """Test creating CompilerConfig with minimal required fields."""
        # Create test file
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

    def test_compiler_config_creation_full(self, temp_dir) -> None:
        """Test creating CompilerConfig with all fields."""
        # Create test files to pass validation
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
            zip_needed=True,
            repo_needed=False,
            upload_structure="disk",
            repo_path="releases",
        )
        assert config.version == "2.0.0"
        assert config.project_name == "FullTestProject"
        assert config.company_name == "TestCorp"
        assert config.author == "Test Author"
        assert config.console is False
        assert config.compiler == "PyInstaller"

    def test_compiler_config_to_dict(self, temp_dir) -> None:
        """Test converting CompilerConfig to dictionary."""
        # Create test file
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

    def test_compiler_config_from_dict(self, temp_dir) -> None:
        """Test creating CompilerConfig from dictionary."""
        # Create test file
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

    def test_compiler_config_defaults(self, temp_dir) -> None:
        """Test that CompilerConfig has proper defaults."""
        # Create test file
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
        assert config.zip_needed is True
        assert config.repo_needed is False
        assert config.upload_structure == "disk"
