# ///////////////////////////////////////////////////////////////
# COMPILER_FACTORY - Compiler factory for creating compiler instances
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Compiler factory - Factory for creating compiler instances.

This module provides a centralized factory for creating compiler
instances based on type and configuration.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ..shared import CompilerConfig
from ..shared.exceptions import CompilationError
from ._cx_freeze_compiler import CxFreezeCompiler
from ._nuitka_compiler import NuitkaCompiler
from ._pyinstaller_compiler import PyInstallerCompiler
from .base_compiler import BaseCompiler

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CompilerFactory:
    """Factory class for creating compiler instances."""

    @staticmethod
    def create_compiler(config: CompilerConfig, compiler_name: str) -> BaseCompiler:
        """
        Create a compiler instance from its name.

        Args:
            config: Compiler configuration to inject
            compiler_name: Compiler name (Cx_Freeze, PyInstaller, Nuitka)

        Returns:
            BaseCompiler: Concrete compiler instance

        Raises:
            CompilationError: If compiler name is unsupported
        """
        normalized_name = compiler_name.strip()

        if normalized_name == "Cx_Freeze":
            return CxFreezeCompiler(config=config)
        if normalized_name == "PyInstaller":
            return PyInstallerCompiler(config=config)
        if normalized_name == "Nuitka":
            return NuitkaCompiler(config=config)

        raise CompilationError(f"Unsupported compiler: {normalized_name}")

    @staticmethod
    def create_from_config(config: CompilerConfig) -> BaseCompiler:
        """
        Create a compiler instance using the config default compiler.

        Args:
            config: Compiler configuration

        Returns:
            BaseCompiler: Concrete compiler instance

        Raises:
            CompilationError: If config compiler is unsupported
        """
        compiler_name = config.compiler if config.compiler != "auto" else "Cx_Freeze"
        return CompilerFactory.create_compiler(
            config=config, compiler_name=compiler_name
        )

    @staticmethod
    def get_supported_compilers() -> list[str]:
        """Return the list of supported compiler names."""
        return ["Cx_Freeze", "PyInstaller", "Nuitka"]
