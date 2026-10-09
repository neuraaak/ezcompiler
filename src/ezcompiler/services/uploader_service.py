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
import shutil
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

# Local imports
from ..adapters import UploaderFactory
from ..shared._constants import RELEASE_SUBDIR, TUF_PUBLIC_DIRS, UPDATE_SUBDIR
from ..shared.exceptions import UploadError
from ..utils.validators import validate_upload_structure
from .tuf_service import WITHDRAWN_FILE, TufService

if TYPE_CHECKING:
    from .._types import UploaderPort
    from ..shared._compiler_config import CompilerConfig

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

UploadType = Literal["disk", "server", "r2"]

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Default keystore name, excluded from staging whatever its position.
DEFAULT_KEYSTORE_DIRNAME = "keystore"

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

            # Copy: the caller's dict is reused for the following uploads,
            # an in-place mutation would contaminate the next backend.
            config = dict(upload_config or {})
            if upload_type == "disk":
                config["destination_path"] = destination
            elif upload_type == "server":
                config["server_url"] = destination
            # r2: bucket comes from upload_config, destination = object prefix

            # Create uploader and perform upload
            uploader: UploaderPort = UploaderFactory.create_uploader(
                upload_type, config
            )
            uploader.upload(source_path=source_path, destination=destination)
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Upload failed: {str(e)}") from e

    @staticmethod
    def download(
        remote_source: str,
        upload_type: UploadType,
        destination_local: Path,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Download a remote tree into ``destination_local`` via the backend.

        Args:
            remote_source: Remote source (path, URL or prefix) to fetch.
            upload_type: Backend type ("disk", "server" or "r2").
            destination_local: Local directory to populate.
            upload_config: Additional uploader configuration options.

        Raises:
            UploadError: If the download fails or the type is invalid.
        """
        try:
            uploader: UploaderPort = UploaderFactory.create_uploader(
                upload_type, upload_config or {}
            )
            uploader.download(remote_source, destination_local)
        except UploadError:
            raise
        except Exception as e:
            raise UploadError(f"Download failed: {str(e)}") from e

    @staticmethod
    def upload_release(
        config: CompilerConfig,
        repo_dir: Path,
        release_root: Path | None,
        destination: str | None = None,
        repo_destination: str | None = None,
        release_destination: str | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Sequential double upload: TUF tree then installer zip.

        Step 1 — upload the TUF tree to ``<dest>/update/`` (or the R2 prefix).
        Step 2 — upload the installer zip to ``<dest>/release/`` (skipped on R2).

        Note: The double upload is not atomic. If the zip upload fails, the
        TUF repo is already online. On failure, run upload() again to
        resume.

        Args:
            config: CompilerConfig holding the destinations and R2 options.
            repo_dir: Local directory of the TUF repo.
            release_root: Local directory of the installer zip (None on R2).
            destination: Shared override for both destinations.
            repo_destination: Override for ``config.repo_destination``.
            release_destination: Override for ``config.release_destination``.
            upload_config: Extra options passed to the uploaders.

        Raises:
            UploadError: If an upload fails.
        """
        repo_dest = repo_destination or config.repo_destination
        rel_dest = release_destination or config.release_destination

        UploaderService.upload_tuf_repo(
            config, repo_dir, repo_dest, destination, upload_config
        )

        if release_root is not None:
            UploaderService.upload_release_zip(
                config, release_root, rel_dest, destination, upload_config
            )

    @staticmethod
    def upload_tuf_repo(
        config: CompilerConfig,
        repo_dir: Path,
        repo_dest: str,
        destination: str | None,
        upload_config: dict[str, Any] | None,
    ) -> None:
        """Upload the public part of the TUF tree to the configured destination.

        Only ``metadata/``, ``targets/`` and ``withdrawn.json`` are published,
        from a temporary copy (see ``staged_tuf_tree``): the private keys
        stored under ``repo_dir`` are never transferred.
        """
        try:
            with UploaderService.staged_tuf_tree(
                repo_dir, keys_dir=TufService.keys_dir(config)
            ) as staged:
                UploaderService._upload_tuf_tree(
                    config, staged, repo_dest, destination, upload_config
                )
        except UploadError as e:
            raise UploadError(f"TUF repo upload failed: {e}") from e

    @staticmethod
    @contextmanager
    def staged_tuf_tree(
        repo_dir: Path, *, keys_dir: Path | None = None
    ) -> Iterator[Path]:
        """Copy the public files of the TUF tree into a temporary directory.

        The layout is preserved (``metadata/``, ``targets/``,
        ``withdrawn.json`` at the root); the directory is removed on exit.
        The keystore is always excluded from the copy, even when it sits
        under ``metadata/`` or ``targets/``.

        Args:
            repo_dir: Root of the local TUF tree.
            keys_dir: Private keystore to exclude, on top of any directory
                named ``keystore``.

        Raises:
            UploadError: If ``repo_dir/metadata`` is missing (publishing an
                empty tree would overwrite the remote channel) or if the copy
                fails.
        """
        if not (repo_dir / "metadata").is_dir():
            raise UploadError(
                f"TUF tree missing: {repo_dir / 'metadata'} not found. "
                "Run `ezcompiler tuf init` first, then the build."
            )
        with tempfile.TemporaryDirectory(prefix="ezcompiler-tuf-") as tmp:
            staging = Path(tmp)
            try:
                ignore = UploaderService._ignore_private_keys(keys_dir)
                for name in TUF_PUBLIC_DIRS:
                    if (repo_dir / name).is_dir():
                        shutil.copytree(repo_dir / name, staging / name, ignore=ignore)
                withdrawn = repo_dir / WITHDRAWN_FILE
                if withdrawn.is_file():
                    shutil.copy2(withdrawn, staging / WITHDRAWN_FILE)
            except OSError as e:
                raise UploadError(f"Copie de l'arbre TUF impossible : {e}") from e
            yield staging

    @staticmethod
    def _ignore_private_keys(
        keys_dir: Path | None,
    ) -> Callable[[str, list[str]], set[str]]:
        """Build the ``ignore`` filter for ``shutil.copytree``.

        Args:
            keys_dir: Configured private keystore, when known.

        Returns:
            Callable: Filter excluding the configured keystore as well as any
                directory named ``keystore``.
        """
        resolved = keys_dir.expanduser().resolve() if keys_dir else None

        def ignore(src: str, names: list[str]) -> set[str]:
            excluded: set[str] = set()
            for name in names:
                if name == DEFAULT_KEYSTORE_DIRNAME:
                    excluded.add(name)
                    continue
                if resolved is None:
                    continue
                candidate = (Path(src) / name).resolve()
                if candidate == resolved or resolved in candidate.parents:
                    excluded.add(name)
            return excluded

        return ignore

    @staticmethod
    def _upload_tuf_tree(
        config: CompilerConfig,
        staged_dir: Path,
        repo_dest: str,
        destination: str | None,
        upload_config: dict[str, Any] | None,
    ) -> None:
        """Route an already-filtered TUF tree to the configured backend."""
        if repo_dest == "r2":
            endpoint = config.repo_endpoint
            bucket, _, prefix = endpoint.partition("/")
            UploaderService.upload(
                source_path=staged_dir,
                upload_type="r2",
                destination=prefix,
                upload_config={"bucket": bucket},
            )
        elif repo_dest == "server":
            base = destination or config.resolved_repo_destination or ""
            UploaderService.upload(
                source_path=staged_dir,
                upload_type="server",
                destination=base.rstrip("/") + f"/{UPDATE_SUBDIR}",
                upload_config=upload_config,
            )
        else:  # disk (default)
            base = destination or config.resolved_repo_destination or ""
            UploaderService.upload(
                source_path=staged_dir,
                upload_type="disk",
                destination=str(Path(base) / UPDATE_SUBDIR),
                upload_config=upload_config,
            )

    @staticmethod
    def upload_release_zip(
        config: CompilerConfig,
        release_root: Path,
        rel_dest: str,
        destination: str | None,
        upload_config: dict[str, Any] | None,
    ) -> None:
        """Upload the installer zip to the configured destination."""
        try:
            if rel_dest == "r2":
                endpoint = config.release_endpoint
                bucket, _, prefix = endpoint.partition("/")
                UploaderService.upload(
                    source_path=release_root,
                    upload_type="r2",
                    destination=prefix,
                    upload_config={"bucket": bucket},
                )
            elif rel_dest == "server":
                base = destination or config.resolved_release_destination or ""
                UploaderService.upload(
                    source_path=release_root,
                    upload_type="server",
                    destination=base.rstrip("/") + f"/{RELEASE_SUBDIR}",
                    upload_config=upload_config,
                )
            else:  # disk (default)
                base = destination or config.resolved_release_destination or ""
                UploaderService.upload(
                    source_path=release_root,
                    upload_type="disk",
                    destination=str(Path(base) / RELEASE_SUBDIR),
                    upload_config=upload_config,
                )
        except UploadError as e:
            raise UploadError(f"Release zip upload failed: {e}") from e

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
