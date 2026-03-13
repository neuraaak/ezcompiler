# ///////////////////////////////////////////////////////////////
# EZCOMPILER - Main Module
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
EzCompiler - Project compilation and distribution framework.

EzCompiler is a comprehensive Python framework for project compilation, version
file generation, packaging, and distribution, with a clean and typed API suitable
for professional and industrial Python applications.

**Main Features:**
    - Multi-compiler support (Cx_Freeze, PyInstaller, Nuitka)
    - Version file generation for Windows executables
    - Project packaging to ZIP archives
    - Upload backends (disk and HTTP server)
    - Template-based file generation (configuration, setup, version)
    - File utilities (validation, ZIP operations)
    - CLI for automation and batch operations

**Architecture (v2.0.0):**
    - interfaces: Public interfaces (CLI, Python API)
    - services: Business logic services
    - adapters: Compiler protocol implementations
    - utils: Utility functions and exceptions

**Quick Start:**
    >>> from ezcompiler import EzCompiler, CompilerConfig
    >>> config = CompilerConfig(
    ...     version="1.0.0",
    ...     project_name="MyProject",
    ...     main_file="main.py",
    ...     include_files={"files": [], "folders": []},
    ...     output_folder="dist",
    ... )
    >>> compiler = EzCompiler(config)
    >>> compiler.compile_project()
    >>> compiler.zip_compiled_project()
    >>> compiler.upload_to_repo("disk", "releases/")
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Local imports
from .interfaces import EzCompiler
from .shared import (
    CompilationError,
    CompilerConfig,
    ConfigurationError,
    EzCompilerError,
    FileOperationError,
    TemplateError,
    UploadError,
    VersionError,
)
from .types import CompilerName, FilePath, IncludeFiles, JsonMap, UploadTarget
from .version import __version__

# ///////////////////////////////////////////////////////////////
# METADATA INFORMATION
# ///////////////////////////////////////////////////////////////

__author__ = "Neuraaak"
__maintainer__ = "Neuraaak"
__description__ = "Project compilation and distribution framework for Python"
__python_requires__ = ">=3.10"
__keywords__ = [
    "compilation",
    "packaging",
    "distribution",
    "cx_freeze",
    "pyinstaller",
    "nuitka",
]
__url__ = "https://github.com/neuraaak/ezcompiler"
__repository__ = "https://github.com/neuraaak/ezcompiler"

# ///////////////////////////////////////////////////////////////
# PYTHON VERSION CHECK
# ///////////////////////////////////////////////////////////////

if sys.version_info < (3, 10):  # noqa: UP036
    raise RuntimeError(
        f"EzCompiler {__version__} requires Python 3.10 or higher. "
        f"Current version: {sys.version}"
    )

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Main orchestration class
    "EzCompiler",
    # Configuration
    "CompilerConfig",
    # Type aliases
    "FilePath",
    "CompilerName",
    "UploadTarget",
    "IncludeFiles",
    "JsonMap",
    # Exceptions
    "EzCompilerError",
    "CompilationError",
    "ConfigurationError",
    "TemplateError",
    "UploadError",
    "VersionError",
    "FileOperationError",
    # Metadata
    "__version__",
    "__author__",
    "__maintainer__",
    "__python_requires__",
    "__description__",
    "__keywords__",
    "__repository__",
    "__url__",
]
