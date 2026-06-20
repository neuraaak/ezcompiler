# ///////////////////////////////////////////////////////////////
# UPLOADER_EXCEPTIONS - Uploader operation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Uploader exceptions - Specialized exceptions for uploader operations.

This module defines exceptions for various uploader-related failures
used by UploaderUtils and uploader implementations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


# UploadError canonique : défini ici (sous-arbre utils), sous EzCompilerError.
# Le sous-arbre services le ré-importe (services/_service_exceptions.py) au lieu
# d'en redéfinir un — un seul `UploadError` partagé par tout le code.
class UploadError(EzCompilerError):
    """Base exception for upload operation errors (canonical)."""


class SourcePathError(UploadError):
    """Raised when source path for upload is invalid or inaccessible."""


class UploaderTypeError(UploadError):
    """Raised when upload type is not supported."""


class ServerConfigError(UploadError):
    """Raised when server configuration is invalid."""


class BackupGenerationError(UploadError):
    """Raised when backup path generation fails."""


class UploadConnectionError(UploadError):
    """Raised when connection to upload destination fails."""


class UploadAuthenticationError(UploadError):
    """Raised when authentication for upload fails."""


class UploadTimeoutError(UploadError):
    """Raised when upload operation times out."""
