# ///////////////////////////////////////////////////////////////
# VALIDATION_EXCEPTIONS - Validation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Validation exceptions - Specialized exceptions for validation operations.

This module defines exceptions for various validation failures
used by ValidationUtils and validation operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ValidationError(EzCompilerError):
    """Base exception for validation errors."""


class TypeValidationError(ValidationError):
    """Raised when type validation fails."""


class FormatValidationError(ValidationError):
    """Raised when format validation fails (version, email, URL, etc.)."""


class RangeValidationError(ValidationError):
    """Raised when value range validation fails."""


class LengthValidationError(ValidationError):
    """Raised when length validation fails."""


class PatternValidationError(ValidationError):
    """Raised when regex pattern validation fails."""


class SchemaValidationError(ValidationError):
    """Raised when dictionary schema validation fails."""


class ChoiceValidationError(ValidationError):
    """Raised when value is not in valid choices."""


class RequiredFieldError(ValidationError):
    """Raised when required field is missing or empty."""
