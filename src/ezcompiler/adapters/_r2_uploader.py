# ///////////////////////////////////////////////////////////////
# R2_UPLOADER - Cloudflare R2 (S3-compatible) uploader implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""R2 uploader - bidirectional S3-compatible backend for the TUF update channel.

Credentials are read from environment variables only and are never logged
nor included in error messages. boto3 is imported lazily (extra ``[r2]``).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
from pathlib import Path
from typing import Any

# Local imports
from ..shared.exceptions import UploadError
from .base_uploader import BaseUploader

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class R2Uploader(BaseUploader):
    """Uploader for Cloudflare R2 (S3-compatible).

    Configuration keys:
        bucket (str): Target R2 bucket name (required).

    Environment variables (required, write credentials):
        R2_ENDPOINT or R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY.
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the R2 uploader and build the S3 client.

        Args:
            config: Configuration dictionary (requires ``bucket``).
        """
        super().__init__(config or {})
        self._bucket = self._config["bucket"]
        self._endpoint = self._resolve_endpoint()
        self._client = self._build_client()

    # ////////////////////////////////////////////////
    # PUBLIC METHODS
    # ////////////////////////////////////////////////

    def get_uploader_name(self) -> str:
        """Get the name of this uploader.

        Returns:
            str: Name of the uploader.
        """
        return "R2 Uploader"

    def upload(self, source_path: Path, destination: str) -> None:
        """Upload a file or directory tree under the ``destination`` prefix.

        For a directory, each file is uploaded with its POSIX path relative
        to ``source_path`` appended to the prefix. Metadata is uploaded last
        to keep the published tree TUF-consistent.

        Args:
            source_path: Path to the source file or directory.
            destination: Object key prefix under the bucket.

        Raises:
            UploadError: If any object upload fails.
        """
        try:
            self._validate_source_path(source_path)
            prefix = destination.strip("/")
            if source_path.is_file():
                self._put(source_path, f"{prefix}/{source_path.name}")
                return

            files = sorted(p for p in source_path.rglob("*") if p.is_file())
            # targets/zip d'abord, metadata en dernier (cohérence TUF)
            files.sort(key=lambda p: "metadata/" in p.as_posix())
            for file_path in files:
                rel = file_path.relative_to(source_path).as_posix()
                self._put(file_path, f"{prefix}/{rel}")
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"R2 upload failed: {e}") from e

    def download(self, remote_source: str, local_dir: Path) -> None:
        """Download every object under the ``remote_source`` prefix.

        Args:
            remote_source: Object key prefix to fetch.
            local_dir: Local directory to populate.

        Raises:
            UploadError: If a download fails.

        Note:
            An empty prefix (first run) is a no-op.
        """
        try:
            prefix = remote_source.strip("/")
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    rel = key[len(prefix) :].lstrip("/")
                    dest = self._safe_join(local_dir, rel)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    self._client.download_file(
                        Bucket=self._bucket, Key=key, Filename=str(dest)
                    )
        except Exception as e:
            raise UploadError(f"R2 download failed: {e}") from e

    # ////////////////////////////////////////////////
    # PRIVATE METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def _safe_join(root: Path, rel: str) -> Path:
        """Join ``rel`` under ``root``, rejecting path traversal.

        Object keys come from the remote bucket listing; a crafted key must
        never let the downloaded file escape ``root``.

        Raises:
            UploadError: If ``rel`` resolves outside ``root``.
        """
        root_resolved = root.resolve()
        candidate = (root / rel).resolve()
        if root_resolved != candidate and root_resolved not in candidate.parents:
            raise UploadError(f"Unsafe object key rejected: {rel}")
        return candidate

    def _put(self, source_path: Path, key: str) -> None:
        """Upload a single file to the bucket under ``key``."""
        self._client.upload_file(
            Filename=str(source_path), Bucket=self._bucket, Key=key
        )

    def _resolve_endpoint(self) -> str:
        """Resolve the R2 endpoint URL from env vars.

        Raises:
            UploadError: If neither R2_ENDPOINT nor R2_ACCOUNT_ID is set.
        """
        endpoint = os.environ.get("R2_ENDPOINT")
        if endpoint:
            return endpoint
        account = os.environ.get("R2_ACCOUNT_ID")
        if not account:
            raise UploadError("Missing R2_ENDPOINT or R2_ACCOUNT_ID env var")
        return f"https://{account}.r2.cloudflarestorage.com"

    def _build_client(self) -> Any:
        """Build the boto3 S3 client (lazy import, extra ``[r2]``)."""
        import boto3  # noqa: PLC0415  # ty: ignore[unresolved-import]  # pyright: ignore[reportMissingImports]

        return boto3.client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._require_env("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=self._require_env("R2_SECRET_ACCESS_KEY"),
            region_name="auto",
        )

    @staticmethod
    def _require_env(name: str) -> str:
        """Return the value of env var ``name`` or raise.

        Raises:
            UploadError: If the variable is missing or empty.
        """
        value = os.environ.get(name)
        if not value:
            raise UploadError(f"Missing required env var: {name}")
        return value

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def _validate_config(self) -> None:
        """Validate R2 uploader configuration.

        Raises:
            UploadError: If the required ``bucket`` key is missing.
        """
        if not self._config.get("bucket"):
            raise UploadError("Missing required configuration key: bucket")
