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
from .base_uploader import BaseUploader
from .compiler_factory import CompilerFactory
from .cx_freeze_compiler import CxFreezeCompiler
from .disk_file_writer import DiskFileWriter
from .disk_uploader import DiskUploader
from .nuitka_compiler import NuitkaCompiler
from .pyinstaller_compiler import PyInstallerCompiler
from .server_uploader import ServerUploader
from .uploader_factory import UploaderFactory

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Compilers
    "BaseCompiler",
    "CxFreezeCompiler",
    "NuitkaCompiler",
    "PyInstallerCompiler",
    "CompilerFactory",
    # Uploaders
    "BaseUploader",
    "BaseFileWriter",
    "DiskUploader",
    "DiskFileWriter",
    "ServerUploader",
    "UploaderFactory",
]
