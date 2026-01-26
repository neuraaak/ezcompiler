# ///////////////////////////////////////////////////////////////
# PYINSTALLER_COMPILER - PyInstaller compiler implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
PyInstaller compiler - PyInstaller compiler implementation for EzCompiler.

This module provides a compiler implementation using PyInstaller, which
creates a single executable file with all dependencies bundled.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import PyInstaller.__main__

# Local imports
from ..core.exceptions import CompilationError
from .base_compiler import BaseCompiler

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class PyInstallerCompiler(BaseCompiler):
    """
    PyInstaller compiler implementation.

    Handles project compilation using PyInstaller, which creates a
    single executable file with all dependencies bundled. Can generate
    either single-file or directory-based executables.

    Attributes:
        config: CompilerConfig with project settings

    Example:
        >>> config = CompilerConfig(...)
        >>> compiler = PyInstallerCompiler(config)
        >>> compiler.compile(console=True)
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: object) -> None:
        """
        Initialize PyInstaller compiler.

        Args:
            config: CompilerConfig instance with project settings

        Note:
            PyInstaller creates single files, so _zip_needed is set to False.
        """
        super().__init__(config)  # type: ignore[arg-type]
        self._zip_needed = False  # PyInstaller creates single file

    # ////////////////////////////////////////////////
    # COMPILER INTERFACE METHODS
    # ////////////////////////////////////////////////

    def get_compiler_name(self) -> str:
        """
        Get the name of this compiler.

        Returns:
            str: Display name "PyInstaller (Empaquetée)"

        Example:
            >>> compiler = PyInstallerCompiler(config)
            >>> print(compiler.get_compiler_name())
            'PyInstaller (Empaquetée)'
        """
        return "PyInstaller (Empaquetée)"

    def compile(self, console: bool = True) -> None:
        """
        Compile the project using PyInstaller.

        Validates configuration, prepares output directory, builds
        PyInstaller options from project settings, and runs compilation.

        Args:
            console: Whether to show console window (default: True)

        Raises:
            CompilationError: If compilation fails

        Note:
            Adds version file if it exists. Includes all configured
            packages, includes, and applies excludes. Adds files and
            folders with appropriate data paths.

        Example:
            >>> config = CompilerConfig(...)
            >>> compiler = PyInstallerCompiler(config)
            >>> compiler.compile(console=False)
        """
        try:
            # Validate and prepare
            self.validate_config()
            self.prepare_output_directory()

            # Build PyInstaller options
            build_exe_options = [
                self.config.main_file,
                "--windowed",
                "--onefile" if "--onefile" in sys.argv else "--onedir",
                "--clean",
                f"--distpath={self.config.output_folder}",
                f"--name={self.config.project_name}",
            ]

            # Add version file if it exists
            if (
                self.config.version_filename
                and Path(self.config.version_filename).exists()
            ):
                build_exe_options.append(
                    f"--version-file={self.config.version_filename}"
                )

            # Add icon if specified
            if self.config.icon:
                build_exe_options.append(f"--icon={self.config.icon}")

            # Add console option
            if not console:
                build_exe_options.append("--noconsole")

            # Add include files
            for file in self.config.include_files.get("files", []):
                build_exe_options.append(f"--add-data={file};.")

            # Add include folders
            for folder in self.config.include_files.get("folders", []):
                build_exe_options.append(f"--add-data={folder};{folder}")

            # Add hidden imports (packages and includes)
            for pkg in self.config.packages + self.config.includes:
                build_exe_options.append(f"--hidden-import={pkg}")

            # Add excluded modules
            for mod in self.config.excludes:
                build_exe_options.append(f"--exclude-module={mod}")

            # Run PyInstaller
            PyInstaller.__main__.run(build_exe_options)

        except Exception as e:
            raise CompilationError(f"PyInstaller compilation failed: {str(e)}") from e
