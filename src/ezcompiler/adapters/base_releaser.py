# ///////////////////////////////////////////////////////////////
# BASE_RELEASER - Abstract base releaser interface
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base releaser - Abstract base class for secure-release packagers.

Defines the interface (conforming to ``types.ReleaserPort``) and shared
validation for releasers. The structural contract is the Port; this base
factors common behaviour. Boundaries are typed via the Port, not this base.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..shared.exceptions import BundleBuildError

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


# Le contrat structurel (Port) est défini par ``types.ReleaserPort`` (Protocol).
# Cette classe reste une base abstraite concrète : elle conforme au Port et
# factorise le comportement partagé (validation de bundle_dir).
# Les frontières (factory, service) sont typées via le Port, pas via cette base.
class BaseReleaser(ABC):
    """Abstract base class for secure-release packagers."""

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    # ////////////////////////////////////////////////
    # ABSTRACT METHODS
    # ////////////////////////////////////////////////

    @abstractmethod
    def release(
        self,
        bundle_dir: Path,
        app_name: str,
        version: str,
        repo_dir: Path,
        *,
        patch: bool = True,
    ) -> Path:
        """Build and sign the local TUF repository. Raises ReleaseError."""

    @abstractmethod
    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        """Initialise clés + squelette repo TUF. Idempotent.

        Returns True si init effectuée, False si déjà présente (skip).
        Raises ReleaseError / SigningKeyError on failure.
        """

    @abstractmethod
    def get_releaser_name(self) -> str:
        """Human-readable releaser name."""

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def _validate_bundle_dir(self, bundle_dir: Path) -> None:
        """Ensure the bundle directory exists and is non-empty."""
        if not bundle_dir.is_dir():
            raise BundleBuildError(f"Bundle directory does not exist: {bundle_dir}")
        if not any(bundle_dir.iterdir()):
            raise BundleBuildError(f"Bundle directory is empty: {bundle_dir}")
