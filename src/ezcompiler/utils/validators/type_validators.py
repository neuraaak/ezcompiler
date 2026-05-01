# ///////////////////////////////////////////////////////////////
# TYPE_VALIDATORS - Type validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Type validators - Validation utilities for type checking.

This module provides validation functions for checking data types and
validating integer values.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Local imports
from ...shared.exceptions.utils import TypeValidationError

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_positive_integer(value: Any) -> bool:
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate

    Returns:
        bool: True if value is a positive integer, False otherwise

    Example:
        >>> validate_positive_integer(5)
        True
        >>> validate_positive_integer(0)
        False
        >>> validate_positive_integer(-1)
        False
    """
    return isinstance(value, int) and value > 0


def validate_non_negative_integer(value: Any) -> bool:
    """
    Validate that a value is a non-negative integer.

    Args:
        value: Value to validate

    Returns:
        bool: True if value is a non-negative integer, False otherwise

    Example:
        >>> validate_non_negative_integer(0)
        True
        >>> validate_non_negative_integer(5)
        True
        >>> validate_non_negative_integer(-1)
        False
    """
    return isinstance(value, int) and value >= 0


def validate_boolean(value: Any) -> bool:
    """
    Validate that a value is a boolean.

    Args:
        value: Value to validate

    Returns:
        bool: True if value is a boolean, False otherwise

    Example:
        >>> validate_boolean(True)
        True
        >>> validate_boolean(False)
        True
        >>> validate_boolean(1)
        False
    """
    return isinstance(value, bool)


def validate_type(
    value: Any, expected_type: type | tuple[type, ...], field_name: str = "Value"
) -> None:
    """
    Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type or tuple of types
        field_name: Name of field for error messages

    Raises:
        TypeValidationError: If value is not of expected type

    Example:
        >>> validate_type("hello", str)
        >>> validate_type(42, int)
        >>> validate_type("hello", int)
        Traceback (most recent call last):
            ...
        TypeValidationError: Value must be of type int, got str
    """
    if not isinstance(value, expected_type):
        if isinstance(expected_type, tuple):
            type_names = " or ".join(t.__name__ for t in expected_type)
        else:
            type_names = expected_type.__name__
        raise TypeValidationError(
            f"{field_name} must be of type {type_names}, got {type(value).__name__}"
        )
