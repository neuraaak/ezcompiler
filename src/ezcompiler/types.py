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
from typing import TYPE_CHECKING, Protocol, TypeAlias

if TYPE_CHECKING:
    from ezcompiler.shared._compiler_config import CompilerConfig

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

# ------------------------------------------------
# Path Types
# ------------------------------------------------

FilePath: TypeAlias = str | Path
"""Type alias for file path inputs.

Accepts:
    - str: String file path
    - Path: pathlib.Path object

Used by: CompilerConfig, template loaders, file utilities.
"""

# ------------------------------------------------
# Compiler Types
# ------------------------------------------------

CompilerName: TypeAlias = str
"""Type alias for compiler name selection.

Valid values: "auto", "Cx_Freeze", "PyInstaller", "Nuitka"

Used by: CompilerConfig.compiler, EzCompiler.compile_project().
"""

UploadTarget: TypeAlias = str
"""Type alias for upload destination selection.

Valid values: "disk", "server"

Used by: CompilerConfig.upload_structure, EzCompiler.upload_to_repo().
"""

# ------------------------------------------------
# Configuration Types
# ------------------------------------------------

IncludeFiles: TypeAlias = dict[str, list[str]]
"""Type alias for the include_files configuration structure.

Expected shape::

    {
        "files": ["path/to/file1.txt", "path/to/file2.dll"],
        "folders": ["path/to/assets/", "path/to/data/"],
    }

Used by: CompilerConfig.include_files.
"""

JsonMap: TypeAlias = dict[str, object]
"""Type alias for a generic JSON-serializable mapping.

Used by: configuration parsers, template renderers, YAML/JSON loaders.
"""

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# PROTOCOL TYPES
# Structural contracts for compiler and uploader implementations.
# Using Protocol (not ABC) so conformance is structural — no forced inheritance.
# ///////////////////////////////////////////////////////////////


class CompilerPort(Protocol):
    """Structural contract for compiler implementations."""

    def compile(self, console: bool = True) -> None: ...

    def get_compiler_name(self) -> str: ...

    @property
    def config(self) -> CompilerConfig: ...

    @property
    def zip_needed(self) -> bool: ...


class UploaderPort(Protocol):
    """Structural contract for uploader implementations."""

    def upload(self, source_path: Path, destination: str) -> None: ...

    def get_uploader_name(self) -> str: ...


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "FilePath",
    "CompilerName",
    "UploadTarget",
    "IncludeFiles",
    "JsonMap",
    "CompilerPort",
    "UploaderPort",
]
