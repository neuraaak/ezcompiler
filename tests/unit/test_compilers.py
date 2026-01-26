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
from ezcompiler.compilers import BaseCompiler, CxFreezeCompiler, PyInstallerCompiler

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
