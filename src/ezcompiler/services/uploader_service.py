# ///////////////////////////////////////////////////////////////
# UPLOADER_SERVICE - Upload orchestration service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Uploader service - Upload orchestration service for EzCompiler.

This module provides the UploaderService class that orchestrates file
and directory uploads using different upload backends (disk, server).

Services layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

# Local imports
from ..adapters import UploaderFactory
from ..shared._constants import RELEASE_SUBDIR, UPDATE_SUBDIR
from ..shared.exceptions import UploadError
from ..utils.validators import validate_upload_structure

if TYPE_CHECKING:
    from ..shared._compiler_config import CompilerConfig
    from ..types import UploaderPort

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

UploadType = Literal["disk", "server", "r2"]

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class UploaderService:
    """
    Upload orchestration service.

    Orchestrates file and directory uploads using different upload backends.
    Handles upload type selection, validation, and execution.

    Example:
        >>> service = UploaderService()
        >>> service.upload(
        ...     source_path=Path("dist.zip"),
        ...     upload_type="disk",
        ...     destination="releases/",
        ...     upload_config={"overwrite": True}
        ... )
    """

    # ////////////////////////////////////////////////
    # UPLOAD METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def upload(
        source_path: Path,
        upload_type: UploadType,
        destination: str,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Upload a file or directory to the specified destination.

        Args:
            source_path: Path to the source file or directory
            upload_type: Type of upload ("disk" or "server")
            destination: Destination path or URL
            upload_config: Additional uploader configuration options

        Raises:
            UploadError: If upload fails or upload type is invalid

        Example:
            >>> UploaderService.upload(
            ...     Path("dist.zip"),
            ...     "disk",
            ...     "releases/",
            ...     {"overwrite": True}
            ... )
        """
        try:
            # Validate upload type
            if not validate_upload_structure(upload_type):
                raise UploadError(f"Invalid upload type: {upload_type}")

            # Prepare uploader configuration
            config = upload_config or {}
            if upload_type == "disk":
                config["destination_path"] = destination
            elif upload_type == "server":
                config["server_url"] = destination
            # r2: bucket vient de upload_config, destination = préfixe objet

            # Create uploader and perform upload
            uploader: UploaderPort = UploaderFactory.create_uploader(
                upload_type, config
            )
            uploader.upload(source_path=source_path, destination=destination)
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Upload failed: {str(e)}") from e

    @staticmethod
    def download(
        remote_source: str,
        upload_type: UploadType,
        destination_local: Path,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Download a remote tree into ``destination_local`` via the backend.

        Args:
            remote_source: Remote source (path, URL or prefix) to fetch.
            upload_type: Backend type ("disk", "server" or "r2").
            destination_local: Local directory to populate.
            upload_config: Additional uploader configuration options.

        Raises:
            UploadError: If the download fails or the type is invalid.
        """
        try:
            uploader: UploaderPort = UploaderFactory.create_uploader(
                upload_type, upload_config or {}
            )
            uploader.download(remote_source, destination_local)
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Download failed: {str(e)}") from e

    @staticmethod
    def upload_release(
        config: CompilerConfig,
        repo_dir: Path,
        release_root: Path | None,
        destination: str | None = None,
        repo_destination: str | None = None,
        release_destination: str | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Double upload séquentiel : arbre TUF puis zip installeur.

        Étape 1 — upload arbre TUF vers ``<dest>/update/`` (ou préfixe R2).
        Étape 2 — upload zip installeur vers ``<dest>/release/`` (ignoré si R2).

        Note: Le double-upload n'est pas atomique. Si l'upload du zip échoue,
        le repo TUF est déjà en ligne. En cas d'échec, ré-exécuter upload()
        pour reprendre.

        Args:
            config: CompilerConfig contenant les destinations et options R2.
            repo_dir: Répertoire local du repo TUF.
            release_root: Répertoire local du zip installeur (None si R2).
            destination: Override commun pour les deux destinations.
            repo_destination: Override de ``config.repo_destination``.
            release_destination: Override de ``config.release_destination``.
            upload_config: Options supplémentaires passées aux uploaders.

        Raises:
            UploadError: Si un upload échoue.
        """
        repo_dest = repo_destination or config.repo_destination
        rel_dest = release_destination or config.release_destination

        UploaderService._upload_tuf_repo(
            config, repo_dir, repo_dest, destination, upload_config
        )

        if release_root is not None:
            UploaderService._upload_release_zip(
                config, release_root, rel_dest, destination, upload_config
            )

    @staticmethod
    def _upload_tuf_repo(
        config: CompilerConfig,
        repo_dir: Path,
        repo_dest: str,
        destination: str | None,
        upload_config: dict[str, Any] | None,
    ) -> None:
        """Upload l'arbre TUF vers la destination configurée."""
        try:
            if repo_dest == "r2":
                endpoint = config.repo_endpoint
                bucket, _, prefix = endpoint.partition("/")
                UploaderService.upload(
                    source_path=repo_dir,
                    upload_type="r2",
                    destination=prefix,
                    upload_config={"bucket": bucket},
                )
            elif repo_dest == "server":
                base = destination or config.resolved_repo_destination or ""
                UploaderService.upload(
                    source_path=repo_dir,
                    upload_type="server",
                    destination=base.rstrip("/") + f"/{UPDATE_SUBDIR}",
                    upload_config=upload_config,
                )
            else:  # disk (default)
                base = destination or config.resolved_repo_destination or ""
                UploaderService.upload(
                    source_path=repo_dir,
                    upload_type="disk",
                    destination=str(Path(base) / UPDATE_SUBDIR),
                    upload_config=upload_config,
                )
        except UploadError as e:
            raise UploadError(f"TUF repo upload failed: {e}") from e

    @staticmethod
    def _upload_release_zip(
        config: CompilerConfig,
        release_root: Path,
        rel_dest: str,
        destination: str | None,
        upload_config: dict[str, Any] | None,
    ) -> None:
        """Upload le zip installeur vers la destination configurée."""
        try:
            if rel_dest == "r2":
                endpoint = config.release_endpoint
                bucket, _, prefix = endpoint.partition("/")
                UploaderService.upload(
                    source_path=release_root,
                    upload_type="r2",
                    destination=prefix,
                    upload_config={"bucket": bucket},
                )
            elif rel_dest == "server":
                base = destination or config.resolved_release_destination or ""
                UploaderService.upload(
                    source_path=release_root,
                    upload_type="server",
                    destination=base.rstrip("/") + f"/{RELEASE_SUBDIR}",
                    upload_config=upload_config,
                )
            else:  # disk (default)
                base = destination or config.resolved_release_destination or ""
                UploaderService.upload(
                    source_path=release_root,
                    upload_type="disk",
                    destination=str(Path(base) / RELEASE_SUBDIR),
                    upload_config=upload_config,
                )
        except UploadError as e:
            raise UploadError(f"Release zip upload failed: {e}") from e

    # ////////////////////////////////////////////////
    # UTILITY METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def get_supported_types() -> list[str]:
        """
        Get list of supported upload types.

        Returns:
            list[str]: List of supported upload type names

        Example:
            >>> types = UploaderService.get_supported_types()
            >>> print(types)
            ['disk', 'server']
        """
        return UploaderFactory.get_supported_types()

    @staticmethod
    def validate_upload_config(
        upload_type: UploadType, config: dict[str, Any] | None = None
    ) -> bool:
        """
        Validate configuration for a specific upload type.

        Args:
            upload_type: Type of uploader to validate
            config: Configuration to validate (default: None)

        Returns:
            bool: True if configuration is valid, False otherwise

        Example:
            >>> is_valid = UploaderService.validate_upload_config(
            ...     "disk", {"overwrite": True}
            ... )
        """
        return UploaderFactory.validate_config(upload_type, config)
