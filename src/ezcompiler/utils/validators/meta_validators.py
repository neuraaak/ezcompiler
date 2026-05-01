# ///////////////////////////////////////////////////////////////
# META_VALIDATORS - Meta validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Meta validators - Validation utilities for batch validation operations.

This module provides validation functions for performing multiple validations
at once using a declarative approach.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from collections.abc import Callable
from typing import Any

# Local imports
from ...shared.exceptions.utils import SchemaValidationError

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_multiple(
    validations: list[tuple[Any, str, str]],
    validators: dict[str, Callable],
) -> None:
    """
    Perform multiple validations at once.

    Args:
        validations: List of (value, validator_name, field_name) tuples
        validators: Dict of validator_name -> validator_function

    Raises:
        SchemaValidationError: If any validation fails

    Example:
        >>> validations = [
        ...     ("1.0.0", "version_string", "version"),
        ...     ("user@example.com", "email", "contact_email"),
        ...     ("https://example.com", "url", "server_url"),
        ... ]
        >>> validators = {
        ...     "version_string": ValidationUtils.validate_version_string,
        ...     "email": ValidationUtils.validate_email,
        ...     "url": ValidationUtils.validate_url,
        ... }
        >>> validate_multiple(validations, validators)

    Raises:
        SchemaValidationError: If any validation fails
    """
    for value, validator_name, field_name in validations:
        if validator_name not in validators:
            raise SchemaValidationError(f"Unknown validator: {validator_name}")

        validator = validators[validator_name]
        result = validator(value)
        if not result:
            raise SchemaValidationError(f"Invalid {field_name}: {value}")
