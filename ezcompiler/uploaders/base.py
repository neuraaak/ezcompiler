# ///////////////////////////////////////////////////////////////
# BASE - Abstract base uploader interface
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base uploader - Abstract base class for uploader implementations.

This module defines the interface and common functionality for all uploaders,
providing logging, validation, and contract enforcement for upload operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Third-party imports
from ezpl import Ezpl

# Local imports
from ..core.exceptions import UploadError

# Type checking imports
if TYPE_CHECKING:
    from ezpl import EzLogger, EzPrinter

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class BaseUploader(ABC):
    """
    Abstract base class for uploaders.

    Defines the interface that all uploaders must implement and provides
    common functionality for upload operations, logging, and validation.

    Attributes:
        config: Configuration dictionary for the uploader
        _ezpl: Ezpl instance for logging
        _printer: Printer instance for console output
        _logger: Logger instance for file logging

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
            logging and configuration.
        """
        self.config = config or {}
        self._validate_config()
        self._ezpl = Ezpl(log_file=Path("ezcompiler.log"))
        self._printer: EzPrinter = self._ezpl.get_printer()
        self._logger: EzLogger = self._ezpl.get_logger()

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
            Used for logging and identification purposes.
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

    def validate_source_path(self, source_path: Path) -> None:
        """
        Validate that the source path exists and is accessible.

        Args:
            source_path: Path to validate

        Raises:
            UploadError: If source path is invalid
        """
        if not source_path.exists():
            raise UploadError(f"Source path does not exist: {source_path}")

        if not source_path.is_file() and not source_path.is_dir():
            raise UploadError(
                f"Source path is neither file nor directory: {source_path}"
            )

    # ////////////////////////////////////////////////
    # LOGGING METHODS
    # ////////////////////////////////////////////////

    def log_upload_start(self, source_path: Path, destination: str) -> None:
        """
        Log the start of an upload operation.

        Args:
            source_path: Source file/directory path
            destination: Destination path or URL
        """
        self._printer.info(f"📤 Starting upload: {source_path} -> {destination}")
        self._logger.info(f"Starting upload: {source_path} -> {destination}")

    def log_upload_success(self, source_path: Path, destination: str) -> None:
        """
        Log successful upload completion.

        Args:
            source_path: Source file/directory path
            destination: Destination path or URL
        """
        self._printer.success(f"✅ Upload completed: {source_path} -> {destination}")
        self._logger.info(f"Upload completed: {source_path} -> {destination}")

    def log_upload_error(self, source_path: Path, destination: str, error: str) -> None:
        """
        Log upload error.

        Args:
            source_path: Source file/directory path
            destination: Destination path or URL
            error: Error message
        """
        self._printer.error(f"❌ Upload failed: {source_path} -> {destination}")
        self._printer.error(f"   Error: {error}")
        self._logger.error(f"Upload failed: {source_path} -> {destination}")
        self._logger.error(f"Error: {error}")
