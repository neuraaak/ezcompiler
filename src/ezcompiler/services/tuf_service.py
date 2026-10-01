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
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

# Third-party imports
from packaging.version import InvalidVersion, Version

# Local imports
from .._types import ReleaserPort
from ..adapters import ReleaserFactory
from ..shared import TufStatus, TufVersion
from ..shared.exceptions import ReleaseError

if TYPE_CHECKING:
    from ..shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

WITHDRAWN_FILE = "withdrawn.json"
TUF_ROLES = ("root", "targets", "snapshot", "timestamp")

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

    # ////////////////////////////////////////////////
    # STATUS
    # ////////////////////////////////////////////////

    @staticmethod
    def status(config: CompilerConfig) -> TufStatus:
        """Read the local tree: versions, flags, expirations, withdrawals.

        Raises:
            ReleaseError: If the tree is not initialized or a metadata file
                cannot be read.
        """
        repo_dir = TufService.repo_dir(config)
        meta_dir = repo_dir / "metadata"
        if not (meta_dir / "root.json").is_file():
            raise ReleaseError(
                f"Aucun arbre TUF initialisé dans {repo_dir} "
                "(metadata/root.json absent). Lancer `ezcompiler tuf init`."
            )

        signed = {role: TufService._read_signed(meta_dir, role) for role in TUF_ROLES}
        try:
            expirations = {
                role: datetime.fromisoformat(
                    str(signed[role]["expires"]).replace("Z", "+00:00")
                )
                for role in TUF_ROLES
            }
            targets = signed["targets"].get("targets", {})
        except (KeyError, ValueError, AttributeError) as e:
            raise ReleaseError(
                f"Métadonnées TUF illisibles dans {meta_dir} : {e}"
            ) from e

        return TufStatus(
            repo_dir=repo_dir,
            versions=TufService._versions(config.project_name, targets),
            expirations=expirations,
            withdrawn=tuple(TufService.withdrawn_versions(repo_dir)),
        )

    @staticmethod
    def _read_signed(meta_dir: Path, role: str) -> dict[str, Any]:
        path = meta_dir / f"{role}.json"
        try:
            signed = json.loads(path.read_text(encoding="utf-8"))["signed"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise ReleaseError(f"{path} illisible : {e}") from e
        if not isinstance(signed, dict):
            raise ReleaseError(f"{path} illisible : 'signed' n'est pas un objet")
        return signed

    @staticmethod
    def _versions(app_name: str, targets: dict[str, Any]) -> tuple[TufVersion, ...]:
        archive = re.compile(rf"^{re.escape(app_name)}-(.+)\.tar\.gz$")
        patch = re.compile(rf"^{re.escape(app_name)}-(.+)\.patch$")
        patched = {m.group(1) for name in targets if (m := patch.match(name))}
        found: list[tuple[Version, TufVersion]] = []
        for name, info in targets.items():
            match = archive.match(name)
            if match is None:
                continue
            raw = match.group(1)
            try:
                parsed = Version(raw)
            except InvalidVersion:
                continue
            custom = (info or {}).get("custom") or {}
            required = bool((custom.get("tufup") or {}).get("required", False))
            found.append((parsed, TufVersion(raw, required, raw in patched)))
        found.sort(key=lambda item: item[0], reverse=True)
        return tuple(v for _, v in found)

    # ////////////////////////////////////////////////
    # TREE VERSION
    # ////////////////////////////////////////////////

    @overload
    @staticmethod
    def read_tree_version(
        config: CompilerConfig, *, allow_empty: Literal[False] = False
    ) -> str: ...

    @overload
    @staticmethod
    def read_tree_version(
        config: CompilerConfig, *, allow_empty: bool
    ) -> str | None: ...

    @staticmethod
    def read_tree_version(
        config: CompilerConfig, *, allow_empty: bool = False
    ) -> str | None:
        """Return the highest version signed in the local TUF tree.

        The recap of ``publish update`` names this version, not
        ``config.version``: a config bumped without a rebuild would otherwise
        announce a version the tree does not carry.

        Args:
            config: Current configuration (repo dir and project name).
            allow_empty: True après le retrait de la seule version : l'arbre
                vide est publiable, ``None`` est alors renvoyé.

        Returns:
            str | None: Highest version among the ``<app>-<version>`` targets,
                or ``None`` if ``allow_empty`` and the tree holds no archive.

        Raises:
            ReleaseError: If no signed ``targets.json`` exists or it names no
                archive of the project.
        """
        repo_dir = TufService.repo_dir(config)
        targets_meta = repo_dir / "metadata" / "targets.json"
        if not targets_meta.is_file():
            raise ReleaseError(
                f"Aucun arbre TUF signé dans {repo_dir} "
                f"({targets_meta.name} absent). "
                "Lancer d'abord le pipeline de build (`ezcompiler compile`)."
            )
        try:
            doc = json.loads(targets_meta.read_text(encoding="utf-8"))
            names = doc["signed"]["targets"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise ReleaseError(f"{targets_meta} illisible : {e}") from e

        pattern = re.compile(rf"^{re.escape(config.project_name)}-(.+)\.tar\.gz$")
        # tufup nomme l'archive avec la chaîne brute de la config : on la
        # renvoie telle quelle (1.2.3-rc.1, pas sa forme normalisée 1.2.3rc1).
        versions: list[tuple[Version, str]] = []
        for name in names:
            match = pattern.match(name)
            if match is None:
                continue
            try:
                versions.append((Version(match.group(1)), match.group(1)))
            except InvalidVersion:
                continue
        if not versions and allow_empty:
            return None
        if not versions:
            raise ReleaseError(
                f"{targets_meta} ne référence aucune archive de "
                f"{config.project_name}. Lancer d'abord le pipeline de build."
            )
        return max(versions)[1]

    @staticmethod
    def same_version(left: str, right: str) -> bool:
        """Compare two version strings by PEP 440 meaning, not spelling.

        ``1.2.3-rc.1`` and ``1.2.3rc1`` are the same version. Strings that
        are not PEP 440 versions fall back to an exact comparison.
        """
        try:
            return Version(left) == Version(right)
        except InvalidVersion:
            return left == right
