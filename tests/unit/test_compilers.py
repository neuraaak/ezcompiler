# ///////////////////////////////////////////////////////////////
# TEST COMPILERS - Unit tests for compiler modules
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Unit tests for compiler modules.

Tests the basic functionality of compiler implementations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ezcompiler.protocols import (
    BaseCompiler,
    CxFreezeCompiler,
    NuitkaCompiler,
    PyInstallerCompiler,
)
from ezcompiler.shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER IMPORTS
# ///////////////////////////////////////////////////////////////


class TestCompilerImports:
    """Test compiler classes can be imported."""

    def test_base_compiler_import(self) -> None:
        """Test that BaseCompiler can be imported."""
        assert BaseCompiler is not None

    def test_cx_freeze_compiler_import(self) -> None:
        """Test that CxFreezeCompiler can be imported."""
        assert CxFreezeCompiler is not None

    def test_pyinstaller_compiler_import(self) -> None:
        """Test that PyInstallerCompiler can be imported."""
        assert PyInstallerCompiler is not None

    def test_nuitka_compiler_import(self) -> None:
        """Test that NuitkaCompiler can be imported."""
        assert NuitkaCompiler is not None


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER INSTANTIATION
# ///////////////////////////////////////////////////////////////


class TestCompilerInstantiation:
    """Test compiler classes can be instantiated."""

    def test_instantiate_cx_freeze_compiler(self, temp_dir) -> None:
        """Test that CxFreezeCompiler can be instantiated."""
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
        compiler = CxFreezeCompiler(config)
        assert compiler is not None
        assert isinstance(compiler, CxFreezeCompiler)

    def test_instantiate_pyinstaller_compiler(self, temp_dir) -> None:
        """Test that PyInstallerCompiler can be instantiated."""
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
        compiler = PyInstallerCompiler(config)
        assert compiler is not None
        assert isinstance(compiler, PyInstallerCompiler)

    def test_instantiate_nuitka_compiler(self, temp_dir) -> None:
        """Test that NuitkaCompiler can be instantiated."""
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
        compiler = NuitkaCompiler(config)
        assert compiler is not None
        assert isinstance(compiler, NuitkaCompiler)

    def test_cx_freeze_compiler_has_config(self, temp_dir) -> None:
        """Test that CxFreezeCompiler stores config."""
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
        compiler = CxFreezeCompiler(config)
        assert hasattr(compiler, "config")
        assert compiler.config == config

    def test_compiler_is_base_compiler_instance(self, temp_dir) -> None:
        """Test that all compilers are instances of BaseCompiler."""
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
        cx_compiler = CxFreezeCompiler(config)
        pyi_compiler = PyInstallerCompiler(config)
        nui_compiler = NuitkaCompiler(config)

        assert isinstance(cx_compiler, BaseCompiler)
        assert isinstance(pyi_compiler, BaseCompiler)
        assert isinstance(nui_compiler, BaseCompiler)


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER NAMES
# ///////////////////////////////////////////////////////////////


class TestCompilerNames:
    """Test that compilers return correct names."""

    def test_cx_freeze_compiler_name(self, temp_dir) -> None:
        """Test that CxFreezeCompiler returns correct name."""
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
        compiler = CxFreezeCompiler(config)
        name = compiler.get_compiler_name()
        assert name is not None
        assert isinstance(name, str)
        assert "freeze" in name.lower() or "cx" in name.lower()

    def test_pyinstaller_compiler_name(self, temp_dir) -> None:
        """Test that PyInstallerCompiler returns correct name."""
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
        compiler = PyInstallerCompiler(config)
        name = compiler.get_compiler_name()
        assert name is not None
        assert isinstance(name, str)
        assert "pyinstaller" in name.lower()

    def test_nuitka_compiler_name(self, temp_dir) -> None:
        """Test that NuitkaCompiler returns correct name."""
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
        compiler = NuitkaCompiler(config)
        name = compiler.get_compiler_name()
        assert name is not None
        assert isinstance(name, str)
        assert "nuitka" in name.lower()
