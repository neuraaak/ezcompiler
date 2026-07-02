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
from ._compilation_result import CompilationResult
from ._compiler_config import COMPILER_SECTION_KEYS, CompilerConfig
from .exceptions import (
    CompilationError,
    ConfigurationError,
    EzCompilerError,
    ReleaseError,
    TemplateError,
    UpdaterConfigError,
    UpdaterError,
    UpdaterGenerationError,
    UploadError,
    VersionError,
)
from .exceptions.utils._file_exceptions import FileError

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
    "COMPILER_SECTION_KEYS",
    # Base exception
    "EzCompilerError",
    # Service exceptions
    "CompilationError",
    "ConfigurationError",
    "ReleaseError",
    "TemplateError",
    "UploadError",
    "VersionError",
    # File exceptions (backward compatibility alias)
    "FileOperationError",
    # Updater exceptions
    "UpdaterError",
    "UpdaterConfigError",
    "UpdaterGenerationError",
]
