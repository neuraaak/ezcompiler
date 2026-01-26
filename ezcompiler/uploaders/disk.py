# ///////////////////////////////////////////////////////////////
# DISK - Local disk uploader implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Disk uploader - Local disk upload handler for EzCompiler.

This module provides functionality for uploading files and directories to
local disk locations, with support for backup creation, permission preservation,
and overwrite control.
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
from ..core.exceptions import UploadError
from .base import BaseUploader

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
        default_config = {
            "preserve_permissions": True,
            "overwrite": True,
            "create_backup": False,
        }

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
            self.validate_source_path(source_path)
            dest_path = Path(destination)
            self.log_upload_start(source_path, destination)

            # Create parent directories
            if source_path.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                dest_path.mkdir(parents=True, exist_ok=True)

            # Handle existing destination
            if not self.config["overwrite"] and dest_path.exists():
                if self.config["create_backup"]:
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

            self.log_upload_success(source_path, destination)

        except Exception as e:
            self.log_upload_error(source_path, destination, str(e))
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
        if self.config["preserve_permissions"]:
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
        if dest_path.exists() and self.config["overwrite"]:
            shutil.rmtree(dest_path)

        shutil.copytree(
            source_path,
            dest_path,
            dirs_exist_ok=self.config["overwrite"],
            copy_function=(
                shutil.copy2 if self.config["preserve_permissions"] else shutil.copy
            ),
        )

    def _create_backup(self, file_path: Path) -> None:
        """
        Create a backup of an existing file.

        Args:
            file_path: Path to file to backup

        Note:
            Appends .backup suffix, with incrementing numbers if needed.
        """
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        counter = 1

        # Find unique backup name
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{counter}")
            counter += 1

        shutil.copy2(file_path, backup_path)
        self._printer.info(f"📦 Backup created: {backup_path}")
        self._logger.info(f"Backup created: {backup_path}")

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
            if key not in self.config:
                raise UploadError(f"Missing required configuration key: {key}")

            if not isinstance(self.config[key], bool):
                raise UploadError(f"Configuration key '{key}' must be a boolean")
