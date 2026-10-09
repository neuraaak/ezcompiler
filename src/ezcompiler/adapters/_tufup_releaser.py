# ///////////////////////////////////////////////////////////////
# TUFUP_RELEASER - tufup (TUF) secure-release adapter
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Tufup releaser - Adapter packaging a compiled bundle into a signed TUF
repository via the optional ``tufup`` dependency.

``tufup`` is imported lazily inside ``release`` so importing this module never
requires the optional extra. This adapter only builds/signs the LOCAL
repository tree; publishing it to a remote target is delegated to the existing
uploaders by ``ReleaseService``.

API pinned on tufup==0.10.0 (see _temp/tufup-audit.md).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from pathlib import Path

from ..shared.exceptions import ReleaseError, SigningKeyError
from .base_releaser import BaseReleaser

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class TufupReleaser(BaseReleaser):
    """Releaser backed by the ``tufup`` TUF framework."""

    # ////////////////////////////////////////////////
    # RELEASE
    # ////////////////////////////////////////////////

    def release(
        self,
        bundle_dir: Path,
        app_name: str,
        version: str,
        repo_dir: Path,
        *,
        patch: bool = True,
        required: bool = False,
    ) -> Path:
        """Build and sign the local TUF repository for the bundle."""
        self._validate_bundle_dir(bundle_dir)

        keys_dir = Path(self._config.get("keys_dir", repo_dir / "keystore"))
        if not keys_dir.is_dir():
            raise SigningKeyError(
                f"Signing keys directory not found: {keys_dir}. "
                "Initialize keys first (admin operation, never part of automated build)."
            )

        # Fail fast on a half-initialized repo (keys present but metadata tree
        # missing): tufup would otherwise prompt interactively to create the
        # metadata directory (input("Create directory ...?")), hanging the build.
        root_metadata = repo_dir / "metadata" / "root.json"
        if not root_metadata.exists():
            raise ReleaseError(
                f"TUF repository not initialized at {repo_dir} "
                f"(missing {root_metadata}). Run key/repo initialization first "
                "(e.g. `ezcompiler tuf init`)."
            )

        try:
            from tufup.repo import (  # noqa: PLC0415 # pyright: ignore[reportMissingImports]
                Repository,
                TargetMeta,
            )
        except ImportError as exc:
            raise ReleaseError(
                "tufup is not installed; install ezcompiler[tufup]"
            ) from exc

        try:
            repository = Repository(
                app_name=app_name,
                repo_dir=str(repo_dir),
                keys_dir=str(keys_dir),
                expiration_days=self._config.get("expiration_days"),
            )
            # Fail fast on an already-released version: TUF versions are immutable
            # once published, and tufup would otherwise prompt interactively
            # (input("Overwrite?")), hanging the automated build.
            archive_path = repository.targets_dir / TargetMeta.compose_filename(
                name=app_name, version=version, is_archive=True
            )
            if archive_path.exists():
                raise ReleaseError(
                    f"Version {version} already released for {app_name} "
                    f"({archive_path}). Bump the version to release again."
                )
            # Load existing keys/roles from disk (self.roles stays None otherwise).
            # Use create_keys=False — same path as Repository.from_config() — so the
            # build never prompts to overwrite keys nor regenerates them.
            repository._load_keys_and_roles(create_keys=False)
            repository.add_bundle(
                new_bundle_dir=bundle_dir,
                new_version=version,
                skip_patch=not patch,
                required=required,
            )
            repository.publish_changes(private_key_dirs=[keys_dir])
        except (ReleaseError, SigningKeyError):
            raise
        except Exception as exc:
            raise ReleaseError(f"tufup release failed: {exc}") from exc

        return repo_dir

    # ////////////////////////////////////////////////
    # INIT
    # ////////////////////////////////////////////////

    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        """Initialize keys and the TUF repo skeleton. Idempotent.

        Returns True if the init ran, False if it was already present (skip).
        """
        try:
            keys_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise SigningKeyError(f"Cannot create keys directory: {keys_dir}") from exc

        # Idempotent only when the repo is FULLY initialized: keys present AND
        # the metadata tree exists. Keys and metadata live in separate dirs, so
        # checking keys alone would skip initialize() on a repo whose metadata
        # was never created (or was cleaned), leaving release() to hang on
        # tufup's interactive metadata-dir prompt. tufup.initialize() is safe to
        # call for existing keys (it never regenerates them).
        root_metadata = repo_dir / "metadata" / "root.json"
        if any(keys_dir.iterdir()) and root_metadata.exists():
            return False

        try:
            from tufup.repo import (  # noqa: PLC0415 # pyright: ignore[reportMissingImports]
                Repository,
            )
        except ImportError as exc:
            raise ReleaseError(
                "tufup is not installed; install ezcompiler[tufup]"
            ) from exc

        try:
            repository = Repository(
                app_name=app_name,
                repo_dir=str(repo_dir),
                keys_dir=str(keys_dir),
                expiration_days=self._config.get("expiration_days"),
            )
            repository.save_config()
            repository.initialize()
        except (ReleaseError, SigningKeyError):
            raise
        except Exception as exc:
            raise ReleaseError(f"tufup init failed: {exc}") from exc

        return True

    # ////////////////////////////////////////////////
    # REFRESH
    # ////////////////////////////////////////////////

    def refresh_expiration(
        self,
        app_name: str,
        repo_dir: Path,
        keys_dir: Path,
        *,
        roles: tuple[str, ...] = ("targets", "snapshot", "timestamp"),
        days: int | None = None,
    ) -> Path:
        """Re-sign metadata to push out expiration without a new release.

        Native tufup keep-alive for projects updated irregularly: bumps the
        expiration date of the short-lived roles (``targets``/``snapshot``/
        ``timestamp`` by default) and re-publishes. ``root`` is long-lived
        (365 days) and left untouched unless explicitly requested.

        Args:
            app_name: Application name (must match the initialized repo).
            repo_dir: Root of the local TUF repository tree.
            keys_dir: Directory holding the private signing keys.
            roles: Role names whose expiration should be refreshed.
            days: Number of days from now. None → the repo's configured
                per-role ``expiration_days`` (or tufup defaults).

        Returns:
            Path: The local repository directory.

        Raises:
            SigningKeyError: If the keys directory is missing.
            ReleaseError: If the repo is not initialized or refresh fails.
        """
        if not keys_dir.is_dir():
            raise SigningKeyError(
                f"Signing keys directory not found: {keys_dir}. "
                "Initialize keys first (admin operation)."
            )
        root_metadata = repo_dir / "metadata" / "root.json"
        if not root_metadata.exists():
            raise ReleaseError(
                f"TUF repository not initialized at {repo_dir} "
                f"(missing {root_metadata}). Run `ezcompiler tuf init` first."
            )

        try:
            from tufup.repo import (  # noqa: PLC0415 # pyright: ignore[reportMissingImports]
                Repository,
            )
        except ImportError as exc:
            raise ReleaseError(
                "tufup is not installed; install ezcompiler[tufup]"
            ) from exc

        try:
            repository = Repository(
                app_name=app_name,
                repo_dir=str(repo_dir),
                keys_dir=str(keys_dir),
                expiration_days=self._config.get("expiration_days"),
            )
            repository._load_keys_and_roles(create_keys=False)
            for role_name in roles:
                repository.refresh_expiration_date(role_name=role_name, days=days)
            repository.publish_changes(private_key_dirs=[keys_dir])
        except (ReleaseError, SigningKeyError):
            raise
        except Exception as exc:
            raise ReleaseError(f"tufup expiration refresh failed: {exc}") from exc

        return repo_dir

    # ////////////////////////////////////////////////
    # REMOVE LATEST
    # ////////////////////////////////////////////////

    def remove_latest(self, app_name: str, repo_dir: Path, keys_dir: Path) -> str:
        """Remove the latest archive and its patch, then re-sign the tree.

        Native tufup ``remove_latest_bundle``: only the latest version can be
        removed, intermediate ones would break the patch chain. The change is
        local; ``ezcompiler publish update`` publishes it.

        Args:
            app_name: Application name (must match the initialized repo).
            repo_dir: Root of the local TUF repository tree.
            keys_dir: Directory holding the private signing keys.

        Returns:
            str: The removed version, as spelled in the archive name.

        Raises:
            SigningKeyError: If the keys directory is missing.
            ReleaseError: If the repo is not initialized, holds no version,
                or tufup fails.
        """
        if not keys_dir.is_dir():
            raise SigningKeyError(
                f"Signing keys directory not found: {keys_dir}. "
                "Initialize keys first (`ezcompiler tuf init`)."
            )
        root_metadata = repo_dir / "metadata" / "root.json"
        if not root_metadata.exists():
            raise ReleaseError(
                f"TUF repository not initialized at {repo_dir} "
                f"(missing {root_metadata}). Run `ezcompiler tuf init` first."
            )

        try:
            from tufup.repo import (  # noqa: PLC0415 # pyright: ignore[reportMissingImports]
                Repository,
            )
        except ImportError as exc:
            raise ReleaseError(
                "tufup is not installed; install ezcompiler[tufup]"
            ) from exc

        try:
            repository = Repository(
                app_name=app_name,
                repo_dir=str(repo_dir),
                keys_dir=str(keys_dir),
                expiration_days=self._config.get("expiration_days"),
            )
            repository._load_keys_and_roles(create_keys=False)
            if repository.roles is None:
                # Under python -O an assert would vanish and the error
                # deviendrait un AttributeError en pleine signature.
                raise ReleaseError(
                    f"Unreadable TUF roles in {repo_dir}: missing or "
                    "arbre incomplet. Relancer `ezcompiler tuf init`."
                )
            latest = repository.roles.get_latest_archive()
            if latest is None:
                raise ReleaseError(f"No version to withdraw in {repo_dir}.")
            # TargetMeta.version is normalized (1.0.1rc1): return the
            # archive-name spelling (1.0.1-rc.1), the one the config uses.
            name = Path(latest.target_path_str).name
            version = name[len(app_name) + 1 : -len(".tar.gz")]
            repository.remove_latest_bundle()
            repository.publish_changes(private_key_dirs=[keys_dir])
        except (ReleaseError, SigningKeyError):
            raise
        except Exception as exc:
            raise ReleaseError(f"tufup remove-latest failed: {exc}") from exc

        return version

    # ////////////////////////////////////////////////
    # METADATA
    # ////////////////////////////////////////////////

    def get_releaser_name(self) -> str:
        return "Tufup"
