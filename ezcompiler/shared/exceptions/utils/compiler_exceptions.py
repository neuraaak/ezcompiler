# ///////////////////////////////////////////////////////////////
# COMPILER_EXCEPTIONS - Compiler operation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Compiler exceptions - Specialized exceptions for compiler operations.

This module defines exceptions for various compiler-related failures
used by CompilerUtils and compiler implementations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from .base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CompilerError(EzCompilerError):
    """Base exception for compiler operation errors."""


class CompilerConfigValidationError(CompilerError):
    """Raised when compiler configuration validation fails."""


class MainFileNotFoundError(CompilerError):
    """Raised when the main file for compilation is not found."""


class OutputDirectoryError(CompilerError):
    """Raised when output directory creation or access fails."""


class IncludeFilesFormatError(CompilerError):
    """Raised when include files formatting fails."""


class CompilerNotAvailableError(CompilerError):
    """Raised when the compiler is not available on the system."""


class CompilationExecutionError(CompilerError):
    """Raised when the actual compilation execution fails."""
