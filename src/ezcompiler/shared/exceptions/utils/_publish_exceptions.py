# ///////////////////////////////////////////////////////////////
# PUBLISH_EXCEPTIONS - Release publication (gh/glab) exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Specialized exceptions for release publication."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PublishError(EzCompilerError):
    """Base exception for release publication errors (canonical)."""


class PublisherTypeError(PublishError):
    """Raised when the requested publisher type is not supported."""


class PublishCliError(PublishError):
    """Raised when the external CLI is missing or exits non-zero."""


class PublishAuthError(PublishError):
    """Raised when the external CLI is not authenticated."""
