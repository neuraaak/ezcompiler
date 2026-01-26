# ///////////////////////////////////////////////////////////////
# CORE - Core configuration and exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Core module - Configuration and exception definitions for EzCompiler.

This module provides the core configuration class and custom exception
hierarchy for the EzCompiler project.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .compiler_config import CompilerConfig
from .exceptions import (
    CompilationError,
    ConfigurationError,
    EzCompilerError,
    FileOperationError,
    TemplateError,
    UploadError,
    VersionError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "CompilerConfig",
    "EzCompilerError",
    "CompilationError",
    "ConfigurationError",
    "TemplateError",
    "UploadError",
    "VersionError",
    "FileOperationError",
]
