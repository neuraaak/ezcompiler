# ///////////////////////////////////////////////////////////////
# UPLOADER_UTILS - Uploader-specific utility functions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Uploader utilities - Uploader-specific utility functions for EzCompiler.

This module provides specialized utility functions for uploader operations,
including source path validation, configuration validation, and backup
operations. Uses thematic utils (FileUtils, ValidationUtils) internally.

Utils layer can only use DEBUG and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Local imports
from ..shared.exceptions.utils import (
    ServerConfigError,
    SourcePathError,
    UploaderTypeError,
)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class UploaderUtils:
    """
    Utility class for uploader-specific operations.

    Provides static methods for uploader-related tasks such as source path
    validation, configuration validation, and backup operations.
    Uses thematic utils (FileUtils) internally.

    Example:
        >>> UploaderUtils.validate_source_path(Path("file.zip"))
        >>> UploaderUtils.validate_upload_type("disk")
        >>> backup_path = UploaderUtils.generate_backup_path(Path("file.zip"))
    """

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_source_path(source_path: Path) -> None:
        """
        Validate that the source path exists and is accessible.

        Args:
            source_path: Path to validate

        Raises:
            SourcePathError: If source path is invalid or inaccessible

        Note:
            Uses FileUtils for file/directory existence checks.

        Example:
            >>> UploaderUtils.validate_source_path(Path("file.zip"))
        """
        if not source_path.exists():
            raise SourcePathError(f"Source path does not exist: {source_path}")

        if not source_path.is_file() and not source_path.is_dir():
            raise SourcePathError(
                f"Source path is neither file nor directory: {source_path}"
            )

    @staticmethod
    def validate_upload_type(upload_type: str) -> None:
        """
        Validate upload type string.

        Args:
            upload_type: Upload type to validate

        Raises:
            UploaderTypeError: If upload type is not supported

        Example:
            >>> UploaderUtils.validate_upload_type("disk")
            >>> UploaderUtils.validate_upload_type("invalid")
            UploaderTypeError: Unsupported upload type: invalid
        """
        valid_types = ["disk", "server"]
        if upload_type.lower() not in valid_types:
            raise UploaderTypeError(f"Unsupported upload type: {upload_type}")

    @staticmethod
    def validate_server_url(server_url: str) -> None:
        """
        Validate server URL format.

        Args:
            server_url: Server URL to validate

        Raises:
            ServerConfigError: If server URL is invalid

        Example:
            >>> UploaderUtils.validate_server_url("https://example.com")
            >>> UploaderUtils.validate_server_url("invalid")
            ServerConfigError: server_url must start with http:// or https://
        """
        if not server_url:
            raise ServerConfigError("server_url is required")

        if not server_url.startswith(("http://", "https://")):
            raise ServerConfigError("server_url must start with http:// or https://")

    # ////////////////////////////////////////////////
    # BACKUP METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def generate_backup_path(file_path: Path) -> Path:
        """
        Generate a unique backup path for a file.

        Args:
            file_path: Path to file that needs backup

        Returns:
            Path: Unique backup path (with .backup suffix and counter if needed)

        Example:
            >>> backup = UploaderUtils.generate_backup_path(Path("file.zip"))
            >>> print(backup)
            file.zip.backup
        """
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        counter = 1

        # Find unique backup name
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{counter}")
            counter += 1

        return backup_path

    # ////////////////////////////////////////////////
    # CONFIGURATION HELPERS
    # ////////////////////////////////////////////////

    @staticmethod
    def get_default_disk_config() -> dict[str, Any]:
        """
        Get default configuration for disk uploader.

        Returns:
            dict[str, Any]: Default disk uploader configuration

        Example:
            >>> config = UploaderUtils.get_default_disk_config()
            >>> print(config)
            {'preserve_permissions': True, 'overwrite': True, 'create_backup': False}
        """
        return {
            "preserve_permissions": True,
            "overwrite": True,
            "create_backup": False,
        }

    @staticmethod
    def get_default_server_config() -> dict[str, Any]:
        """
        Get default configuration for server uploader.

        Returns:
            dict[str, Any]: Default server uploader configuration

        Example:
            >>> config = UploaderUtils.get_default_server_config()
            >>> print(config)
            {'server_url': '', 'username': '', 'password': '', ...}
        """
        return {
            "server_url": "",
            "username": "",
            "password": "",  # nosec B105 - placeholder vide, pas un secret en dur
            "api_key": "",
            "timeout": 30,
            "verify_ssl": True,
            "chunk_size": 8192,
            "retry_attempts": 3,
        }
