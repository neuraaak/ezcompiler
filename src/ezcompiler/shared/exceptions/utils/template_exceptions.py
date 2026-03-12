# ///////////////////////////////////////////////////////////////
# TEMPLATE_EXCEPTIONS - Template processing exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Template exceptions - Specialized exceptions for template processing operations.

This module defines exceptions for template variable substitution,
file generation, and template validation failures.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from .base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class TemplateProcessingError(EzCompilerError):
    """Base exception for template processing errors."""


class TemplateSubstitutionError(TemplateProcessingError):
    """Raised when template variable substitution fails."""


class TemplateFileWriteError(TemplateProcessingError):
    """Raised when writing a processed template to file fails."""


class TemplateValidationError(TemplateProcessingError):
    """Raised when template syntax validation fails."""
