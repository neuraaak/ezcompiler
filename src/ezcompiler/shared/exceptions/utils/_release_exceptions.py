# ///////////////////////////////////////////////////////////////
# RELEASE_EXCEPTIONS - Release (TUF/tufup) operation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Release exceptions - Specialized exceptions for secure-release operations.

Canonical ``ReleaseError`` lives here (utils subtree), under ``EzCompilerError``.
The services subtree re-imports it instead of redefining one — a single
``ReleaseError`` shared by all code (mirrors the ``UploadError`` pattern).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ReleaseError(EzCompilerError):
    """Base exception for secure-release operation errors (canonical)."""


class ReleaserTypeError(ReleaseError):
    """Raised when the requested releaser type is not supported."""


class BundleBuildError(ReleaseError):
    """Raised when building the release bundle archive fails."""


class SigningKeyError(ReleaseError):
    """Raised when signing keys are missing, invalid, or inaccessible."""


class ReleaseConfigError(ReleaseError):
    """Raised when release configuration is invalid or incomplete."""
