# ///////////////////////////////////////////////////////////////
# VALIDATION_UTILS - Data validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Validation utilities - Data validation utilities for EzCompiler.

This module provides utility functions for validating various types of data
used throughout the EzCompiler project, including strings, paths, configuration,
and project-specific validators.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path
from typing import Any

# Local imports
from ..core.exceptions import ConfigurationError

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ValidationUtils:
    """
    Data validation utility class.

    Provides static methods for validating various types of data
    used throughout the EzCompiler project, including version strings,
    email addresses, file paths, and configuration structures.

    Example:
        >>> ValidationUtils.validate_version_string("1.0.0")
        True
        >>> ValidationUtils.validate_email("user@example.com")
        True
    """

    # ////////////////////////////////////////////////
    # FORMAT VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_version_string(version: str) -> bool:
        """
        Validate a version string format.

        Args:
            version: Version string to validate

        Returns:
            bool: True if version format is valid (e.g., 1.0.0), False otherwise

        Note:
            Accepts common version formats: x.y.z, x.y.z.w, x.y, etc.
        """
        if not isinstance(version, str):
            return False

        # Check for common version formats: x.y.z, x.y.z.w, x.y, etc.
        version_pattern = r"^\d+(\.\d+)*$"
        return bool(re.match(version_pattern, version))

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate an email address format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if email format is valid, False otherwise

        Note:
            Uses basic regex pattern validation. Not a strict RFC 5322 validator.
        """
        if not isinstance(email, str):
            return False

        # Basic email validation pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate a URL format.

        Args:
            url: URL to validate

        Returns:
            bool: True if URL format is valid, False otherwise

        Note:
            Validates basic HTTP/HTTPS URL structure.
        """
        if not isinstance(url, str):
            return False

        # Basic URL validation pattern
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(url_pattern, url))

    # ////////////////////////////////////////////////
    # PATH VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_file_path(path: str | Path) -> bool:
        """
        Validate a file path.

        Args:
            path: File path to validate

        Returns:
            bool: True if path format is valid, False otherwise

        Note:
            Checks for valid characters and structure, not existence.
        """
        try:
            path_obj = Path(path)
            # Check if path has valid characters and structure
            path_str = str(path_obj)
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
            return len(path_str) > 0 and not any(
                char in path_str for char in invalid_chars
            )
        except Exception:
            return False

    @staticmethod
    def validate_directory_path(path: str | Path) -> bool:
        """
        Validate a directory path.

        Args:
            path: Directory path to validate

        Returns:
            bool: True if path format is valid, False otherwise

        Note:
            Uses same validation as file path validation.
        """
        return ValidationUtils.validate_file_path(path)

    # ////////////////////////////////////////////////
    # DICTIONARY VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_required_fields(
        data: dict[str, Any], required_fields: list[str]
    ) -> None:
        """
        Validate that required fields are present in a dictionary.

        Args:
            data: Dictionary to validate
            required_fields: List of required field names

        Raises:
            ConfigurationError: If data is not a dict or required fields are missing
        """
        if not isinstance(data, dict):
            raise ConfigurationError("Data must be a dictionary")

        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ConfigurationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    @staticmethod
    def validate_field_types(
        data: dict[str, Any], field_types: dict[str, type]
    ) -> None:
        """
        Validate that fields have the correct types.

        Args:
            data: Dictionary to validate
            field_types: Dictionary mapping field names to expected types

        Raises:
            ConfigurationError: If data is not a dict or field types are incorrect
        """
        if not isinstance(data, dict):
            raise ConfigurationError("Data must be a dictionary")

        for field, expected_type in field_types.items():
            if (
                field in data
                and data[field] is not None
                and not isinstance(data[field], expected_type)
            ):
                raise ConfigurationError(
                    f"Field '{field}' must be of type {expected_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )

    # ////////////////////////////////////////////////
    # STRING VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
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
        """
        if not isinstance(value, str):
            return False

        if len(value) < min_length:
            return False

        return not (max_length is not None and len(value) > max_length)

    # ////////////////////////////////////////////////
    # NUMERIC VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
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
        """
        if not isinstance(value, (int, float)):
            return False

        if min_value is not None and value < min_value:
            return False

        return not (max_value is not None and value > max_value)

    @staticmethod
    def validate_positive_integer(value: Any) -> bool:
        """
        Validate that a value is a positive integer.

        Args:
            value: Value to validate

        Returns:
            bool: True if value is a positive integer, False otherwise
        """
        return isinstance(value, int) and value > 0

    @staticmethod
    def validate_non_negative_integer(value: Any) -> bool:
        """
        Validate that a value is a non-negative integer.

        Args:
            value: Value to validate

        Returns:
            bool: True if value is a non-negative integer, False otherwise
        """
        return isinstance(value, int) and value >= 0

    # ////////////////////////////////////////////////
    # COLLECTION VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
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
        """
        if not isinstance(value, list):
            return False

        if len(value) < min_length:
            return False

        return not (max_length is not None and len(value) > max_length)

    @staticmethod
    def validate_choice(value: Any, valid_choices: list[Any]) -> bool:
        """
        Validate that a value is one of the valid choices.

        Args:
            value: Value to validate
            valid_choices: List of valid choices

        Returns:
            bool: True if value is a valid choice, False otherwise
        """
        return value in valid_choices

    # ////////////////////////////////////////////////
    # BOOLEAN AND TYPE VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """
        Validate that a value is a boolean.

        Args:
            value: Value to validate

        Returns:
            bool: True if value is a boolean, False otherwise
        """
        return isinstance(value, bool)

    # ////////////////////////////////////////////////
    # PROJECT-SPECIFIC VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_compiler_name(compiler: str) -> bool:
        """
        Validate a compiler name.

        Args:
            compiler: Compiler name to validate

        Returns:
            bool: True if compiler name is valid, False otherwise

        Note:
            Valid compilers: "auto", "Cx_Freeze", "PyInstaller"
        """
        valid_compilers = ["auto", "Cx_Freeze", "PyInstaller"]
        return ValidationUtils.validate_choice(compiler, valid_compilers)

    @staticmethod
    def validate_upload_structure(structure: str) -> bool:
        """
        Validate an upload structure type.

        Args:
            structure: Upload structure to validate

        Returns:
            bool: True if upload structure is valid, False otherwise

        Note:
            Valid structures: "disk", "server"
        """
        valid_structures = ["disk", "server"]
        return ValidationUtils.validate_choice(structure, valid_structures)

    # ////////////////////////////////////////////////
    # STRING SANITIZATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename by removing invalid characters.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename with invalid characters removed

        Note:
            Returns "unnamed_file" if filename becomes empty after sanitization.
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

    # ////////////////////////////////////////////////
    # CONFIGURATION VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_config_dict(config: dict[str, Any]) -> None:
        """
        Validate a configuration dictionary structure.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ConfigurationError: If configuration is invalid

        Note:
            Validates required top-level sections and their formats.
        """
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration must be a dictionary")

        # Check for required top-level sections
        required_sections = ["version", "project_name", "main_file"]
        ValidationUtils.validate_required_fields(config, required_sections)

        # Validate version format
        if not ValidationUtils.validate_version_string(config["version"]):
            raise ConfigurationError("Invalid version format")

        # Validate project name
        if not ValidationUtils.validate_string_length(
            config["project_name"], min_length=1
        ):
            raise ConfigurationError("Project name cannot be empty")

        # Validate main file path
        if not ValidationUtils.validate_file_path(config["main_file"]):
            raise ConfigurationError("Invalid main file path")
