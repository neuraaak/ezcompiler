# ///////////////////////////////////////////////////////////////
# TUF_SERVICE - Local TUF tree management (status, withdrawal)
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
TUF service - Reads and manages the local signed TUF tree.

Reads metadata as plain JSON (no tufup, no keys), keeps the list of
withdrawn versions in ``<repo>/withdrawn.json`` and enforces the rule that
a new release must be higher than every withdrawn version: clients that
installed a withdrawn version only leave it for a higher one.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Third-party imports
from packaging.version import InvalidVersion, Version

# Local imports
from .._types import ReleaserPort
from ..adapters import ReleaserFactory
from ..shared.exceptions import ReleaseError

if TYPE_CHECKING:
    from ..shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

WITHDRAWN_FILE = "withdrawn.json"

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class TufService:
    """Local TUF tree operations shared by the CLI and the release path."""

    # ////////////////////////////////////////////////
    # PATHS
    # ////////////////////////////////////////////////

    @staticmethod
    def repo_dir(config: CompilerConfig) -> Path:
        """Local TUF repository directory."""
        return config.tuf_repo_dir or (config.output_folder / "repo")

    @staticmethod
    def keys_dir(config: CompilerConfig) -> Path:
        """Private signing keys directory."""
        return config.tuf_keys_dir or (TufService.repo_dir(config) / "keystore")

    # ////////////////////////////////////////////////
    # WITHDRAWN VERSIONS
    # ////////////////////////////////////////////////

    @staticmethod
    def withdrawn_versions(repo_dir: Path) -> list[str]:
        """Versions removed from the tree, in withdrawal order.

        Raises:
            ReleaseError: If ``withdrawn.json`` exists but is malformed — a
                silently ignored file would disable the version guard.
        """
        path = repo_dir / WITHDRAWN_FILE
        if not path.is_file():
            return []
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            entries = doc["withdrawn"]
            if not isinstance(entries, list):
                raise TypeError("'withdrawn' n'est pas une liste")
            versions = [entry["version"] for entry in entries]
            if not all(isinstance(v, str) for v in versions):
                raise TypeError("version non textuelle")
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise ReleaseError(f"{path} illisible : {e}") from e
        return versions

    @staticmethod
    def record_withdrawn(
        repo_dir: Path, version: str, *, now: datetime | None = None
    ) -> None:
        """Append ``version`` to ``withdrawn.json``."""
        path = repo_dir / WITHDRAWN_FILE
        entries: list[dict[str, Any]] = [
            {"version": v, "withdrawn_at": at}
            for v, at in TufService._withdrawn_entries(path)
        ]
        stamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
        entries.append({"version": version, "withdrawn_at": stamp})
        path.write_text(
            json.dumps({"withdrawn": entries}, indent=2) + "\n", encoding="utf-8"
        )

    @staticmethod
    def _withdrawn_entries(path: Path) -> list[tuple[str, str]]:
        """Existing (version, withdrawn_at) pairs, validated."""
        versions = TufService.withdrawn_versions(path.parent)
        if not versions:
            return []
        doc = json.loads(path.read_text(encoding="utf-8"))
        return [
            (entry["version"], str(entry.get("withdrawn_at", "")))
            for entry in doc["withdrawn"]
        ]

    @staticmethod
    def ensure_releasable(repo_dir: Path, version: str) -> None:
        """Refuse a version that is not above every withdrawn version.

        Raises:
            ReleaseError: If ``version`` <= a withdrawn version (PEP 440), or
                equals a non-PEP 440 withdrawn string.
        """
        for withdrawn in TufService.withdrawn_versions(repo_dir):
            if TufService._not_above(version, withdrawn):
                raise ReleaseError(
                    f"La version {withdrawn} a été retirée de l'arbre TUF : les "
                    "clients qui l'ont installée n'accepteront qu'une version "
                    f"supérieure. Utiliser une version > {withdrawn} "
                    f"(demandée : {version})."
                )

    @staticmethod
    def _not_above(version: str, withdrawn: str) -> bool:
        try:
            return Version(version) <= Version(withdrawn)
        except InvalidVersion:
            return version == withdrawn

    # ////////////////////////////////////////////////
    # REMOVAL
    # ////////////////////////////////////////////////

    @staticmethod
    def remove_latest(config: CompilerConfig, *, release_type: str = "tufup") -> str:
        """Remove the latest version from the local tree and record it.

        Returns:
            str: The removed version.

        Raises:
            ReleaseError / SigningKeyError: From the releaser; nothing is
                recorded when the removal fails.
        """
        repo_dir = TufService.repo_dir(config)
        keys_dir = TufService.keys_dir(config)
        releaser: ReleaserPort = ReleaserFactory.create_releaser(
            release_type,
            {"keys_dir": keys_dir, "expiration_days": config.tuf_expiration_days},
        )
        removed = releaser.remove_latest(
            app_name=config.project_name, repo_dir=repo_dir, keys_dir=keys_dir
        )
        TufService.record_withdrawn(repo_dir, removed)
        logger.info("TUF version withdrawn: %s", removed)
        return removed
