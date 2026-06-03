# ///////////////////////////////////////////////////////////////
# BASE_UPLOADER - Abstract base uploader interface
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base uploader - Abstract base class for uploader implementations.

This module defines the interface and common functionality for all uploaders,
providing validation and contract enforcement for upload operations.

Note: Protocols layer should not perform logging directly. Logging is handled
by the service layer that orchestrates upload operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

# Local imports
from ..shared.exceptions import UploadError

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


# TODO [AUDIT P3]: migrer ABC → Protocol (typing.Protocol) pour aligner avec l'architecture hexagonale
# Même approche que BaseCompiler — créer UploaderPort(Protocol) dans adapters/ports.py.
class BaseUploader(ABC):
    """
    Abstract base class for uploaders.

    Defines the interface that all uploaders must implement and provides
    common functionality for upload operations and validation.

    Attributes:
        _config: Configuration dictionary for the uploader

    Example:
        >>> class MyUploader(BaseUploader):
        ...     def upload(self, source_path: Path, destination: str) -> None:
        ...         # Implementation
        ...         pass
        ...     def get_uploader_name(self) -> str:
        ...         return "My Uploader"
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize the uploader with configuration.

        Args:
            config: Configuration dictionary (default: None)

        Note:
            Subclasses should call super().__init__(config) to initialize
            configuration and validation.
        """
        self._config = config or {}
        self._validate_config()

    # ////////////////////////////////////////////////
    # ABSTRACT METHODS
    # ////////////////////////////////////////////////

    @abstractmethod
    def upload(self, source_path: Path, destination: str) -> None:
        """
        Upload a file or directory to the destination.

        Args:
            source_path: Path to the source file or directory
            destination: Destination path or URL

        Raises:
            UploadError: If upload fails

        Note:
            Subclasses must implement this method to define upload behavior.
        """

    @abstractmethod
    def get_uploader_name(self) -> str:
        """
        Get the name of this uploader.

        Returns:
            str: Human-readable name of the uploader

        Note:
            Used for identification purposes.
        """

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def _validate_config(self) -> None:  # noqa: B027
        """
        Validate uploader configuration.

        Base implementation does nothing. Subclasses should override this
        method to perform specific validation for their configuration.

        Raises:
            UploadError: If configuration is invalid (in subclasses)

        Note:
            This method is intentionally empty in the base class.
        """
        # Base implementation intentionally empty - subclasses should override

    def _validate_source_path(self, source_path: Path) -> None:
        """
        Validate that the source path exists and is accessible.

        Args:
            source_path: Path to validate

        Raises:
            UploadError: If source path is invalid

        Note:
            Validation is handled at protocol level to keep this port independent
            from uploader utility helpers.
        """
        if not source_path.exists():
            raise UploadError(f"Source path does not exist: {source_path}")
        if not source_path.is_file() and not source_path.is_dir():
            raise UploadError(f"Source path is not a file or directory: {source_path}")
