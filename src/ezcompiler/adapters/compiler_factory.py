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
# Standard library imports
import importlib.util

# Local imports
from ..shared import CompilerConfig
from ..shared.exceptions import CompilationError
from ..types import CompilerPort

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_COMPILER_PACKAGES: dict[str, tuple[str, str]] = {
    "Cx_Freeze": ("cx_Freeze", "ezcompiler[cx-freeze]"),
    "PyInstaller": ("PyInstaller", "ezcompiler[pyinstaller]"),
    "Nuitka": ("nuitka", "ezcompiler[nuitka]"),
}

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CompilerFactory:
    """Factory class for creating compiler instances."""

    @staticmethod
    def _check_compiler_available(compiler_name: str) -> None:
        """
        Verify the compiler package is installed, raise a clear error if not.

        Args:
            compiler_name: Canonical compiler name (Cx_Freeze, PyInstaller, Nuitka)

        Raises:
            CompilationError: If the package is not installed, with install hint
        """
        package, extra = _COMPILER_PACKAGES[compiler_name]
        if importlib.util.find_spec(package) is None:
            raise CompilationError(
                f"{compiler_name} is not installed. "
                f"Install it with: pip install {extra}"
            )

    @staticmethod
    def create_compiler(config: CompilerConfig, compiler_name: str) -> CompilerPort:
        """
        Create a compiler instance from its name.

        Args:
            config: Compiler configuration to inject
            compiler_name: Compiler name (Cx_Freeze, PyInstaller, Nuitka)

        Returns:
            CompilerPort: Concrete compiler instance (satisfies the Port)

        Raises:
            CompilationError: If compiler name is unsupported or package not installed
        """
        normalized_name = compiler_name.strip()

        if normalized_name == "Cx_Freeze":
            CompilerFactory._check_compiler_available("Cx_Freeze")
            from ._cx_freeze_compiler import CxFreezeCompiler

            return CxFreezeCompiler(config=config)

        if normalized_name == "PyInstaller":
            CompilerFactory._check_compiler_available("PyInstaller")
            from ._pyinstaller_compiler import PyInstallerCompiler

            return PyInstallerCompiler(config=config)

        if normalized_name == "Nuitka":
            CompilerFactory._check_compiler_available("Nuitka")
            from ._nuitka_compiler import NuitkaCompiler

            return NuitkaCompiler(config=config)

        raise CompilationError(f"Unsupported compiler: {normalized_name}")

    @staticmethod
    def create_from_config(config: CompilerConfig) -> CompilerPort:
        """
        Create a compiler instance using the config default compiler.

        Args:
            config: Compiler configuration

        Returns:
            CompilerPort: Concrete compiler instance (satisfies the Port)

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
