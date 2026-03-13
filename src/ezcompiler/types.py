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
from typing import TypeAlias

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

__all__ = [
    "FilePath",
    "CompilerName",
    "UploadTarget",
    "IncludeFiles",
    "JsonMap",
]
