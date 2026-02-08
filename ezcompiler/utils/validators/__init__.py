# ///////////////////////////////////////////////////////////////
# VALIDATORS - Validation utilities package
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Validators package - Modular validation utilities for EzCompiler.

This package provides validation functions organized by domain:
- format_validators: Version, email, URL validation
- path_validators: File and directory path validation
- type_validators: Type checking and validation
- value_validators: Range, length, choice validation
- schema_validators: Schema and configuration validation
- domain_validators: Domain-specific validators (compiler, upload)
- string_validators: String utilities and pattern validation
- meta_validators: Meta-validation utilities

For backward compatibility, all validators are re-exported at package level.
"""

from __future__ import annotations

# Domain validators
from .domain_validators import (
    validate_compiler_name,
    validate_upload_structure,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Format validators
from .format_validators import (
    validate_email,
    validate_url,
    validate_version_string,
)

# Meta validators
from .meta_validators import validate_multiple

# Path validators
from .path_validators import (
    validate_directory_path,
    validate_file_path,
)

# Schema validators
from .schema_validators import (
    validate_config_dict,
    validate_dict_schema,
    validate_field_types,
    validate_required_fields,
)

# String validators
from .string_validators import (
    sanitize_filename,
    validate_pattern,
)

# Type validators
from .type_validators import (
    validate_boolean,
    validate_non_negative_integer,
    validate_positive_integer,
    validate_type,
)

# Value validators
from .value_validators import (
    validate_choice,
    validate_length,
    validate_list_length,
    validate_not_empty,
    validate_numeric_range,
    validate_one_of,
    validate_string_length,
    validate_value_in_range,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////
__all__ = [
    # Format validators
    "validate_version_string",
    "validate_email",
    "validate_url",
    # Path validators
    "validate_file_path",
    "validate_directory_path",
    # Type validators
    "validate_boolean",
    "validate_positive_integer",
    "validate_non_negative_integer",
    "validate_type",
    # Value validators
    "validate_string_length",
    "validate_numeric_range",
    "validate_list_length",
    "validate_choice",
    "validate_not_empty",
    "validate_one_of",
    "validate_value_in_range",
    "validate_length",
    # Schema validators
    "validate_required_fields",
    "validate_field_types",
    "validate_config_dict",
    "validate_dict_schema",
    # Domain validators
    "validate_compiler_name",
    "validate_upload_structure",
    # String validators
    "sanitize_filename",
    "validate_pattern",
    # Meta validators
    "validate_multiple",
]
