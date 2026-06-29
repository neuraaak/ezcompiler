# ///////////////////////////////////////////////////////////////
# UPDATER_EXCEPTIONS - Updater client generation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Updater exceptions - Exceptions for client update script generation.

Canonical ``UpdaterError`` lives here (utils subtree), under ``EzCompilerError``.
The services subtree re-imports it instead of redefining one — mirrors the
``ReleaseError`` / ``UploadError`` pattern.
"""

from __future__ import annotations

from ._base import EzCompilerError


class UpdaterError(EzCompilerError):
    """Base exception for updater client generation errors (canonical)."""


class UpdaterConfigError(UpdaterError):
    """Raised when updater config is invalid or incomplete."""


class UpdaterGenerationError(UpdaterError):
    """Raised when generating or writing updater files fails."""
