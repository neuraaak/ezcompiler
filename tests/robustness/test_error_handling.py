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

pytestmark = pytest.mark.robustness

# ///////////////////////////////////////////////////////////////
# TESTS - ERROR HANDLING
# ///////////////////////////////////////////////////////////////


class TestErrorHandling:
    """Test error handling and exception raising."""

    def test_should_raise_with_message_when_ezcompiler_error_is_triggered(self) -> None:
        """Test EzCompilerError raises with custom message."""
        error_msg = "Custom error message"
        with pytest.raises(EzCompilerError, match=error_msg):
            raise EzCompilerError(error_msg)

    def test_should_raise_with_message_when_compilation_error_is_triggered(
        self,
    ) -> None:
        """Test CompilationError raises with custom message."""
        error_msg = "Compilation failed"
        with pytest.raises(CompilationError, match=error_msg):
            raise CompilationError(error_msg)

    def test_should_raise_with_message_when_configuration_error_is_triggered(
        self,
    ) -> None:
        """Test ConfigurationError raises with custom message."""
        error_msg = "Invalid configuration"
        with pytest.raises(ConfigurationError, match=error_msg):
            raise ConfigurationError(error_msg)

    def test_should_be_catchable_when_compilation_error_is_raised(self) -> None:
        """Test that CompilationError can be caught specifically."""
        with pytest.raises(CompilationError):
            raise CompilationError("Test error")

    def test_should_be_catchable_when_configuration_error_is_raised(self) -> None:
        """Test that ConfigurationError can be caught specifically."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test error")
