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
    ReleaseError,
    TemplateError,
    TemplateServiceError,
    UpdaterError,
    UploadError,
    UploaderServiceError,
    VersionError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - Exception modules from utils
# ///////////////////////////////////////////////////////////////
from .utils import (
    _base,
    _compiler_exceptions,
    _config_exceptions,
    _file_exceptions,
    _template_exceptions,
    _uploader_exceptions,
    _validation_exceptions,
    _zip_exceptions,
)

# ///////////////////////////////////////////////////////////////
# RE-EXPORTS - Base exception for backward compatibility
# ///////////////////////////////////////////////////////////////
from .utils._base import EzCompilerError
from .utils._config_exceptions import ConfigError
from .utils._release_exceptions import (
    BundleBuildError,
    ReleaseConfigError,
    ReleaserTypeError,
    SigningKeyError,
)
from .utils._updater_exceptions import (
    UpdaterConfigError,
    UpdaterGenerationError,
)
from .utils._zip_exceptions import ZipError

# ///////////////////////////////////////////////////////////////
# PUBLIC API - Exception modules
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Exception modules
    "services",
    "_base",
    "_compiler_exceptions",
    "_config_exceptions",
    "_file_exceptions",
    "_uploader_exceptions",
    "_template_exceptions",
    "_validation_exceptions",
    "_zip_exceptions",
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
    # Release exceptions
    "ReleaseError",
    "ReleaserTypeError",
    "BundleBuildError",
    "SigningKeyError",
    "ReleaseConfigError",
    # Updater exceptions
    "UpdaterError",
    "UpdaterConfigError",
    "UpdaterGenerationError",
    # Util exceptions promoted for interface layer use
    "ConfigError",
    "ZipError",
]
