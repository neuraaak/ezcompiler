# ///////////////////////////////////////////////////////////////
# PUBLISH_SERVICE - Publication orchestration (update tree & release)
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Publish service - Orchestrates the two publication paths.

``publish_update`` transfers the signed TUF tree; ``publish_release``
either creates a platform release (github) or copies the assets to a file
destination (disk/server/r2). This module owns the routing between the two
and is the only place that decides it.

The human-facing confirmation lives in ``interfaces/``, never here: a
service must not read stdin.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Third-party imports
# Local imports
from .._types import PublisherPort
from ..adapters import PublisherFactory
from ..shared import ReleasePreflight
from ..shared._compiler_config import _OWNER_REPO_RE
from ..shared.exceptions import PublishError, UploadError
from .pipeline_service import PipelineService
from .tuf_service import TufService
from .uploader_service import UploaderService

if TYPE_CHECKING:
    from ..shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_PLATFORMS: tuple[str, ...] = ("github", "gitlab")

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class PublishService:
    """Orchestrates TUF-tree and release publication."""

    # ////////////////////////////////////////////////
    # ROUTING
    # ////////////////////////////////////////////////

    @staticmethod
    def resolve_publisher(
        config: CompilerConfig, release_destination: str | None = None
    ) -> PublisherPort | None:
        """Return a publisher for platform destinations, else ``None``.

        Args:
            config: Current configuration.
            release_destination: Override for ``config.release_destination``.

        Returns:
            PublisherPort | None: ``None`` when the destination is a file
                backend (disk/server/r2) and the uploader path applies.

        Raises:
            PublisherTypeError: If the platform is not supported.
            PublishError: If ``release_endpoint`` is not an ``owner/repo``.
        """
        dest = release_destination or config.release_destination
        if dest not in _PLATFORMS:
            return None
        endpoint = config.release_endpoint
        # The config only validates the owner/repo form when
        # release_destination already names a platform: an override
        # (-rld github) on a disk/r2 config would bring a path or a bucket
        # through --repo.
        if endpoint and not _OWNER_REPO_RE.fullmatch(endpoint):
            raise PublishError(
                f"release_endpoint '{endpoint}' is not an 'owner/repo' "
                f"repository usable for '{dest}' publication."
            )
        return PublisherFactory.create_publisher(
            dest, {"repo": endpoint} if endpoint else None
        )

    @staticmethod
    def preflight_release(
        config: CompilerConfig,
        *,
        tag: str,
        release_destination: str | None = None,
    ) -> ReleasePreflight:
        """Run every pre-publication check and return the recap to display.

        The routing decision and the ``PublisherPort`` lifecycle both stay
        here: the interfaces layer receives a value object, shows it and asks
        for confirmation. Every costly check runs before that confirmation, so
        once the operator says yes only a network failure remains.

        Args:
            config: Current configuration.
            tag: Release tag that would be created (platform path only).
            release_destination: Override for ``config.release_destination``.

        Returns:
            ReleasePreflight: Recap of what the publication would do.

        Raises:
            PublishError: If the CLI is missing or unauthenticated, or if a
                release already exists for ``tag``.
            PublisherTypeError: If the platform is not supported.
            ReleaseError: If an enabled installer is missing, or nothing was
                built.
        """
        dest = release_destination or config.release_destination
        publisher = PublishService.resolve_publisher(config, release_destination)
        if publisher is None:
            return ReleasePreflight(destination=dest, is_platform=False)

        publisher.preflight()
        if publisher.exists(tag):
            raise PublishError(
                f"Release {tag} already exists. Delete it or change version."
            )
        assets = PipelineService.stage_versioned_assets(config)
        return ReleasePreflight(
            destination=dest,
            is_platform=True,
            publisher_name=publisher.get_publisher_name(),
            repo=config.release_endpoint or None,
            assets=tuple(assets),
        )

    # ////////////////////////////////////////////////
    # PUBLICATION
    # ////////////////////////////////////////////////

    @staticmethod
    def publish_update(
        config: CompilerConfig,
        *,
        destination: str | None = None,
        repo_destination: str | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Transfer the signed TUF tree to the update backend.

        Never routed to a platform release: a TUF tree must be served over
        HTTP on stable paths, which release assets do not provide.

        Args:
            config: Current configuration.
            destination: Override for the resolved repo destination.
            repo_destination: Override for ``config.repo_destination``.
            upload_config: Extra options forwarded to the uploader.

        Raises:
            UploadError: If the transfer fails.
        """
        repo_dir = TufService.repo_dir(config)
        repo_dest = repo_destination or config.repo_destination
        logger.info("Publishing TUF update tree (%s)", repo_dest)
        UploaderService.upload_tuf_repo(
            config, repo_dir, repo_dest, destination, upload_config
        )

    @staticmethod
    def publish_release(
        config: CompilerConfig,
        assets: list[Path],
        *,
        tag: str,
        title: str,
        notes: str | None = None,
        prerelease: bool = False,
        draft: bool = False,
        destination: str | None = None,
        release_destination: str | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> str | None:
        """Publish the release assets.

        Args:
            config: Current configuration.
            assets: Files to attach (platform path only). The file path
                re-assembles ``release/`` exactly as before and ignores it.
            tag: Release tag (platform path only).
            title: Release title (platform path only).
            notes: Release body; ``None`` requests generated notes.
            prerelease: Mark as pre-release.
            draft: Create unpublished.
            destination: Override for the resolved release destination.
            release_destination: Override for ``config.release_destination``.
            upload_config: Extra options forwarded to the uploader.

        Returns:
            str | None: The release URL on the platform path, ``None`` on the
                file-destination path.

        Raises:
            PublishError: If platform publication fails.
            UploadError: If the file transfer fails, or nothing was built.
        """
        # Routing resolved here and nowhere else: the CLI never handles a
        # PublisherPort (it goes through preflight_release()).
        publisher = PublishService.resolve_publisher(config, release_destination)
        if publisher is None:
            # File path: delegated as is to the existing code, which puts
            # the artifacts under <dest>/release/ and handles the r2/server
            # variants. Do NOT reimplement the upload loop here: the
            # `release/` subdirectory and the destination branches would be
            # lost.
            rel_dest = release_destination or config.release_destination
            logger.info("Uploading release assets (%s)", rel_dest)
            release_root = PipelineService.assemble_release_dir(config)
            # assemble_release_dir only copies what exists: without a
            # build, an empty directory would be transferred as a success.
            if not any(release_root.iterdir()):
                raise UploadError(
                    f"No artifact to publish in {release_root} "
                    "(zip or installer): run the compilation first."
                )
            UploaderService.upload_release_zip(
                config, release_root, rel_dest, destination, upload_config
            )
            return None

        if not assets:
            raise PublishError(f"No asset to publish for {tag}.")

        logger.info("Publishing release %s via %s", tag, publisher.get_publisher_name())
        url = publisher.publish(
            assets,
            tag=tag,
            title=title,
            notes=notes,
            prerelease=prerelease,
            draft=draft,
        )
        if not url:
            raise PublishError(
                f"Publishing {tag} returned no URL — cannot confirm that it succeeded."
            )
        return url
