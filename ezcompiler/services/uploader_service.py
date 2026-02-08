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
from typing import Any, Literal

# Local imports
from ..protocols.uploader_factory import UploaderFactory
from ..shared.exceptions import UploadError
from ..utils.validators import validate_upload_structure

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

UploadType = Literal["disk", "server"]

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

            # Create uploader and perform upload
            uploader = UploaderFactory.create_uploader(upload_type, config)
            uploader.upload(source_path=source_path, destination=destination)
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Upload failed: {str(e)}") from e

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
