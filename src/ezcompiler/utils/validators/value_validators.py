# ///////////////////////////////////////////////////////////////
# VALUE_VALIDATORS - Value validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Value validators - Validation utilities for value ranges and constraints.

This module provides validation functions for checking string lengths,
numeric ranges, list lengths, choices, and other value constraints.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Local imports
from ...shared.exceptions.utils.validation_exceptions import (
    ChoiceValidationError,
    LengthValidationError,
    RangeValidationError,
    RequiredFieldError,
)

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_string_length(
    value: str, min_length: int = 0, max_length: int | None = None
) -> bool:
    """
    Validate string length.

    Args:
        value: String to validate
        min_length: Minimum allowed length (default: 0)
        max_length: Maximum allowed length, None for no limit (default: None)

    Returns:
        bool: True if string length is valid, False otherwise

    Example:
        >>> validate_string_length("hello", min_length=3)
        True
        >>> validate_string_length("hi", min_length=3)
        False
        >>> validate_string_length("toolong", max_length=5)
        False
    """
    if not isinstance(value, str):
        return False

    if len(value) < min_length:
        return False

    return not (max_length is not None and len(value) > max_length)


def validate_numeric_range(
    value: int | float,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
) -> bool:
    """
    Validate numeric value range.

    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value, None for no limit (default: None)
        max_value: Maximum allowed value, None for no limit (default: None)

    Returns:
        bool: True if value is within range, False otherwise

    Example:
        >>> validate_numeric_range(5, min_value=0, max_value=10)
        True
        >>> validate_numeric_range(-1, min_value=0)
        False
        >>> validate_numeric_range(15, max_value=10)
        False
    """
    if not isinstance(value, (int, float)):
        return False

    if min_value is not None and value < min_value:
        return False

    return not (max_value is not None and value > max_value)


def validate_list_length(
    value: list[Any], min_length: int = 0, max_length: int | None = None
) -> bool:
    """
    Validate list length.

    Args:
        value: List to validate
        min_length: Minimum allowed length (default: 0)
        max_length: Maximum allowed length, None for no limit (default: None)

    Returns:
        bool: True if list length is valid, False otherwise

    Example:
        >>> validate_list_length([1, 2, 3], min_length=2)
        True
        >>> validate_list_length([1], min_length=2)
        False
        >>> validate_list_length([1, 2, 3, 4], max_length=3)
        False
    """
    if not isinstance(value, list):
        return False

    if len(value) < min_length:
        return False

    return not (max_length is not None and len(value) > max_length)


def validate_choice(value: Any, valid_choices: list[Any]) -> bool:
    """
    Validate that a value is one of the valid choices.

    Args:
        value: Value to validate
        valid_choices: List of valid choices

    Returns:
        bool: True if value is a valid choice, False otherwise

    Example:
        >>> validate_choice("red", ["red", "green", "blue"])
        True
        >>> validate_choice("yellow", ["red", "green", "blue"])
        False
    """
    return value in valid_choices


def validate_not_empty(value: Any, field_name: str = "Value") -> None:
    """
    Validate that a value is not empty (string, list, dict, etc.).

    Args:
        value: Value to validate
        field_name: Name of field for error messages

    Raises:
        RequiredFieldError: If value is empty

    Example:
        >>> validate_not_empty("hello")
        >>> validate_not_empty([1, 2, 3])
        >>> validate_not_empty("")
        Traceback (most recent call last):
            ...
        RequiredFieldError: Value cannot be empty
    """
    if not value:
        raise RequiredFieldError(f"{field_name} cannot be empty")


def validate_one_of(
    value: Any, valid_values: list[Any], field_name: str = "Value"
) -> None:
    """
    Validate that a value is one of the valid options.

    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of field for error messages

    Raises:
        ChoiceValidationError: If value is not in valid values

    Example:
        >>> validate_one_of("red", ["red", "green", "blue"])
        >>> validate_one_of("yellow", ["red", "green", "blue"])
        Traceback (most recent call last):
            ...
        ChoiceValidationError: Value must be one of: red, green, blue, got yellow
    """
    if value not in valid_values:
        valid_str = ", ".join(str(v) for v in valid_values)
        raise ChoiceValidationError(
            f"{field_name} must be one of: {valid_str}, got {value}"
        )


def validate_value_in_range(
    value: int | float,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    field_name: str = "Value",
) -> None:
    """
    Validate that a numeric value is within a range.

    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value (None for no limit)
        max_value: Maximum allowed value (None for no limit)
        field_name: Name of field for error messages

    Raises:
        RangeValidationError: If value is out of range

    Example:
        >>> validate_value_in_range(5, min_value=0, max_value=10)
        >>> validate_value_in_range(-1, min_value=0)
        Traceback (most recent call last):
            ...
        RangeValidationError: Value must be >= 0, got -1
    """
    if min_value is not None and value < min_value:
        raise RangeValidationError(f"{field_name} must be >= {min_value}, got {value}")
    if max_value is not None and value > max_value:
        raise RangeValidationError(f"{field_name} must be <= {max_value}, got {value}")


def validate_length(
    value: str | list[Any],
    min_length: int | None = None,
    max_length: int | None = None,
    field_name: str = "Value",
) -> None:
    """
    Validate the length of a string or list.

    Args:
        value: String or list to validate
        min_length: Minimum allowed length (None for no limit)
        max_length: Maximum allowed length (None for no limit)
        field_name: Name of field for error messages

    Raises:
        TypeError: If value is not string or list
        LengthValidationError: If length is out of range

    Example:
        >>> validate_length("hello", min_length=3, max_length=10)
        >>> validate_length("hi", min_length=3)
        Traceback (most recent call last):
            ...
        LengthValidationError: Value must have length >= 3, got 2
    """
    if not isinstance(value, (str, list)):
        raise TypeError(f"{field_name} must be string or list")

    length = len(value)
    if min_length is not None and length < min_length:
        raise LengthValidationError(
            f"{field_name} must have length >= {min_length}, got {length}"
        )
    if max_length is not None and length > max_length:
        raise LengthValidationError(
            f"{field_name} must have length <= {max_length}, got {length}"
        )
