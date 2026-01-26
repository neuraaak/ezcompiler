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
