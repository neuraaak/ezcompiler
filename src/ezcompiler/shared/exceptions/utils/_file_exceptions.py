# ///////////////////////////////////////////////////////////////
# FILE_EXCEPTIONS - File operation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
File exceptions - Specialized exceptions for file operations.

This module defines exceptions for various file operation failures
used by FileUtils and other file-related utilities.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class FileError(EzCompilerError):
    """Base exception for file operation errors."""


class FileNotFoundError(FileError):
    """Raised when a file or directory cannot be found."""


class DirectoryCreationError(FileError):
    """Raised when directory creation fails."""


class FileAccessError(FileError):
    """Raised when file access is denied or fails."""


class FileCopyError(FileError):
    """Raised when file copy operation fails."""


class FileMoveError(FileError):
    """Raised when file move operation fails."""


class FileDeleteError(FileError):
    """Raised when file deletion fails."""


class DirectoryListError(FileError):
    """Raised when directory listing fails."""


class PathNormalizationError(FileError):
    """Raised when path normalization fails."""
