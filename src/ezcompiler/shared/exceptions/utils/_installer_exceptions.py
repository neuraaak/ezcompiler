# ///////////////////////////////////////////////////////////////
# INSTALLER_EXCEPTIONS - Installer (Inno Setup) operation exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Installer exceptions - Specialized exceptions for installer packaging.

Canonical ``InstallerError`` lives here (utils subtree), under
``EzCompilerError``. Mirrors the ``ReleaseError`` pattern.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class InstallerError(EzCompilerError):
    """Base exception for installer packaging errors (canonical)."""


class InstallerTypeError(InstallerError):
    """Raised when the requested installer type is not supported."""


class IsccNotFoundError(InstallerError):
    """Raised when the Inno Setup compiler (ISCC.exe) cannot be located."""


class InstallerBuildError(InstallerError):
    """Raised when running ISCC.exe against the .iss script fails."""


class InstallerConfigError(InstallerError):
    """Raised when installer configuration is invalid or incomplete."""
