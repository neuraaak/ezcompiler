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
    - Multi-compiler support (Cx_Freeze, PyInstaller)
    - Version file generation for Windows executables
    - Project packaging to ZIP archives
    - Upload backends (disk and HTTP server)
    - Template-based file generation (configuration, setup, version)
    - File utilities (validation, ZIP operations)
    - CLI for automation and batch operations

**Main Modules:**
    - core: Configuration and exception hierarchy
    - compilers: Concrete compiler implementations
    - generators: Setup and version file generators
    - templates: Template management and processing
    - uploaders: Upload backends (disk, server)
    - utils: File, ZIP, and validation utilities
    - cli: Command-line interface
    - helper: Template-based file generation helpers

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
from .compilers import BaseCompiler, CxFreezeCompiler, PyInstallerCompiler
from .core import (
    CompilationError,
    CompilerConfig,
    ConfigurationError,
    EzCompilerError,
)
from .ezcompiler import EzCompiler
from .generators import SetupGenerator, VersionGenerator
from .helper import Helper
from .templates import TemplateManager, TemplateProcessor
from .uploaders import BaseUploader, DiskUploader, ServerUploader, UploaderFactory
from .utils import FileUtils, ValidationUtils, ZipUtils

# ///////////////////////////////////////////////////////////////
# METADATA INFORMATION
# ///////////////////////////////////////////////////////////////

__version__ = "1.0.1"
__author__ = "Neuraaak"
__maintainer__ = "Neuraaak"
__description__ = "Project compilation and distribution framework for Python"
__python_requires__ = ">=3.10"
__keywords__ = ["compilation", "packaging", "distribution", "cx_freeze", "pyinstaller"]
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
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

Config = CompilerConfig
"""Type alias for CompilerConfig.

Use this type when you want to annotate a variable that represents
a compiler configuration.

Example:
    >>> from ezcompiler import EzCompiler, Config
    >>> config: Config = CompilerConfig(...)
    >>> compiler = EzCompiler(config)
"""

Compiler = BaseCompiler
"""Type alias for BaseCompiler.

Use this type when you want to annotate a variable that represents
a compiler implementation.

Example:
    >>> from ezcompiler import Compiler
    >>> compiler: Compiler = CxFreezeCompiler(config)
    >>> compiler.compile()
"""

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Main orchestration class
    "EzCompiler",
    # Configuration and exceptions
    "CompilerConfig",
    "Config",
    "EzCompilerError",
    "CompilationError",
    "ConfigurationError",
    # Compiler implementations
    "BaseCompiler",
    "Compiler",
    "CxFreezeCompiler",
    "PyInstallerCompiler",
    # Generators
    "VersionGenerator",
    "SetupGenerator",
    # Templates
    "TemplateManager",
    "TemplateProcessor",
    # Uploaders
    "BaseUploader",
    "DiskUploader",
    "ServerUploader",
    "UploaderFactory",
    # Utilities
    "FileUtils",
    "ZipUtils",
    "ValidationUtils",
    "Helper",
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
