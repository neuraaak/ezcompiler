# ///////////////////////////////////////////////////////////////
# PROTOCOLS - Compiler protocol implementations
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Protocols module - Compiler protocol implementations for EzCompiler.

This module provides protocol implementations for different packaging
tools (Cx_Freeze, PyInstaller, Nuitka) along with a base abstract class
defining the compiler interface.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .base_compiler import BaseCompiler
from .base_file_writer import BaseFileWriter
from .base_installer import BaseInstaller
from .base_releaser import BaseReleaser
from .base_uploader import BaseUploader
from .compiler_factory import CompilerFactory
from .releaser_factory import ReleaserFactory
from .uploader_factory import UploaderFactory

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Abstract bases and factories only
    "BaseCompiler",
    "BaseUploader",
    "BaseFileWriter",
    "BaseInstaller",
    "BaseReleaser",
    "CompilerFactory",
    "UploaderFactory",
    "ReleaserFactory",
]
