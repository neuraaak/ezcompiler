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
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

# Third-party imports
from packaging.version import InvalidVersion, Version

# Local imports
from .._types import ReleaserPort
from ..adapters import ReleaserFactory
from ..shared import TufStatus, TufVersion
from ..shared._constants import TUF_PUBLIC_DIRS
from ..shared.exceptions import ReleaseError

if TYPE_CHECKING:
    from ..shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

WITHDRAWN_FILE = "withdrawn.json"
# Timestamped backups of the signed tree, taken before any withdrawal.
BACKUP_DIR = ".backup"
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
                raise TypeError("'withdrawn' is not a list")
            versions = [entry["version"] for entry in entries]
            if not all(isinstance(v, str) for v in versions):
                raise TypeError("non-string version")
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise ReleaseError(f"{path} is unreadable: {e}") from e
        return versions

    @staticmethod
    def record_withdrawn(
        repo_dir: Path, version: str, *, now: datetime | None = None
    ) -> None:
        """Append ``version`` to ``withdrawn.json``.

        The file is written atomically (temporary file in the same directory,
        then ``os.replace``): an interrupted write never truncates it.

        Raises:
            ReleaseError: If the existing file is malformed, or if the write
                fails — the message names the version to add by hand.
        """
        path = repo_dir / WITHDRAWN_FILE
        entries: list[dict[str, Any]] = [
            {"version": v, "withdrawn_at": at}
            for v, at in TufService._withdrawn_entries(path)
        ]
        stamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
        entries.append({"version": version, "withdrawn_at": stamp})
        tmp = path.with_name(f"{WITHDRAWN_FILE}.tmp")
        try:
            tmp.write_text(
                json.dumps({"withdrawn": entries}, indent=2) + "\n", encoding="utf-8"
            )
            os.replace(tmp, path)
        except OSError as e:
            tmp.unlink(missing_ok=True)
            raise ReleaseError(
                f"Cannot record the withdrawal of {version} in {path}: "
                f"{e}. Add {version} to that file by hand before any "
                "new release."
            ) from e

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
                    f"Version {withdrawn} was withdrawn from the TUF tree: "
                    "clients that installed it will only accept a higher "
                    f"version. Use a version > {withdrawn} "
                    f"(requested: {version})."
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

        The signed tree (``metadata/``, ``targets/`` and ``withdrawn.json``) is
        copied to a timestamped backup directory first, and the withdrawal is
        recorded **before** the irreversible mutation: a releaser failure
        (missing key, read-only keystore, expired role) can therefore never
        leave a half-mutated tree with the withdrawal unrecorded. On failure the
        three are restored from the backup, whose path is named in the error.

        Returns:
            str: The removed version.

        Raises:
            ReleaseError: If ``withdrawn.json`` is malformed or cannot be
                written, if the tree holds no version, or if the backup cannot
                be taken (nothing is removed in any of those cases).
            ReleaseError / SigningKeyError: From the releaser; the tree and the
                register are rolled back to their pre-removal state.
        """
        repo_dir = TufService.repo_dir(config)
        keys_dir = TufService.keys_dir(config)
        # Validate withdrawn.json BEFORE the irreversible withdrawal: an
        # unreadable file would drop the version without recording it.
        TufService.withdrawn_versions(repo_dir)

        predicted = TufService.latest_tree_version(repo_dir, config.project_name)
        if predicted is None:
            raise ReleaseError(f"No version to withdraw in {repo_dir}.")

        backup = TufService._backup_tree(repo_dir)
        releaser: ReleaserPort = ReleaserFactory.create_releaser(
            release_type,
            {"keys_dir": keys_dir, "expiration_days": config.tuf_expiration_days},
        )
        TufService.record_withdrawn(repo_dir, predicted)
        try:
            removed = releaser.remove_latest(
                app_name=config.project_name, repo_dir=repo_dir, keys_dir=keys_dir
            )
        except Exception as exc:
            restored = TufService._restore_tree(repo_dir, backup)
            detail = (
                f"tree and register restored from {backup}"
                if restored
                else f"RESTORE FAILED: restore by hand from {backup}"
            )
            raise ReleaseError(
                f"Withdrawal of {predicted} failed ({exc}) — {detail}."
            ) from exc
        if not TufService.same_version(removed, predicted):
            # Unlikely divergence: also record the version actually
            # withdrawn so the guard covers both spellings.
            logger.warning(
                "TUF removal mismatch: tree announced %s, releaser removed %s",
                predicted,
                removed,
            )
            TufService.record_withdrawn(repo_dir, removed)
        logger.info("TUF version withdrawn: %s (sauvegarde : %s)", removed, backup)
        return removed

    @staticmethod
    def _backup_tree(repo_dir: Path) -> Path:
        """Copy the signed tree and the register to a timestamped directory.

        Returns:
            Path: The backup directory, under ``<repo_dir>/.backup``.

        Raises:
            ReleaseError: If the copy fails — nothing must be removed without
                a restorable snapshot.
        """
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup = repo_dir / BACKUP_DIR / f"remove-latest-{stamp}"
        try:
            backup.mkdir(parents=True, exist_ok=True)
            for name in TUF_PUBLIC_DIRS:
                source = repo_dir / name
                if source.is_dir():
                    shutil.copytree(source, backup / name, dirs_exist_ok=True)
            register = repo_dir / WITHDRAWN_FILE
            if register.is_file():
                shutil.copy2(register, backup / WITHDRAWN_FILE)
        except OSError as e:
            raise ReleaseError(
                f"Cannot back up the TUF tree into {backup}: {e}. "
                "No withdrawal was performed."
            ) from e
        return backup

    @staticmethod
    def _restore_tree(repo_dir: Path, backup: Path) -> bool:
        """Put ``metadata/``, ``targets/`` and the register back from ``backup``.

        Returns:
            bool: True when the restore succeeded; the caller names the backup
                directory in its error message when it did not.
        """
        try:
            for name in TUF_PUBLIC_DIRS:
                source = backup / name
                if source.is_dir():
                    shutil.rmtree(repo_dir / name, ignore_errors=True)
                    shutil.copytree(source, repo_dir / name)
            register = backup / WITHDRAWN_FILE
            if register.is_file():
                shutil.copy2(register, repo_dir / WITHDRAWN_FILE)
            else:
                (repo_dir / WITHDRAWN_FILE).unlink(missing_ok=True)
        except OSError:
            return False
        return True

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
                f"No TUF tree initialized in {repo_dir} "
                "(metadata/root.json missing). Run `ezcompiler tuf init`."
            )

        signed = {role: TufService._read_signed(meta_dir, role) for role in TUF_ROLES}
        try:
            expirations = {
                role: TufService._parse_expires(signed[role]["expires"])
                for role in TUF_ROLES
            }
            targets = signed["targets"].get("targets", {})
            if not isinstance(targets, dict):
                raise TypeError("'targets' is not an object")
            versions = TufService._versions(config.project_name, targets)
        except (KeyError, ValueError, AttributeError, TypeError) as e:
            raise ReleaseError(f"Unreadable TUF metadata in {meta_dir}: {e}") from e

        return TufStatus(
            repo_dir=repo_dir,
            versions=versions,
            expirations=expirations,
            withdrawn=tuple(TufService.withdrawn_versions(repo_dir)),
        )

    @staticmethod
    def _parse_expires(raw: object) -> datetime:
        """ISO 8601 expiry; a value without offset is read as UTC."""
        expires = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return expires

    @staticmethod
    def _read_signed(meta_dir: Path, role: str) -> dict[str, Any]:
        path = meta_dir / f"{role}.json"
        try:
            signed = json.loads(path.read_text(encoding="utf-8"))["signed"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise ReleaseError(f"{path} is unreadable: {e}") from e
        if not isinstance(signed, dict):
            raise ReleaseError(f"{path} is unreadable: 'signed' is not an object")
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
            if not isinstance(info, dict):
                raise TypeError(f"entry {name!r} is not an object")
            custom = info.get("custom") or {}
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
            allow_empty: True after the only version was withdrawn: the
                empty tree is publishable and ``None`` is then returned.

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
                f"No signed TUF tree in {repo_dir} "
                f"({targets_meta.name} missing). "
                "Run the build pipeline first (`ezcompiler compile`)."
            )
        latest = TufService.latest_tree_version(repo_dir, config.project_name)
        if latest is None and not allow_empty:
            raise ReleaseError(
                f"{targets_meta} references no archive of "
                f"{config.project_name}. Run the build pipeline first."
            )
        return latest

    @staticmethod
    def latest_tree_version(repo_dir: Path, app_name: str) -> str | None:
        """Highest ``<app>-<version>`` archive signed in ``repo_dir``.

        Returns:
            str | None: The raw version spelling tufup used, or ``None`` when
                no signed ``targets.json`` exists or it names no archive.

        Raises:
            ReleaseError: If ``targets.json`` exists but cannot be read.
        """
        targets_meta = repo_dir / "metadata" / "targets.json"
        if not targets_meta.is_file():
            return None
        try:
            doc = json.loads(targets_meta.read_text(encoding="utf-8"))
            names = doc["signed"]["targets"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise ReleaseError(f"{targets_meta} is unreadable: {e}") from e

        pattern = re.compile(rf"^{re.escape(app_name)}-(.+)\.tar\.gz$")
        # tufup names the archive with the raw config string: return it as
        # is (1.2.3-rc.1, not its normalized form 1.2.3rc1).
        versions: list[tuple[Version, str]] = []
        for name in names:
            match = pattern.match(name)
            if match is None:
                continue
            try:
                versions.append((Version(match.group(1)), match.group(1)))
            except InvalidVersion:
                continue
        return max(versions)[1] if versions else None

    @staticmethod
    def needs_full_archive(repo_dir: Path, app_name: str) -> bool:
        """True for the first release after a withdrawal.

        tufup builds the patch from the latest archive still in the tree.
        Clients on a withdrawn version above it hold another archive: the
        patch would fail its hash check, so the release ships without one.
        """
        withdrawn = TufService.withdrawn_versions(repo_dir)
        if not withdrawn:
            return False
        latest = TufService.latest_tree_version(repo_dir, app_name)
        if latest is None:
            return True
        return any(not TufService._not_above(w, latest) for w in withdrawn)

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
