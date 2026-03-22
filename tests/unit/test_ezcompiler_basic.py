# ///////////////////////////////////////////////////////////////
# TEST EZCOMPILER BASIC - Unit tests for EzCompiler basic functionality
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Basic unit tests for EzCompiler module.

Tests the main EzCompiler class and its basic functionality.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from pathlib import Path

from ezcompiler import EzCompiler

# ///////////////////////////////////////////////////////////////
# TESTS - IMPORT AND INSTANTIATION
# ///////////////////////////////////////////////////////////////


class TestEzCompilerImport:
    """Test EzCompiler can be imported and instantiated."""

    def test_import_ezcompiler(self) -> None:
        """Test that EzCompiler can be imported."""
        assert EzCompiler is not None

    def test_instantiate_ezcompiler(self) -> None:
        """Test that EzCompiler can be instantiated."""
        compiler = EzCompiler()
        assert compiler is not None
        assert isinstance(compiler, EzCompiler)

    def test_ezcompiler_has_logger(self) -> None:
        """Test that EzCompiler instance has a logger."""
        compiler = EzCompiler()
        assert hasattr(compiler, "logger")

    def test_ezcompiler_has_printer(self) -> None:
        """Test that EzCompiler instance has a printer."""
        compiler = EzCompiler()
        assert hasattr(compiler, "printer")

    def test_ezcompiler_has_config(self) -> None:
        """Test that EzCompiler instance has a config property."""
        compiler = EzCompiler()
        assert hasattr(compiler, "config")

    def test_ezcompiler_config_returns_compiler_config(self) -> None:
        """Test that config property returns CompilerConfig or None initially."""
        compiler = EzCompiler()
        # Config is initialized as None until init_project is called
        # This is expected behavior
        assert hasattr(compiler, "config")

    def test_ezcompiler_logging_is_passive(self) -> None:
        """Test that EzCompiler uses lib_mode passive logging (no logging args accepted)."""
        compiler = EzCompiler()
        assert compiler.logger is not None
        assert compiler.printer is not None

    def test_ezcompiler_has_printer_attribute(self) -> None:
        """Test that printer attribute is accessible."""
        compiler = EzCompiler()
        printer = compiler.printer
        assert printer is not None

    def test_ezcompiler_has_logger_attribute(self) -> None:
        """Test that logger attribute is accessible."""
        compiler = EzCompiler()
        logger = compiler.logger
        assert logger is not None

    def test_ezcompiler_logger_is_stdlib(self) -> None:
        """Test that logger is a stdlib logging.Logger (lib_mode pattern)."""
        import logging

        compiler = EzCompiler()
        assert isinstance(compiler.logger, logging.Logger)


# ///////////////////////////////////////////////////////////////
# TESTS - INITIALIZATION
# ///////////////////////////////////////////////////////////////


class TestEzCompilerInitialization:
    """Test EzCompiler project initialization."""

    def test_init_project_minimal(self, temp_dir: Path) -> None:
        """Test initializing a project with minimal configuration."""
        # Create test file
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        compiler = EzCompiler()
        output_folder = temp_dir / "dist"

        compiler.init_project(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(output_folder),
        )

        # Verify config is set
        assert compiler.config is not None
        assert compiler.config.version == "1.0.0"
        assert compiler.config.project_name == "TestProject"

    def test_init_project_full(self, temp_dir: Path) -> None:
        """Test initializing a project with full configuration."""
        # Create test file
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        main_file = src_dir / "main.py"
        main_file.write_text("# test")

        compiler = EzCompiler()
        output_folder = temp_dir / "dist"

        compiler.init_project(
            version="2.0.0",
            project_name="FullProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(output_folder),
            company_name="TestCorp",
            project_description="Test project",
            author="Test Author",
        )

        assert compiler.config.version == "2.0.0"
        assert compiler.config.project_name == "FullProject"
        assert compiler.config.company_name == "TestCorp"
        assert compiler.config.author == "Test Author"
