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
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ..adapters import InstallerFactory
from ..adapters._iss_renderer import render_iss
from ..shared import InstallerConfig
from ..shared.exceptions import InstallerConfigError

if TYPE_CHECKING:
    from ..shared._compiler_config import CompilerConfig

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_logger = logging.getLogger(__name__)

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
        company_name: str = "",
        icon: str = "",
        main_file: str = "",
    ) -> Path:
        """Build the installer executable for a compiled bundle.

        Args:
            bundle_dir: Directory containing the compiled application.
            app_name: Application name.
            version: Application version string.
            output_dir: Directory where the setup.exe is produced.
            installer_type: Installer backend to use (default: "innosetup").
            installer_config: Config forwarded to the installer adapter.
            company_name: Publisher name; feeds the AppId GUID derivation
                (see ``_iss_renderer.resolve_app_id``) — must match whatever
                ``generate iss`` uses for the same product, or the two
                builds mint different AppIds for one product.
            icon: Path to the setup wizard icon.
            main_file: Entry-point script; disambiguates the main executable
                when the bundle holds several and none matches ``app_name``.

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
            company_name=company_name,
            icon=icon,
            main_file=main_file,
        )

    @staticmethod
    def generate_iss_script(
        config: CompilerConfig, output_path: Path, *, force: bool
    ) -> Path:
        """Render a standalone, committable ``.iss`` script for ``config``.

        Unlike the ephemeral build path, the icon is emitted verbatim
        (never absolutized): the standalone script is meant to be committed,
        and an absolute machine-specific path would defeat that. A relative
        icon triggers a warning, since ISCC resolves it against the ``.iss``
        file's own directory rather than the process cwd.

        Args:
            config: Compiler configuration (provides installer, company_name,
                icon and project_name).
            output_path: Destination ``.iss`` file path.
            force: When False, refuse to overwrite an existing file.

        Returns:
            Path: ``output_path``, once written.

        Raises:
            InstallerConfigError: If ``output_path`` already exists and
                ``force`` is False.
        """
        if output_path.exists() and not force:
            raise InstallerConfigError(
                f"{output_path} already exists; pass --force to overwrite it"
            )

        if config.icon and not Path(config.icon).is_absolute():
            _logger.warning(
                "installer.icon %r is a relative path: ISCC resolves it "
                "against the .iss file's own directory, not the current "
                "working directory",
                config.icon,
            )

        content = render_iss(
            config.installer,
            project_name=config.project_name,
            company_name=config.company_name,
            icon=config.icon,
            standalone=True,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8-sig")
        return output_path
