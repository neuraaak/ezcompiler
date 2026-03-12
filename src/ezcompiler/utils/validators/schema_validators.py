# ///////////////////////////////////////////////////////////////
# SCHEMA_VALIDATORS - Schema validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Schema validators - Validation utilities for dictionary schemas and structures.

This module provides validation functions for validating dictionary structures,
required fields, field types, and complex schema validation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Local imports
from ...shared.exceptions.utils.validation_exceptions import (
    FormatValidationError,
    LengthValidationError,
    RequiredFieldError,
    SchemaValidationError,
    TypeValidationError,
)
from .format_validators import validate_version_string
from .path_validators import validate_file_path
from .string_validators import validate_pattern
from .type_validators import validate_type
from .value_validators import (
    validate_length,
    validate_not_empty,
    validate_one_of,
    validate_string_length,
    validate_value_in_range,
)

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> None:
    """
    Validate that required fields are present in a dictionary.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Raises:
        TypeError: If data is not a dict
        RequiredFieldError: If required fields are missing

    Example:
        >>> validate_required_fields({"name": "test", "age": 25}, ["name", "age"])
        >>> validate_required_fields({"name": "test"}, ["name", "age"])
        Traceback (most recent call last):
            ...
        RequiredFieldError: Missing required fields: age
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise RequiredFieldError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )


def validate_field_types(data: dict[str, Any], field_types: dict[str, type]) -> None:
    """
    Validate that fields have the correct types.

    Args:
        data: Dictionary to validate
        field_types: Dictionary mapping field names to expected types

    Raises:
        TypeError: If data is not a dict
        TypeValidationError: If field types are incorrect

    Example:
        >>> validate_field_types({"name": "test", "age": 25}, {"name": str, "age": int})
        >>> validate_field_types({"name": "test", "age": "25"}, {"name": str, "age": int})
        Traceback (most recent call last):
            ...
        TypeValidationError: Field 'age' must be of type int, got str
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    for field, expected_type in field_types.items():
        if (
            field in data
            and data[field] is not None
            and not isinstance(data[field], expected_type)
        ):
            raise TypeValidationError(
                f"Field '{field}' must be of type {expected_type.__name__}, "
                f"got {type(data[field]).__name__}"
            )


def validate_config_dict(config: dict[str, Any]) -> None:
    """
    Validate a configuration dictionary structure.

    Args:
        config: Configuration dictionary to validate

    Raises:
        SchemaValidationError: If configuration is invalid

    Note:
        Validates required top-level sections and their formats.

    Example:
        >>> config = {
        ...     "version": "1.0.0",
        ...     "project_name": "MyProject",
        ...     "main_file": "main.py"
        ... }
        >>> validate_config_dict(config)
    """
    if not isinstance(config, dict):
        raise SchemaValidationError("Configuration must be a dictionary")

    # Check for required top-level sections
    required_sections = ["version", "project_name", "main_file"]
    validate_required_fields(config, required_sections)

    # Validate version format
    if not validate_version_string(config["version"]):
        raise FormatValidationError("Invalid version format")

    # Validate project name
    if not validate_string_length(config["project_name"], min_length=1):
        raise LengthValidationError("Project name cannot be empty")

    # Validate main file path
    if not validate_file_path(config["main_file"]):
        raise FormatValidationError("Invalid main file path")


def validate_dict_schema(
    data: dict[str, Any],
    schema: dict[str, dict[str, Any]],
) -> None:
    """
    Validate a dictionary against a schema.

    Schema format:
    {
        "field_name": {
            "type": (str, int, ...),  # Required type(s)
            "required": True/False,     # Is field required
            "empty": True/False,        # Allow empty values
            "choices": [...]            # Valid choices
            "min_length": int,          # Min length (str/list)
            "max_length": int,          # Max length (str/list)
            "min_value": int/float,     # Min value (numeric)
            "max_value": int/float,     # Max value (numeric)
            "pattern": "regex",         # Regex pattern (str)
        }
    }

    Args:
        data: Dictionary to validate
        schema: Validation schema

    Raises:
        SchemaValidationError: If validation fails

    Example:
        >>> schema = {  # noqa: W605
        ...     "version": {"type": str, "required": True, "pattern": r"^\\d+\\.\\d+\\.\\d+$"},  # noqa: W605
        ...     "port": {"type": int, "required": False, "min_value": 1, "max_value": 65535},
        ... }
        >>> validate_dict_schema(data, schema)
    """
    if not isinstance(data, dict):
        raise SchemaValidationError("Data must be a dictionary")

    for field_name, field_schema in schema.items():
        value = data.get(field_name)

        # Check required fields
        if field_schema.get("required", False) and value is None:
            raise SchemaValidationError(f"Field '{field_name}' is required")

        # Skip validation for None optional fields
        if value is None:
            continue

        # Check not empty
        if not field_schema.get("empty", True):
            validate_not_empty(value, field_name)

        # Check type
        if "type" in field_schema:
            validate_type(value, field_schema["type"], field_name)

        # Check choices
        if "choices" in field_schema:
            validate_one_of(value, field_schema["choices"], field_name)

        # Check length (for strings/lists)
        if isinstance(value, (str, list)):
            min_len = field_schema.get("min_length")
            max_len = field_schema.get("max_length")
            if min_len is not None or max_len is not None:
                validate_length(value, min_len, max_len, field_name)

        # Check numeric range
        if isinstance(value, (int, float)):
            min_val = field_schema.get("min_value")
            max_val = field_schema.get("max_value")
            if min_val is not None or max_val is not None:
                validate_value_in_range(value, min_val, max_val, field_name)

        # Check pattern (for strings)
        if isinstance(value, str) and "pattern" in field_schema:
            validate_pattern(value, field_schema["pattern"], field_name)
