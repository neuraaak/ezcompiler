# ///////////////////////////////////////////////////////////////
# DOMAIN_VALIDATORS - Domain-specific validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Domain validators - Validation utilities for project-specific domains.

This module provides validation functions for project-specific data types
like compiler names and upload structures.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .value_validators import validate_choice

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_compiler_name(compiler: str) -> bool:
    """
    Validate a compiler name.

    Args:
        compiler: Compiler name to validate

    Returns:
        bool: True if compiler name is valid, False otherwise

    Note:
        Valid compilers: "Cx_Freeze", "PyInstaller", "Nuitka"

    Example:
        >>> validate_compiler_name("PyInstaller")
        True
        >>> validate_compiler_name("auto")
        False
        >>> validate_compiler_name("InvalidCompiler")
        False
    """
    valid_compilers = ["Cx_Freeze", "PyInstaller", "Nuitka"]
    return validate_choice(compiler, valid_compilers)


def validate_upload_structure(structure: str) -> bool:
    """
    Validate an upload structure type.

    Args:
        structure: Upload structure to validate

    Returns:
        bool: True if upload structure is valid, False otherwise

    Note:
        Valid structures: "disk", "server"

    Example:
        >>> validate_upload_structure("disk")
        True
        >>> validate_upload_structure("server")
        True
        >>> validate_upload_structure("cloud")
        False
    """
    valid_structures = ["disk", "server", "r2"]
    return validate_choice(structure, valid_structures)
