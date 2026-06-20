# ///////////////////////////////////////////////////////////////
# UPLOADER_FACTORY - Uploader factory for creating uploader instances
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Uploader factory - Factory for creating uploader instances.

This module provides a centralized factory for creating and configuring
uploader instances based on type and configuration, with support for
validation and discovery of supported types.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Local imports
from ..shared.exceptions import UploadError
from ..types import UploaderPort
from ..utils import UploaderUtils
from ._disk_uploader import DiskUploader
from ._server_uploader import ServerUploader

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class UploaderFactory:
    """
    Factory class for creating uploader instances.

    Provides a centralized way to create and configure uploader instances
    based on type specification, with support for validation and type discovery.

    Example:
        >>> uploader = UploaderFactory.create_uploader("disk", {"overwrite": True})
        >>> types = UploaderFactory.get_supported_types()
        >>> print(types)
        ['disk', 'server']
    """

    # ////////////////////////////////////////////////
    # FACTORY METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def create_uploader(
        upload_type: str, config: dict[str, Any] | None = None
    ) -> UploaderPort:
        """
        Create an uploader instance based on the specified type.

        Args:
            upload_type: Type of uploader ("disk" or "server")
            config: Configuration dictionary for the uploader (default: None)

        Returns:
            UploaderPort: Configured uploader instance (satisfies the Port)

        Raises:
            UploadError: If upload type is not supported

        Example:
            >>> disk_uploader = UploaderFactory.create_uploader("disk")
            >>> server_uploader = UploaderFactory.create_uploader(
            ...     "server", {"server_url": "https://example.com"}
            ... )
        """
        upload_type = upload_type.lower()

        # Validate upload type using UploaderUtils
        UploaderUtils.validate_upload_type(upload_type)

        if upload_type == "disk":
            return DiskUploader(config)
        elif upload_type == "server":
            return ServerUploader(config)
        else:
            # This should not happen due to validation above, but kept for safety
            raise UploadError(f"Unsupported upload type: {upload_type}")

    @staticmethod
    def create_from_config(config: dict[str, Any]) -> UploaderPort:
        """
        Create an uploader instance from a configuration dictionary.

        Args:
            config: Configuration dictionary containing:
                - type: Upload type ("disk" or "server")
                - config: Uploader-specific configuration (optional)

        Returns:
            UploaderPort: Configured uploader instance (satisfies the Port)

        Raises:
            UploadError: If configuration is invalid or type is missing

        Example:
            >>> config = {
            ...     "type": "disk",
            ...     "config": {"overwrite": True}
            ... }
            >>> uploader = UploaderFactory.create_from_config(config)
        """
        if "type" not in config:
            raise UploadError("Upload type not specified in configuration")

        upload_type = config["type"]
        uploader_config = config.get("config", {})

        return UploaderFactory.create_uploader(upload_type, uploader_config)

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
            >>> types = UploaderFactory.get_supported_types()
            >>> print(types)
            ['disk', 'server']
        """
        return ["disk", "server"]

    @staticmethod
    def validate_config(upload_type: str, config: dict[str, Any] | None = None) -> bool:
        """
        Validate configuration for a specific upload type.

        Args:
            upload_type: Type of uploader to validate
            config: Configuration to validate (default: None)

        Returns:
            bool: True if configuration is valid, False otherwise

        Note:
            Creates a temporary uploader instance to test configuration validity.

        Example:
            >>> is_valid = UploaderFactory.validate_config("disk", {"overwrite": True})
            >>> print(is_valid)
            True
        """
        try:
            UploaderFactory.create_uploader(upload_type, config)
            return True
        except Exception:
            return False
