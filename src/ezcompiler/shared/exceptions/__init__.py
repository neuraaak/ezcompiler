# ///////////////////////////////////////////////////////////////
# EXCEPTIONS PACKAGE - Specialized exception hierarchy
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Exceptions package - Specialized exceptions organized by module functionality.

This package provides fine-grained exceptions for different layers and utilities
of the EzCompiler project, enabling precise error handling.

Structure:
- services: Service layer exceptions (compiler, template, uploader services)
- utils: Utility layer exceptions
  - file_exceptions: File and directory operation errors
  - compiler_exceptions: Compiler operation errors
  - uploader_exceptions: Upload operation errors
  - validation_exceptions: Validation errors
  - zip_exceptions: ZIP archive errors
  - config_exceptions: Configuration errors
  - template_exceptions: Template processing errors
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS - Exception modules from services
# ///////////////////////////////////////////////////////////////
from . import services
from .services import (
    CompilationError,
    CompilerServiceError,
    ConfigurationError,
    TemplateError,
    TemplateServiceError,
    UploadError,
    UploaderServiceError,
    VersionError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - Exception modules from utils
# ///////////////////////////////////////////////////////////////
from .utils import (
    base,
    compiler_exceptions,
    config_exceptions,
    file_exceptions,
    template_exceptions,
    uploader_exceptions,
    validation_exceptions,
    zip_exceptions,
)

# ///////////////////////////////////////////////////////////////
# RE-EXPORTS - Base exception for backward compatibility
# ///////////////////////////////////////////////////////////////
from .utils.base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# PUBLIC API - Exception modules
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Exception modules
    "services",
    "base",
    "compiler_exceptions",
    "config_exceptions",
    "file_exceptions",
    "uploader_exceptions",
    "template_exceptions",
    "validation_exceptions",
    "zip_exceptions",
    # Base exception (re-exported for convenience)
    "EzCompilerError",
    # Service exceptions (re-exported for convenience)
    "CompilerServiceError",
    "CompilationError",
    "ConfigurationError",
    "TemplateServiceError",
    "TemplateError",
    "VersionError",
    "UploaderServiceError",
    "UploadError",
]
