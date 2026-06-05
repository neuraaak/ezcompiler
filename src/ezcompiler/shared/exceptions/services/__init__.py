# ///////////////////////////////////////////////////////////////
# SERVICES - Service layer exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Services exceptions module - Exceptions for the business logic layer.

This module provides exceptions for the service layer, with limited granularity
to avoid exception overload. Each service has a base exception and specific
error scenarios.
"""

from __future__ import annotations

from ..utils._uploader_exceptions import UploadError

# ///////////////////////////////////////////////////////////////
# IMPORTS - Service exceptions
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerServiceError
from ._service_exceptions import (
    CompilationError,
    CompilerServiceError,
    ConfigurationError,
    TemplateError,
    TemplateServiceError,
    UploaderServiceError,
    VersionError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "EzCompilerServiceError",
    # Compiler service exceptions
    "CompilerServiceError",
    "CompilationError",
    "ConfigurationError",
    # Template service exceptions
    "TemplateServiceError",
    "TemplateError",
    "VersionError",
    # Uploader service exceptions
    "UploaderServiceError",
    "UploadError",
]
