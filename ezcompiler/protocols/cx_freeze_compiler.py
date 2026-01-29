# ///////////////////////////////////////////////////////////////
# CX_FREEZE_COMPILER - Cx_Freeze compiler implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Cx_Freeze compiler - Cx_Freeze compiler implementation for EzCompiler.

This module provides a compiler implementation using Cx_Freeze, which
creates a directory containing the executable and all dependencies.

Protocols layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
from cx_Freeze import Executable, setup

# Local imports
from ..shared.exceptions import CompilationError
from .base_compiler import BaseCompiler

# Increase recursion limit for deep imports
sys.setrecursionlimit(5000)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CxFreezeCompiler(BaseCompiler):
    """
    Cx_Freeze compiler implementation.

    Handles project compilation using Cx_Freeze, which creates a
    directory structure containing the executable and all dependencies.
    The output is typically zipped for distribution.

    Attributes:
        config: CompilerConfig with project settings

    Example:
        >>> config = CompilerConfig(...)
        >>> compiler = CxFreezeCompiler(config)
        >>> compiler.compile(console=True)
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: object) -> None:
        """
        Initialize Cx_Freeze compiler.

        Args:
            config: CompilerConfig instance with project settings

        Note:
            Cx_Freeze output requires zipping, so _zip_needed is set to True.
        """
        super().__init__(config)  # type: ignore[arg-type]
        self._zip_needed = True  # Cx_Freeze always needs zipping

    # ////////////////////////////////////////////////
    # COMPILER INTERFACE METHODS
    # ////////////////////////////////////////////////

    def get_compiler_name(self) -> str:
        """
        Get the name of this compiler.

        Returns:
            str: Display name "Cx_Freeze"

        Example:
            >>> compiler = CxFreezeCompiler(config)
            >>> print(compiler.get_compiler_name())
            'Cx_Freeze'
        """
        return "Cx_Freeze"

    def compile(self, console: bool = True) -> None:
        """
        Compile the project using Cx_Freeze.

        Validates configuration, prepares output directory, and runs
        Cx_Freeze setup with configured options for packages, includes,
        excludes, and executable properties.

        Args:
            console: Whether to show console window (default: True)

        Raises:
            CompilationError: If compilation fails

        Note:
            On Windows with console=False, uses Win32GUI base.
            Sets recursion limit to 5000 for deep import chains.

        Example:
            >>> config = CompilerConfig(...)
            >>> compiler = CxFreezeCompiler(config)
            >>> compiler.compile(console=False)
        """
        try:
            # Validate and prepare
            self.validate_config()
            self.prepare_output_directory()

            # Prepare include files data
            data = self.get_include_files_data()

            # Build executable options
            build_exe_options = {
                "include_files": data,
                "packages": self.config.packages,
                "includes": self.config.includes,
                "excludes": self.config.excludes,
                "build_exe": str(self.config.output_folder),
            }

            # Determine base for executable (Win32GUI for no-console on Windows)
            from ..utils.compiler_utils import CompilerUtils

            base = CompilerUtils.get_windows_base_for_console(console)

            # Create executable configuration
            executables = [
                Executable(
                    self.config.main_file,
                    base=base,
                    target_name=f"{self.config.project_name}.exe",
                    icon=self.config.icon if self.config.icon else None,
                )
            ]

            # Run Cx_Freeze setup
            setup(
                name=self.config.project_name,
                version=self.config.version,
                description=self.config.project_description,
                author=self.config.author,
                options={"build_exe": build_exe_options},
                executables=executables,
            )

        except Exception as e:
            raise CompilationError(f"Cx_Freeze compilation failed: {str(e)}") from e
