# ///////////////////////////////////////////////////////////////
# NUITKA_COMPILER - Nuitka compiler implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Nuitka compiler - Nuitka compiler implementation for EzCompiler.

This module provides a compiler implementation using Nuitka, which
can generate either a standalone folder or a single-file executable.

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
from ..shared import CompilerConfig
from ..shared.exceptions import CompilationError
from .base_compiler import BaseCompiler

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class NuitkaCompiler(BaseCompiler):
    """
    Nuitka compiler implementation.

    Handles project compilation using Nuitka, which can produce a
    standalone folder or a single-file executable depending on options.

    Attributes:
        _config: CompilerConfig with project settings
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: CompilerConfig) -> None:
        """
        Initialize Nuitka compiler.

        Args:
            config: CompilerConfig instance with project settings
        """
        super().__init__(config)
        self._zip_needed = True

    # ////////////////////////////////////////////////
    # COMPILER INTERFACE METHODS
    # ////////////////////////////////////////////////

    def get_compiler_name(self) -> str:
        """
        Get the name of this compiler.

        Returns:
            str: Display name "Nuitka"
        """
        return "Nuitka"

    def compile(self, console: bool = True) -> None:
        """
        Compile the project using Nuitka.

        Validates configuration, prepares output directory, builds Nuitka
        options from project settings, and runs compilation.

        Args:
            console: Whether to show console window (default: True)

        Raises:
            CompilationError: If compilation fails
        """
        try:
            # Validate and prepare
            self._validate_config()
            self._prepare_output_directory()

            # Choose output mode
            from ..utils._compiler_utils import CompilerUtils

            onefile = CompilerUtils.check_onefile_mode()
            self._zip_needed = not onefile

            # Build Nuitka command
            output_dir = str(self._config.output_folder)
            output_name = self._config.project_name
            cmd = [
                sys.executable,
                "-m",
                "nuitka",
                self._config.main_file,
                "--assume-yes-for-downloads",
                "--remove-output",
                f"--output-dir={output_dir}",
                f"--output-filename={output_name}",
            ]

            if onefile:
                cmd.append("--onefile")
            else:
                cmd.append("--standalone")

            # Windows: use MSVC backend (MinGW64 not supported on Python 3.13+)
            if sys.platform == "win32":
                cmd.append("--msvc=latest")
                if not console:
                    cmd.append("--windows-disable-console")

            # Icon support
            if self._config.icon:
                cmd.append(f"--windows-icon-from-ico={self._config.icon}")

            # Include data files
            for file in self._config.include_files.get("files", []):
                cmd.append(f"--include-data-file={file}={Path(file).name}")

            for folder in self._config.include_files.get("folders", []):
                cmd.append(f"--include-data-dir={folder}={folder}")

            # Include packages and modules (both use --include-module to avoid
            # crashes with stdlib built-in modules that have no __path__)
            for mod in self._config.packages + self._config.includes:
                cmd.append(f"--include-module={mod}")

            # Exclude modules
            for mod in self._config.excludes:
                cmd.append(f"--nofollow-import-to={mod}")

            # Windows metadata
            if sys.platform == "win32":
                cmd.append(f"--product-name={self._config.project_name}")
                cmd.append(f"--product-version={self._config.version}")
                if self._config.company_name:
                    cmd.append(f"--company-name={self._config.company_name}")
                if self._config.project_description:
                    cmd.append(f"--file-description={self._config.project_description}")

            # Advanced options
            if self._config.debug:
                cmd.append("--debug")

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

            # Run Nuitka
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
            if result.returncode != 0:
                raw_output = result.stderr or result.stdout
                error_detail = self._extract_error_summary(raw_output)
                raise CompilationError(f"Nuitka compilation failed: {error_detail}")

            # Flatten output: Nuitka --standalone creates a subfolder
            # named "{main_stem}.dist" inside output-dir. Move its contents
            # up to output_folder so the layout matches Cx_Freeze.
            if not onefile:
                main_stem = Path(self._config.main_file).stem
                nested = self._config.output_folder / f"{main_stem}.dist"
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
            raise CompilationError(f"Nuitka compilation failed: {str(e)}") from e
