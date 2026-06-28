# ///////////////////////////////////////////////////////////////
# RELEASE_SERVICE - Secure-release orchestration service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Release service - Orchestrates secure-release packaging.

Builds a signed TUF repository locally via a releaser adapter, then OPTIONALLY
delegates the remote transfer of that repository tree to the existing
``UploaderService`` (disk/server). Release packaging and transfer stay
separate concerns.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from pathlib import Path
from typing import Any, Literal, cast

from ..adapters import ReleaserFactory
from ..shared.exceptions import ReleaseError
from .uploader_service import UploaderService

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ReleaseService:
    """Service orchestrating secure-release packaging and publication."""

    # ------------------------------------------------
    # RELEASE METHODS
    # ------------------------------------------------

    @staticmethod
    def release_and_publish(
        bundle_dir: Path,
        app_name: str,
        version: str,
        repo_dir: Path,
        *,
        release_type: str = "tufup",
        publish: bool = False,
        pull_before: bool = False,
        upload_type: str | None = None,
        destination: str | None = None,
        releaser_config: dict[str, Any] | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> Path:
        """Build the local TUF repo, then optionally publish it.

        Args:
            bundle_dir: Directory containing the compiled application.
            app_name: Application name (used by tufup to name bundles).
            version: Application version string.
            repo_dir: Root directory for the local TUF repository tree.
            release_type: Release backend to use (default: "tufup").
            publish: When True, transfer the repository/ tree via an uploader.
            pull_before: When True, download the current remote tree into
                ``repo_dir`` before releasing (R2 source-of-truth cycle).
                Requires upload_type and destination.
            upload_type: Upload backend ("disk" or "server"). Required when publish=True.
            destination: Upload destination path or URL. Required when publish=True.
            releaser_config: Extra config forwarded to the releaser adapter.
            upload_config: Extra config forwarded to the uploader adapter.

        Returns:
            Path: The local ``repository/`` tree path.

        Raises:
            ValueError: When publish=True but upload_type or destination is missing.
            ReleaseError: When release packaging or publishing fails.
        """
        if pull_before and upload_type and destination:
            UploaderService.download(
                remote_source=destination,
                upload_type=cast(Literal["disk", "server", "r2"], upload_type),
                destination_local=repo_dir,
                upload_config=upload_config,
            )

        releaser = ReleaserFactory.create_releaser(release_type, releaser_config)
        repository_path = releaser.release(
            bundle_dir=bundle_dir,
            app_name=app_name,
            version=version,
            repo_dir=repo_dir,
        )

        if not publish:
            return repository_path

        if not upload_type or not destination:
            raise ValueError("publish=True requires both upload_type and destination")

        try:
            UploaderService.upload(
                source_path=repository_path,
                upload_type=cast(Literal["disk", "server", "r2"], upload_type),
                destination=destination,
                upload_config=upload_config,
            )
        except Exception as exc:
            raise ReleaseError(f"Publishing release repository failed: {exc}") from exc

        return repository_path

    @staticmethod
    def init_release(
        app_name: str,
        repo_dir: Path,
        keys_dir: Path,
        *,
        release_type: str = "tufup",
        releaser_config: dict[str, Any] | None = None,
    ) -> bool:
        """Crée le releaser via la factory et délègue à init_keys.

        Returns True si init effectuée, False si déjà présente (skip).
        """
        releaser = ReleaserFactory.create_releaser(release_type, releaser_config)
        return releaser.init_keys(
            app_name=app_name, repo_dir=repo_dir, keys_dir=keys_dir
        )
