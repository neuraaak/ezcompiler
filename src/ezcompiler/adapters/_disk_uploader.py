# ///////////////////////////////////////////////////////////////
# DISK_UPLOADER - Local disk uploader implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Disk uploader - Local disk upload handler for EzCompiler.

This module provides functionality for uploading files and directories to
local disk locations, with support for backup creation, permission preservation,
and overwrite control.

Note: Protocols layer should not perform logging directly. Logging is handled
by the service layer that orchestrates upload operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import contextlib
import shutil
from pathlib import Path
from typing import Any

# Local imports
from ..shared.exceptions import UploadError
from ..utils import FileUtils, UploaderUtils
from .base_uploader import BaseUploader

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class DiskUploader(BaseUploader):
    """
    Uploader for local disk operations.

    Handles copying files and directories to local disk locations with
    configurable behavior for permissions, overwrites, and backups.

    Configuration keys:
        preserve_permissions (bool): Preserve file permissions (default: True)
        overwrite (bool): Allow overwriting existing files (default: True)
        create_backup (bool): Create backup before overwrite (default: False)

    Example:
        >>> config = {"preserve_permissions": True, "overwrite": True}
        >>> uploader = DiskUploader(config)
        >>> uploader.upload(Path("source.zip"), "/path/to/destination.zip")
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize the disk uploader.

        Args:
            config: Optional configuration dictionary with keys:
                - preserve_permissions (bool): Preserve file permissions
                - overwrite (bool): Allow overwriting existing files
                - create_backup (bool): Create backup before overwrite
        """
        default_config = UploaderUtils.get_default_disk_config()

        if config:
            default_config.update(config)

        super().__init__(default_config)

    # ////////////////////////////////////////////////
    # PUBLIC METHODS
    # ////////////////////////////////////////////////

    def get_uploader_name(self) -> str:
        """
        Get the name of this uploader.

        Returns:
            str: Name of the uploader
        """
        return "Disk Uploader"

    def upload(self, source_path: Path, destination: str) -> None:
        """
        Upload a file or directory to a local disk location.

        Args:
            source_path: Path to the source file or directory
            destination: Destination path on local disk

        Raises:
            UploadError: If upload fails

        Note:
            Creates parent directories automatically if they don't exist.
        """
        try:
            self._validate_source_path(source_path)
            dest_path = Path(destination)

            # For file uploads, treat destination as a directory and
            # preserve the source filename (e.g., "releases/Nuitka" + "build.zip"
            # -> "releases/Nuitka/build.zip")
            if source_path.is_file():
                FileUtils.create_directory_if_not_exists(dest_path)
                dest_path = dest_path / source_path.name
            else:
                FileUtils.create_directory_if_not_exists(dest_path)

            # Handle existing destination
            if not self._config["overwrite"] and dest_path.exists():
                if self._config["create_backup"]:
                    self._create_backup(dest_path)
                else:
                    raise UploadError(
                        f"Destination already exists and overwrite is disabled: {dest_path}"
                    )

            # Perform upload
            if source_path.is_file():
                self._upload_file(source_path, dest_path)
            else:
                self._upload_directory(source_path, dest_path)

        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Disk upload failed: {e}") from e

    # ////////////////////////////////////////////////
    # PRIVATE METHODS
    # ////////////////////////////////////////////////

    def _upload_file(self, source_path: Path, dest_path: Path) -> None:
        """
        Upload a single file.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Note:
            Uses copy2 to preserve metadata, then optionally preserves permissions.
        """
        shutil.copy2(source_path, dest_path)

        # Preserve permissions if configured
        if self._config["preserve_permissions"]:
            with contextlib.suppress(OSError, AttributeError):
                shutil.copystat(source_path, dest_path)

    def _upload_directory(self, source_path: Path, dest_path: Path) -> None:
        """
        Upload a directory recursively.

        Args:
            source_path: Source directory path
            dest_path: Destination directory path

        Note:
            Removes destination if it exists and overwrite is enabled.
        """
        if dest_path.exists() and self._config["overwrite"]:
            shutil.rmtree(dest_path)

        shutil.copytree(
            source_path,
            dest_path,
            dirs_exist_ok=self._config["overwrite"],
            copy_function=(
                shutil.copy2 if self._config["preserve_permissions"] else shutil.copy
            ),
        )

    def _create_backup(self, file_path: Path) -> None:
        """
        Create a backup of an existing file.

        Args:
            file_path: Path to file to backup

        Note:
            Uses UploaderUtils to generate unique backup path.
        """
        backup_path = UploaderUtils.generate_backup_path(file_path)
        shutil.copy2(file_path, backup_path)

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def _validate_config(self) -> None:
        """
        Validate disk uploader configuration.

        Raises:
            UploadError: If configuration is invalid

        Note:
            Ensures all required boolean flags are present and valid.
        """
        required_keys = ["preserve_permissions", "overwrite", "create_backup"]

        for key in required_keys:
            if key not in self._config:
                raise UploadError(f"Missing required configuration key: {key}")

            if not isinstance(self._config[key], bool):
                raise UploadError(f"Configuration key '{key}' must be a boolean")
