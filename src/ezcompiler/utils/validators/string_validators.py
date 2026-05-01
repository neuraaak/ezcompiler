# ///////////////////////////////////////////////////////////////
# STRING_VALIDATORS - String validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
String validators - Validation utilities for string manipulation and validation.

This module provides validation functions for sanitizing filenames and
validating string patterns.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re

# Local imports
from ...shared.exceptions.utils import PatternValidationError

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename with invalid characters removed

    Note:
        Returns "unnamed_file" if filename becomes empty after sanitization.

    Example:
        >>> sanitize_filename("my_file.txt")
        'my_file.txt'
        >>> sanitize_filename("invalid<>file.txt")
        'invalid__file.txt'
        >>> sanitize_filename(">>>")
        'unnamed_file'
    """
    if not isinstance(filename, str):
        return ""

    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"

    return sanitized


def validate_pattern(
    value: str,
    pattern: str,
    field_name: str = "Value",
    error_msg: str | None = None,
) -> None:
    r"""
    Validate that a string matches a regex pattern.

    Args:
        value: String to validate
        pattern: Regex pattern to match
        field_name: Name of field for error messages
        error_msg: Custom error message

    Raises:
        TypeError: If value is not a string
        PatternValidationError: If value doesn't match pattern

    Example:
        >>> validate_pattern("hello123", r"^[a-z]+\d+$")
        >>> validate_pattern("hello", r"^\d+$")
        Traceback (most recent call last):
            ...
        PatternValidationError: Value does not match required pattern
    """
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    if not re.match(pattern, value):
        msg = error_msg or f"{field_name} does not match required pattern"
        raise PatternValidationError(msg)
