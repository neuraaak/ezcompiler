# ///////////////////////////////////////////////////////////////
# BASE_INSTALLER - Abstract base installer interface
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base installer - Abstract base class for first-deployment installer builders.

Defines the interface (conforming to ``types.InstallerPort``) and shared
validation. The structural contract is the Port; this base factors common
behaviour. Boundaries are typed via the Port, not this base.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..shared.exceptions import InstallerConfigError

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class BaseInstaller(ABC):
    """Abstract base class for first-deployment installer builders."""

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    # ////////////////////////////////////////////////
    # ABSTRACT METHODS
    # ////////////////////////////////////////////////

    @abstractmethod
    def build(
        self, bundle_dir: Path, app_name: str, version: str, output_dir: Path
    ) -> Path:
        """Build the installer executable. Raises InstallerError on failure."""

    @abstractmethod
    def get_installer_name(self) -> str:
        """Human-readable installer backend name."""

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def _validate_bundle_dir(self, bundle_dir: Path) -> None:
        """Ensure the bundle directory exists and is non-empty."""
        if not bundle_dir.is_dir():
            raise InstallerConfigError(f"Bundle directory does not exist: {bundle_dir}")
        if not any(bundle_dir.iterdir()):
            raise InstallerConfigError(f"Bundle directory is empty: {bundle_dir}")
