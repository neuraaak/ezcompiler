# ///////////////////////////////////////////////////////////////
# TYPES - Type Aliases Module
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Type aliases module for ezcompiler.

This module centralizes common type aliases used throughout the library
to improve code readability, maintainability, and type safety.

Example:
    >>> from ezcompiler.types import IncludeFiles, CompilerName
    >>>
    >>> def build(compiler: CompilerName, files: IncludeFiles) -> None:
    ...     pass
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

# ------------------------------------------------
# Path Types
# ------------------------------------------------

type FilePath = str | Path
"""Type alias for file path inputs.

Accepts:
    - str: String file path
    - Path: pathlib.Path object

Used by: CompilerConfig, template loaders, file utilities.
"""

# ------------------------------------------------
# Compiler Types
# ------------------------------------------------

type CompilerName = str
"""Type alias for compiler name selection.

Valid values: "" (unset -> prompt), "Cx_Freeze", "PyInstaller", "Nuitka"

Used by: CompilerConfig.compiler, EzCompiler.compile_project().
"""

type RepoDestination = Literal["disk", "server", "r2"]
"""Type alias for the TUF repository upload backend.

Valid values: "disk", "server", "r2"

Used by: CompilerConfig.repo_destination, EzCompiler.upload().
"""

type ReleaseDestination = Literal["disk", "server", "r2"]
"""Type alias for the release zip upload backend.

Valid values: "disk", "server", "r2"

Used by: CompilerConfig.release_destination, EzCompiler.upload().
"""

type ReleaseTarget = Literal["tufup"]
"""Type alias for the secure-release backend selection.

Valid values: "tufup"

Used by: CompilerConfig.release_type, ReleaserFactory.
"""

# ------------------------------------------------
# Configuration Types
# ------------------------------------------------

type IncludeFiles = dict[str, list[str]]
"""Type alias for the include_files configuration structure.

Expected shape::

    {
        "files": ["path/to/file1.txt", "path/to/file2.dll"],
        "folders": ["path/to/assets/", "path/to/data/"],
    }

Used by: CompilerConfig.include_files.
"""

type JsonMap = dict[str, object]
"""Type alias for a generic JSON-serializable mapping.

Used by: configuration parsers, template renderers, YAML/JSON loaders.
"""

# ///////////////////////////////////////////////////////////////
# PORTS (structural contracts — Hexagonal architecture)
# ///////////////////////////////////////////////////////////////


@runtime_checkable
class CompilerPort(Protocol):
    """Structural contract for a project compiler (Port).

    Any object exposing this surface is a valid compiler — no inheritance
    required. ``adapters.BaseCompiler`` and its subclasses conform to it.

    Used by: CompilerFactory return type, CompilationResult.compiler_instance.
    """

    @property
    def config(self) -> CompilerConfig:
        """Configuration the compiler was built with."""
        ...

    @property
    def zip_needed(self) -> bool:
        """Whether the compiled output must be zipped."""
        ...

    def compile(self, console: bool = True) -> None:
        """Compile the project. Raises CompilationError on failure."""
        ...

    def get_compiler_name(self) -> str:
        """Human-readable compiler name."""
        ...


@runtime_checkable
class UploaderPort(Protocol):
    """Structural contract for an artifact uploader (Port).

    Any object exposing this surface is a valid uploader — no inheritance
    required. ``adapters.BaseUploader`` and its subclasses conform to it.

    Used by: UploaderFactory return type, UploaderService boundaries.
    """

    def upload(self, source_path: Path, destination: str) -> None:
        """Upload a file or directory. Raises UploadError on failure."""
        ...

    def download(self, remote_source: str, local_dir: Path) -> None:
        """Download a remote tree into ``local_dir``. Raises UploadError."""
        ...

    def get_uploader_name(self) -> str:
        """Human-readable uploader name."""
        ...


@runtime_checkable
class ReleaserPort(Protocol):
    """Structural contract for a secure-release packager (Port).

    Any object exposing this surface is a valid releaser — no inheritance
    required. ``adapters.BaseReleaser`` and its subclasses conform to it.

    Used by: ReleaserFactory return type, ReleaseService boundaries.
    """

    def release(
        self,
        bundle_dir: Path,
        app_name: str,
        version: str,
        repo_dir: Path,
        *,
        patch: bool = True,
    ) -> Path:
        """Build and sign the local TUF repository for ``bundle_dir``.

        Returns the path to the produced ``repository/`` tree.
        Raises ReleaseError on failure.
        """
        ...

    def init_keys(self, app_name: str, repo_dir: Path, keys_dir: Path) -> bool:
        """Initialise clés TUF + squelette repo. Idempotent.

        Returns True si init effectuée, False si clés déjà présentes (skip).
        Raises ReleaseError / SigningKeyError on failure.
        """
        ...

    def refresh_expiration(
        self,
        app_name: str,
        repo_dir: Path,
        keys_dir: Path,
        *,
        roles: tuple[str, ...] = ...,
        days: int | None = None,
    ) -> Path:
        """Re-sign metadata to push out expiration without a new release.

        Returns the local repository directory.
        Raises ReleaseError / SigningKeyError on failure.
        """
        ...

    def get_releaser_name(self) -> str:
        """Human-readable releaser name."""
        ...


@runtime_checkable
class InstallerPort(Protocol):
    """Structural contract for a first-deployment installer builder (Port).

    Any object exposing this surface is a valid installer builder — no
    inheritance required. ``adapters.BaseInstaller`` and its subclasses
    conform to it.

    Used by: InstallerFactory return type, InstallerService boundaries.
    """

    def build(
        self, bundle_dir: Path, app_name: str, version: str, output_dir: Path
    ) -> Path:
        """Build the installer executable. Raises InstallerError on failure."""
        ...

    def get_installer_name(self) -> str:
        """Human-readable installer backend name."""
        ...


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "FilePath",
    "CompilerName",
    "RepoDestination",
    "ReleaseDestination",
    "ReleaseTarget",
    "IncludeFiles",
    "JsonMap",
    "CompilerPort",
    "UploaderPort",
    "ReleaserPort",
    "InstallerPort",
]
