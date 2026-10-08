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
from typing import TYPE_CHECKING, Any, Literal, cast

from ..adapters import ReleaserFactory
from ..shared.exceptions import ReleaseError
from .tuf_service import TufService
from .uploader_service import UploaderService

if TYPE_CHECKING:
    from .._types import ReleaserPort

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
        required: bool = False,
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
            required: Mark the version as mandatory for clients.

        Returns:
            Path: The local ``repository/`` tree path.

        Raises:
            ValueError: When publish=True but upload_type or destination is missing.
            ReleaseError: When the version is not above a withdrawn version, or
                when release packaging or publishing fails.
        """
        if pull_before and upload_type and destination:
            UploaderService.download(
                remote_source=destination,
                upload_type=cast(Literal["disk", "server", "r2"], upload_type),
                destination_local=repo_dir,
                upload_config=upload_config,
            )

        # After the pull: withdrawn.json travels with the remote tree.
        TufService.ensure_releasable(repo_dir, version)
        # First release after a withdrawal: full archive only, a patch
        # would start from an archive the withdrawn clients do not have.
        patch = not TufService.needs_full_archive(repo_dir, app_name)

        releaser: ReleaserPort = ReleaserFactory.create_releaser(
            release_type, releaser_config
        )
        repository_path = releaser.release(
            bundle_dir=bundle_dir,
            app_name=app_name,
            version=version,
            repo_dir=repo_dir,
            patch=patch,
            required=required,
        )

        if not publish:
            return repository_path

        if not upload_type or not destination:
            raise ValueError("publish=True requires both upload_type and destination")

        try:
            # Never the raw tree: the default keystore lives under repo_dir.
            with UploaderService.staged_tuf_tree(
                repository_path, keys_dir=(releaser_config or {}).get("keys_dir")
            ) as staged:
                UploaderService.upload(
                    source_path=staged,
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
        """Create the releaser through the factory and delegate to init_keys.

        Returns True if the init ran, False if it was already present (skip).
        """
        releaser: ReleaserPort = ReleaserFactory.create_releaser(
            release_type, releaser_config
        )
        return releaser.init_keys(
            app_name=app_name, repo_dir=repo_dir, keys_dir=keys_dir
        )

    @staticmethod
    def refresh_expiration(
        app_name: str,
        repo_dir: Path,
        keys_dir: Path,
        *,
        roles: tuple[str, ...] = ("targets", "snapshot", "timestamp"),
        days: int | None = None,
        release_type: str = "tufup",
        releaser_config: dict[str, Any] | None = None,
    ) -> Path:
        """Re-sign the metadata to push back expiration without a new release.

        Native tufup keep-alive for projects updated irregularly.

        Returns the local TUF repo directory.
        """
        releaser: ReleaserPort = ReleaserFactory.create_releaser(
            release_type, releaser_config
        )
        return releaser.refresh_expiration(
            app_name=app_name,
            repo_dir=repo_dir,
            keys_dir=keys_dir,
            roles=roles,
            days=days,
        )
