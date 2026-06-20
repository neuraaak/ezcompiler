# ///////////////////////////////////////////////////////////////
# SERVICE_EXCEPTIONS - Service layer exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Service exceptions - Specialized exceptions for service layer operations.

This module defines exceptions for the business logic layer (services).
Each service has a base exception with specific error scenarios.
Granularity is limited to essential error categories to avoid exception overload.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ..utils._uploader_exceptions import UploadError
from ._base import EzCompilerServiceError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - COMPILER SERVICE
# ///////////////////////////////////////////////////////////////


class CompilerServiceError(EzCompilerServiceError):
    """Base exception for compiler service operations."""


class CompilationError(CompilerServiceError):
    """Raised when project compilation fails."""


class ConfigurationError(CompilerServiceError):
    """Raised when configuration is invalid or missing."""


# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - TEMPLATE SERVICE
# ///////////////////////////////////////////////////////////////


class TemplateServiceError(EzCompilerServiceError):
    """Base exception for template service operations."""


class TemplateError(TemplateServiceError):
    """Raised when template processing or file generation fails."""


class VersionError(TemplateServiceError):
    """Raised when version file generation fails."""


# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - UPLOADER SERVICE
# ///////////////////////////////////////////////////////////////


class UploaderServiceError(EzCompilerServiceError):
    """Base exception for uploader service operations.

    Conservé pour compatibilité ; `UploadError` est désormais l'unique classe
    canonique importée depuis utils/_uploader_exceptions.py (sous EzCompilerError).
    """


# UploadError est ré-exporté ici (importé ci-dessus) pour préserver l'API publique
# `from ..shared.exceptions import UploadError` sans dupliquer la classe.
__all__ = [
    "CompilerServiceError",
    "CompilationError",
    "ConfigurationError",
    "TemplateServiceError",
    "TemplateError",
    "VersionError",
    "UploaderServiceError",
    "UploadError",
]
