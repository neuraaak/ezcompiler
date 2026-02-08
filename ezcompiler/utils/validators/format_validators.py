# ///////////////////////////////////////////////////////////////
# FORMAT_VALIDATORS - Format validation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Format validators - Validation utilities for common data formats.

This module provides validation functions for common data formats like
version strings, email addresses, and URLs.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_version_string(version: str) -> bool:
    """
    Validate a version string format.

    Args:
        version: Version string to validate

    Returns:
        bool: True if version format is valid (e.g., 1.0.0), False otherwise

    Note:
        Accepts common version formats: x.y.z, x.y.z.w, x.y, etc.

    Example:
        >>> validate_version_string("1.0.0")
        True
        >>> validate_version_string("1.0")
        True
        >>> validate_version_string("invalid")
        False
    """
    if not isinstance(version, str):
        return False

    # Check for common version formats: x.y.z, x.y.z.w, x.y, etc.
    version_pattern = r"^\d+(\.\d+)*$"
    return bool(re.match(version_pattern, version))


def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email format is valid, False otherwise

    Note:
        Uses basic regex pattern validation. Not a strict RFC 5322 validator.

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not isinstance(email, str):
        return False

    # Basic email validation pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate a URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if URL format is valid, False otherwise

    Note:
        Validates basic HTTP/HTTPS URL structure.

    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("http://example.com/path")
        True
        >>> validate_url("invalid-url")
        False
    """
    if not isinstance(url, str):
        return False

    # Basic URL validation pattern
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(url_pattern, url))
