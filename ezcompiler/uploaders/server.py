# ///////////////////////////////////////////////////////////////
# SERVER - Remote server uploader implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Server uploader - HTTP/HTTPS remote server upload handler for EzCompiler.

This module provides functionality for uploading files to remote servers
via HTTP/HTTPS POST requests, with support for authentication, retry logic,
and SSL verification.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Third-party imports
import requests

# Local imports
from ..core.exceptions import UploadError
from .base import BaseUploader

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ServerUploader(BaseUploader):
    """
    Uploader for server operations via HTTP/HTTPS.

    Handles uploading files to remote servers using HTTP POST requests with
    support for authentication, SSL verification, and automatic retry logic.

    Configuration keys:
        server_url (str): Base URL of the upload server
        username (str): Username for basic authentication (default: "")
        password (str): Password for basic authentication (default: "")
        api_key (str): API key for bearer token authentication (default: "")
        timeout (int|float): Request timeout in seconds (default: 30)
        verify_ssl (bool): Verify SSL certificates (default: True)
        chunk_size (int): Chunk size for uploads (default: 8192)
        retry_attempts (int): Number of retry attempts (default: 3)

    Example:
        >>> config = {"server_url": "https://example.com", "api_key": "abc123"}
        >>> uploader = ServerUploader(config)
        >>> uploader.upload(Path("file.zip"), "/uploads/file.zip")
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize the server uploader.

        Args:
            config: Optional configuration dictionary with server settings
        """
        default_config = {
            "server_url": "",
            "username": "",
            "password": "",
            "api_key": "",
            "timeout": 30,
            "verify_ssl": True,
            "chunk_size": 8192,
            "retry_attempts": 3,
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
        return "Server Uploader"

    def upload(self, source_path: Path, destination: str) -> None:
        """
        Upload a file to a remote server.

        Args:
            source_path: Path to the source file
            destination: Destination path on the server

        Raises:
            UploadError: If upload fails after all retry attempts

        Note:
            Only supports single files, not directories.
            Automatically retries on failure based on retry_attempts config.
        """
        try:
            self.validate_source_path(source_path)

            if not source_path.is_file():
                raise UploadError(
                    "Server uploader only supports single files, not directories"
                )

            self.log_upload_start(source_path, destination)

            # Retry logic
            for attempt in range(self.config["retry_attempts"]):
                try:
                    self._perform_upload(source_path, destination)
                    break
                except Exception as e:
                    if attempt == self.config["retry_attempts"] - 1:
                        raise
                    self._printer.warning(
                        f"⚠️ Upload attempt {attempt + 1} failed, retrying... ({e})"
                    )
                    self._logger.warning(
                        f"Upload attempt {attempt + 1} failed, retrying... ({e})"
                    )

            self.log_upload_success(source_path, destination)

        except Exception as e:
            self.log_upload_error(source_path, destination, str(e))
            raise UploadError(f"Server upload failed: {e}") from e

    def test_connection(self) -> bool:
        """
        Test the connection to the server.

        Returns:
            bool: True if connection is successful, False otherwise

        Note:
            Attempts to reach /health endpoint on the server.
        """
        try:
            test_url = f"{self.config['server_url'].rstrip('/')}/health"
            headers = self._prepare_headers()
            auth = self._prepare_auth()

            response = requests.get(
                test_url,
                headers=headers,
                auth=auth,
                timeout=self.config["timeout"],
                verify=self.config["verify_ssl"],
            )

            return response.ok
        except Exception:
            return False

    # ////////////////////////////////////////////////
    # PRIVATE METHODS
    # ////////////////////////////////////////////////

    def _perform_upload(self, source_path: Path, destination: str) -> None:
        """
        Perform the actual upload operation.

        Args:
            source_path: Source file path
            destination: Destination path on server

        Raises:
            UploadError: If server returns error response
        """
        upload_url = self._build_upload_url(destination)
        headers = self._prepare_headers()
        auth = self._prepare_auth()

        with open(source_path, "rb") as file:
            files = {"file": (source_path.name, file, "application/octet-stream")}
            data = {"destination": destination}

            response = requests.post(
                upload_url,
                files=files,
                data=data,
                headers=headers,
                auth=auth,
                timeout=self.config["timeout"],
                verify=self.config["verify_ssl"],
            )

        if not response.ok:
            raise UploadError(
                f"Server returned error {response.status_code}: {response.text}"
            )

    def _build_upload_url(self, _destination: str) -> str:
        """
        Build the complete upload URL.

        Args:
            _destination: Destination path (unused, for future extensions)

        Returns:
            str: Complete upload URL
        """
        base_url = self.config["server_url"].rstrip("/")
        return f"{base_url}/upload"

    def _prepare_headers(self) -> dict[str, str]:
        """
        Prepare HTTP headers for the upload request.

        Returns:
            dict[str, str]: Headers dictionary

        Note:
            Includes User-Agent and optional Bearer token authorization.
        """
        headers = {
            "User-Agent": "EzCompiler/2.1.4",
            "Accept": "application/json",
        }

        if self.config["api_key"]:
            headers["Authorization"] = f"Bearer {self.config['api_key']}"

        return headers

    def _prepare_auth(self) -> tuple[str, str] | None:
        """
        Prepare authentication for the upload request.

        Returns:
            tuple[str, str] | None: Basic auth tuple or None

        Note:
            Returns (username, password) tuple for basic auth if configured.
        """
        if self.config["username"] and self.config["password"]:
            return (self.config["username"], self.config["password"])
        return None

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def _validate_config(self) -> None:
        """
        Validate server uploader configuration.

        Raises:
            UploadError: If configuration is invalid

        Note:
            Validates required keys, URL format, and value types/ranges.
        """
        required_keys = [
            "server_url",
            "username",
            "password",
            "api_key",
            "timeout",
            "verify_ssl",
            "chunk_size",
            "retry_attempts",
        ]

        for key in required_keys:
            if key not in self.config:
                raise UploadError(f"Missing required configuration key: {key}")

        if not self.config["server_url"]:
            raise UploadError("server_url is required")

        if not self.config["server_url"].startswith(("http://", "https://")):
            raise UploadError("server_url must start with http:// or https://")

        if (
            not isinstance(self.config["timeout"], (int, float))
            or self.config["timeout"] <= 0
        ):
            raise UploadError("timeout must be a positive number")

        if (
            not isinstance(self.config["chunk_size"], int)
            or self.config["chunk_size"] <= 0
        ):
            raise UploadError("chunk_size must be a positive integer")

        if (
            not isinstance(self.config["retry_attempts"], int)
            or self.config["retry_attempts"] < 0
        ):
            raise UploadError("retry_attempts must be a non-negative integer")

        if not isinstance(self.config["verify_ssl"], bool):
            raise UploadError("verify_ssl must be a boolean")
