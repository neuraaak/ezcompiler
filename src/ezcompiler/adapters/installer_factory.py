# ///////////////////////////////////////////////////////////////
# INSTALLER_FACTORY - Factory for installer instances
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Installer factory - Centralized creation of installer instances by type."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from typing import Any

from ..shared.exceptions import InstallerTypeError
from ..types import InstallerPort
from ._innosetup_installer import InnoSetupInstaller

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class InstallerFactory:
    """Factory class for creating installer instances."""

    # ------------------------------------------------
    # FACTORY METHODS
    # ------------------------------------------------

    @staticmethod
    def create_installer(
        installer_type: str, config: dict[str, Any] | None = None
    ) -> InstallerPort:
        """Create an installer instance for the given type.

        Args:
            installer_type: Type of installer builder ("innosetup")
            config: Configuration dictionary for the installer adapter

        Returns:
            InstallerPort: Configured installer instance (satisfies the Port)

        Raises:
            InstallerTypeError: If installer type is not supported
        """
        normalized = installer_type.lower()
        if normalized == "innosetup":
            return InnoSetupInstaller(config)
        raise InstallerTypeError(f"Unsupported installer type: {installer_type}")

    @staticmethod
    def get_supported_types() -> list[str]:
        """Return the list of supported installer backend names."""
        return ["innosetup"]
