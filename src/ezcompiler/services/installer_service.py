# ///////////////////////////////////////////////////////////////
# INSTALLER_SERVICE - Installer build orchestration service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Installer service - Orchestrates first-deployment installer packaging.

Builds a setup.exe from a compiled bundle via an installer adapter
(InstallerFactory). Mirrors ReleaseService's structure.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from pathlib import Path

from ..adapters import InstallerFactory
from ..shared import InstallerConfig

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class InstallerService:
    """Service orchestrating first-deployment installer packaging."""

    # ------------------------------------------------
    # BUILD METHODS
    # ------------------------------------------------

    @staticmethod
    def build_installer(
        bundle_dir: Path,
        app_name: str,
        version: str,
        output_dir: Path,
        *,
        installer_type: str = "innosetup",
        installer_config: InstallerConfig | None = None,
    ) -> Path:
        """Build the installer executable for a compiled bundle.

        Args:
            bundle_dir: Directory containing the compiled application.
            app_name: Application name.
            version: Application version string.
            output_dir: Directory where the setup.exe is produced.
            installer_type: Installer backend to use (default: "innosetup").
            installer_config: Config forwarded to the installer adapter.

        Returns:
            Path: The produced setup.exe path.

        Raises:
            InstallerError: When installer packaging fails.
        """
        installer = InstallerFactory.create_installer(installer_type, installer_config)
        return installer.build(
            bundle_dir=bundle_dir,
            app_name=app_name,
            version=version,
            output_dir=output_dir,
        )
