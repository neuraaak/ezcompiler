# ///////////////////////////////////////////////////////////////
# PYINSTALLER_COMPILER - PyInstaller compiler implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
PyInstaller compiler - PyInstaller compiler implementation for EzCompiler.

This module provides a compiler implementation using PyInstaller, which
creates a single executable file with all dependencies bundled.

Compilation is executed in a subprocess to isolate PyInstaller stdout/stderr
from the main process (preserving DLP rendering).

Protocols layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
import subprocess
import sys
from pathlib import Path

# Local imports
from ..shared.compiler_config import CompilerConfig
from ..shared.exceptions import CompilationError
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

    Compilation runs in a separate subprocess to prevent PyInstaller
    output from interfering with the main process display (DLP).

    Attributes:
        _config: CompilerConfig with project settings

    Example:
        >>> config = CompilerConfig(...)
        >>> compiler = PyInstallerCompiler(config)
        >>> compiler.compile(console=True)
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: CompilerConfig) -> None:
        """
        Initialize PyInstaller compiler.

        Args:
            config: CompilerConfig instance with project settings

        Note:
            PyInstaller creates single files, so _zip_needed is set to False.
        """
        super().__init__(config)
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
        Compile the project using PyInstaller in a subprocess.

        Validates configuration, prepares output directory, builds
        PyInstaller command-line arguments, and runs compilation in
        a separate process to isolate stdout/stderr from the DLP.

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
            self._validate_config()
            self._prepare_output_directory()

            # Determine output type and ZIP behavior
            from ..utils.compiler_utils import CompilerUtils

            onefile = CompilerUtils.check_onefile_mode()
            self._zip_needed = not onefile

            # Build PyInstaller command
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                self._config.main_file,
                "--console" if console else "--windowed",
                "--onefile" if onefile else "--onedir",
                "--clean",
                "-y",
                f"--distpath={self._config.output_folder}",
                f"--name={self._config.project_name}",
            ]

            # Add version file if it exists
            if (
                self._config.version_filename
                and Path(self._config.version_filename).exists()
            ):
                cmd.append(f"--version-file={self._config.version_filename}")

            # Add icon if specified
            if self._config.icon:
                cmd.append(f"--icon={self._config.icon}")

            # Add include files
            for file in self._config.include_files.get("files", []):
                cmd.append(f"--add-data={file};.")

            # Add include folders
            for folder in self._config.include_files.get("folders", []):
                cmd.append(f"--add-data={folder};{folder}")

            # Add hidden imports (packages and includes)
            for pkg in self._config.packages + self._config.includes:
                cmd.append(f"--hidden-import={pkg}")

            # Add excluded modules
            for mod in self._config.excludes:
                cmd.append(f"--exclude-module={mod}")

            # Advanced options
            if self._config.optimize:
                cmd.append("--optimize=1")

            if self._config.strip:
                cmd.append("--strip")

            if self._config.debug:
                cmd.append("--debug=all")

            # Add compiler-specific options from config.compiler_options
            # Format: {"option-name": "value"} -> --option-name=value
            #         {"option-flag": True} -> --option-flag
            if self._config.compiler_options:
                for key, value in self._config.compiler_options.items():
                    if isinstance(value, bool):
                        if value:  # Only add if True
                            cmd.append(f"--{key}")
                    else:
                        cmd.append(f"--{key}={value}")

            # Run PyInstaller in subprocess with captured output
            result = subprocess.run(  # noqa: S603
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raw_output = result.stderr or result.stdout
                error_detail = self._extract_error_summary(raw_output)
                raise CompilationError(
                    f"PyInstaller compilation failed: {error_detail}"
                )

            # Flatten output: PyInstaller --onedir creates a subfolder
            # named after the project inside distpath. Move its contents
            # up to output_folder so the layout matches Cx_Freeze.
            if not onefile:
                nested = self._config.output_folder / self._config.project_name
                if nested.is_dir():
                    for item in nested.iterdir():
                        dest = self._config.output_folder / item.name
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(item), str(dest))
                    nested.rmdir()

        except Exception as e:
            if isinstance(e, CompilationError):
                raise
            raise CompilationError(f"PyInstaller compilation failed: {str(e)}") from e
