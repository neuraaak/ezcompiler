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

from ezcompiler.core import (
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
        """Test that CompilationError is subclass of EzCompilerError."""
        assert issubclass(CompilationError, EzCompilerError)

    def test_configuration_error_is_subclass(self) -> None:
        """Test that ConfigurationError is subclass of EzCompilerError."""
        assert issubclass(ConfigurationError, EzCompilerError)

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
