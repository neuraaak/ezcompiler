# ///////////////////////////////////////////////////////////////
# SERVER_UPLOADER - Remote server uploader implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Server uploader - HTTP/HTTPS remote server upload handler for EzCompiler.

This module provides functionality for uploading files to remote servers
via HTTP/HTTPS POST requests, with support for authentication, retry logic,
and SSL verification.

Note: Protocols layer should not perform logging directly. Logging is handled
by the service layer that orchestrates upload operations.
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
from .._version import __version__
from ..shared.exceptions import UploadError
from ..utils import UploaderUtils
from .base_uploader import BaseUploader

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
        proxies (dict): Proxy URLs keyed by scheme, e.g.
            ``{"http": "http://proxy:3128", "https": "http://proxy:3128"}`` (default: {})
        extra_headers (dict): Additional HTTP headers merged into every request (default: {})
        cert (str | tuple | None): Client certificate for mTLS — path to a .pem file,
            or a ``(certfile, keyfile)`` tuple (default: None)

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
        default_config = UploaderUtils.get_default_server_config()

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
        Upload a file or a directory tree to a remote server.

        For directories, walks recursively and POSTs each file using its
        POSIX path relative to ``source_path`` as the server destination.

        Args:
            source_path: Path to the source file or directory
            destination: Destination path on the server (single-file uploads)

        Raises:
            UploadError: If any file fails after all retry attempts.

        Note:
            Automatically retries on failure based on retry_attempts config.
        """
        try:
            self._validate_source_path(source_path)

            if source_path.is_dir():
                for file_path in sorted(source_path.rglob("*")):
                    if file_path.is_file():
                        rel = file_path.relative_to(source_path).as_posix()
                        self._upload_single_file_with_retry(file_path, rel)
                return

            self._upload_single_file_with_retry(source_path, destination)

        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Server upload failed: {e}") from e

    def download(self, remote_source: str, local_dir: Path) -> None:
        """
        Fetch the current TUF tree from ``remote_source`` (metadata-driven).

        Reads the role metadata by known names, then the targets listed in
        ``targets.json``. A 404 on ``timestamp.json`` means the channel is
        empty (first run) -> no-op.

        Args:
            remote_source: Base read URL of the update channel.
            local_dir: Local directory to populate with the TUF tree.

        Raises:
            UploadError: On any non-404 transport failure.
        """
        import json  # noqa: PLC0415

        base = remote_source.rstrip("/")
        try:
            ts = self._get(f"{base}/metadata/timestamp.json")
            if ts is None:
                return  # premier run : canal vide
            self._save(local_dir / "metadata" / "timestamp.json", ts)

            for role in ("snapshot.json", "root.json", "targets.json"):
                body = self._get(f"{base}/metadata/{role}")
                if body is not None:
                    self._save(local_dir / "metadata" / role, body)

            targets_path = local_dir / "metadata" / "targets.json"
            if targets_path.exists():
                doc = json.loads(targets_path.read_text())
                targets_root = local_dir / "targets"
                for name in doc.get("signed", {}).get("targets", {}):
                    dest = self._safe_join(targets_root, name)
                    body = self._get(f"{base}/targets/{name}")
                    if body is not None:
                        self._save(dest, body)
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Server download failed: {e}") from e

    def _get(self, url: str) -> bytes | None:
        """GET ``url``; return bytes, or None on 404.

        Raises:
            UploadError: On any non-404 error response.
        """
        response = requests.get(  # nosec B113 - timeout fourni et validé > 0 dans _validate_config
            url,
            headers=self._prepare_headers(),
            auth=self._prepare_auth(),
            timeout=self._config["timeout"],
            verify=self._config["verify_ssl"],
            proxies=self._config["proxies"] or None,
            cert=self._config["cert"],
        )
        if response.status_code == 404:
            return None
        if not response.ok:
            raise UploadError(f"Server returned error {response.status_code} for {url}")
        return response.content

    @staticmethod
    def _safe_join(root: Path, name: str) -> Path:
        """Join ``name`` under ``root``, rejecting path traversal.

        Target names come from a remote, not-yet-verified ``targets.json``;
        a crafted ``name`` (``../`` or absolute) must never escape ``root``.

        Raises:
            UploadError: If ``name`` resolves outside ``root``.
        """
        root_resolved = root.resolve()
        candidate = (root / name).resolve()
        if root_resolved != candidate and root_resolved not in candidate.parents:
            raise UploadError(f"Unsafe target name rejected: {name}")
        return candidate

    @staticmethod
    def _save(path: Path, content: bytes) -> None:
        """Write ``content`` to ``path``, creating parent directories."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def _upload_single_file_with_retry(
        self, source_path: Path, destination: str
    ) -> None:
        """POST a single file, retrying per ``retry_attempts``.

        Raises:
            UploadError: If the file fails after all retry attempts.
        """
        last_error = None
        for attempt in range(self._config["retry_attempts"]):
            try:
                self._perform_upload(source_path, destination)
                return
            except Exception as e:
                last_error = e
                if attempt == self._config["retry_attempts"] - 1:
                    break
        raise UploadError(
            f"Server upload failed after {self._config['retry_attempts']} "
            f"attempts: {last_error}"
        ) from last_error

    def _test_connection(self) -> bool:
        """
        Test the connection to the server.

        Returns:
            bool: True if connection is successful, False otherwise

        Note:
            Attempts to reach /health endpoint on the server.
        """
        try:
            test_url = f"{self._config['server_url'].rstrip('/')}/health"
            headers = self._prepare_headers()
            auth = self._prepare_auth()

            response = requests.get(  # nosec B113 - timeout fourni et validé > 0 dans _validate_config
                test_url,
                headers=headers,
                auth=auth,
                timeout=self._config["timeout"],
                verify=self._config["verify_ssl"],
                proxies=self._config["proxies"] or None,
                cert=self._config["cert"],
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

            response = requests.post(  # nosec B113 - timeout fourni et validé > 0 dans _validate_config
                upload_url,
                files=files,
                data=data,
                headers=headers,
                auth=auth,
                timeout=self._config["timeout"],
                verify=self._config["verify_ssl"],
                proxies=self._config["proxies"] or None,
                cert=self._config["cert"],
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
        base_url = self._config["server_url"].rstrip("/")
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
            "User-Agent": f"EzCompiler/{__version__}",
            "Accept": "application/json",
        }

        if self._config["api_key"]:
            headers["Authorization"] = f"Bearer {self._config['api_key']}"

        headers.update(self._config.get("extra_headers", {}))
        return headers

    def _prepare_auth(self) -> tuple[str, str] | None:
        """
        Prepare authentication for the upload request.

        Returns:
            tuple[str, str] | None: Basic auth tuple or None

        Note:
            Returns (username, password) tuple for basic auth if configured.
        """
        if self._config["username"] and self._config["password"]:
            return (self._config["username"], self._config["password"])
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
            Uses UploaderUtils for URL validation.
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
            "proxies",
            "extra_headers",
            "cert",
        ]

        for key in required_keys:
            if key not in self._config:
                raise UploadError(f"Missing required configuration key: {key}")

        # Validate server URL using UploaderUtils
        UploaderUtils.validate_server_url(self._config["server_url"])

        if (
            not isinstance(self._config["timeout"], (int, float))
            or self._config["timeout"] <= 0
        ):
            raise UploadError("timeout must be a positive number")

        if (
            not isinstance(self._config["chunk_size"], int)
            or self._config["chunk_size"] <= 0
        ):
            raise UploadError("chunk_size must be a positive integer")

        if (
            not isinstance(self._config["retry_attempts"], int)
            or self._config["retry_attempts"] < 1
        ):
            raise UploadError("retry_attempts must be an integer >= 1")

        if not isinstance(self._config["verify_ssl"], bool):
            raise UploadError("verify_ssl must be a boolean")

        if not isinstance(self._config["proxies"], dict):
            raise UploadError("proxies must be a dict")

        if not isinstance(self._config["extra_headers"], dict):
            raise UploadError("extra_headers must be a dict")

        cert = self._config["cert"]
        if cert is not None and not isinstance(cert, (str, tuple)):
            raise UploadError(
                "cert must be a path string or a (certfile, keyfile) tuple"
            )
