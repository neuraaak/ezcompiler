# ///////////////////////////////////////////////////////////////
# PATH_VALIDATORS - Path validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Path validators - Validation utilities for file and directory paths.

This module provides validation functions for validating file and directory
paths, checking for valid characters and structure.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_file_path(path: str | Path) -> bool:
    """
    Validate a file path.

    Args:
        path: File path to validate

    Returns:
        bool: True if path format is valid, False otherwise

    Note:
        Checks for valid characters and structure, not existence.

    Example:
        >>> validate_file_path("path/to/file.txt")
        True
        >>> validate_file_path("invalid<path>")
        False
    """
    try:
        path_obj = Path(path)
        # Check if path has valid characters and structure
        path_str = str(path_obj)
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
        return len(path_str) > 0 and not any(char in path_str for char in invalid_chars)
    except Exception:
        return False


def validate_directory_path(path: str | Path) -> bool:
    """
    Validate a directory path.

    Args:
        path: Directory path to validate

    Returns:
        bool: True if path format is valid, False otherwise

    Note:
        Uses same validation as file path validation.

    Example:
        >>> validate_directory_path("path/to/directory")
        True
        >>> validate_directory_path("invalid<path>")
        False
    """
    return validate_file_path(path)
