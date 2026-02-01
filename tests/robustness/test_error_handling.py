# ///////////////////////////////////////////////////////////////
# TEST ERROR HANDLING - Robustness tests for error handling
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Robustness tests for error handling.

Tests that exceptions are properly raised and handled in various scenarios.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import pytest

from ezcompiler.shared import (
    CompilationError,
    ConfigurationError,
    EzCompilerError,
)

# ///////////////////////////////////////////////////////////////
# TESTS - ERROR HANDLING
# ///////////////////////////////////////////////////////////////


class TestErrorHandling:
    """Test error handling and exception raising."""

    def test_ezcompiler_error_with_message(self) -> None:
        """Test EzCompilerError raises with custom message."""
        error_msg = "Custom error message"
        with pytest.raises(EzCompilerError, match=error_msg):
            raise EzCompilerError(error_msg)

    def test_compilation_error_with_message(self) -> None:
        """Test CompilationError raises with custom message."""
        error_msg = "Compilation failed"
        with pytest.raises(CompilationError, match=error_msg):
            raise CompilationError(error_msg)

    def test_configuration_error_with_message(self) -> None:
        """Test ConfigurationError raises with custom message."""
        error_msg = "Invalid configuration"
        with pytest.raises(ConfigurationError, match=error_msg):
            raise ConfigurationError(error_msg)

    def test_catch_compilation_error_as_base(self) -> None:
        """Test that CompilationError can be caught specifically."""
        with pytest.raises(CompilationError):
            raise CompilationError("Test error")

    def test_catch_configuration_error_as_base(self) -> None:
        """Test that ConfigurationError can be caught specifically."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test error")
