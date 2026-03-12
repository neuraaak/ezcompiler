# ///////////////////////////////////////////////////////////////
# SHARED - Shared configuration and exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Shared module - Shared configuration and exceptions for EzCompiler.

This module provides access to shared components used across all layers:
- CompilerConfig: Project configuration dataclass
- Exceptions: Service and utility exception hierarchy
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .compilation_result import CompilationResult
from .compiler_config import CompilerConfig
from .exceptions import (
    CompilationError,
    ConfigurationError,
    EzCompilerError,
    TemplateError,
    UploadError,
    VersionError,
)
from .exceptions.utils.file_exceptions import FileError

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

# Backward compatibility alias
FileOperationError = FileError

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Configuration
    # Result types
    "CompilationResult",
    # Configuration
    "CompilerConfig",
    # Base exception
    "EzCompilerError",
    # Service exceptions
    "CompilationError",
    "ConfigurationError",
    "TemplateError",
    "UploadError",
    "VersionError",
    # File exceptions (backward compatibility alias)
    "FileOperationError",
]
