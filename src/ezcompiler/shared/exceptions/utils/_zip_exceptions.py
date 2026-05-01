# ///////////////////////////////////////////////////////////////
# ZIP_EXCEPTIONS - ZIP archive exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
ZIP exceptions - Specialized exceptions for ZIP archive operations.

This module defines exceptions for various ZIP-related failures
used by ZipUtils and archive operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ZipError(EzCompilerError):
    """Base exception for ZIP operation errors."""


class ZipCreationError(ZipError):
    """Raised when ZIP archive creation fails."""


class ZipExtractionError(ZipError):
    """Raised when ZIP archive extraction fails."""


class ZipFileNotFoundError(ZipError):
    """Raised when ZIP file does not exist."""


class ZipFileCorruptedError(ZipError):
    """Raised when ZIP file is corrupted or cannot be opened."""


class ZipPathError(ZipError):
    """Raised when source path for zipping is invalid."""


class ZipProgressError(ZipError):
    """Raised when ZIP operation progress tracking fails."""


class ZipCompressionError(ZipError):
    """Raised when ZIP compression fails."""
