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
import subprocess
import sys
from pathlib import Path

# Local imports
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
        config: CompilerConfig with project settings
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: object) -> None:
        """
        Initialize Nuitka compiler.

        Args:
            config: CompilerConfig instance with project settings
        """
        super().__init__(config)  # type: ignore[arg-type]
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
            self.validate_config()
            self.prepare_output_directory()

            # Choose output mode
            from ..utils.compiler_utils import CompilerUtils

            onefile = CompilerUtils.check_onefile_mode()
            self._zip_needed = not onefile

            # Build Nuitka command
            output_dir = str(self.config.output_folder)
            output_name = self.config.project_name
            cmd = [
                sys.executable,
                "-m",
                "nuitka",
                self.config.main_file,
                "--follow-imports",
                f"--output-dir={output_dir}",
                f"--output-filename={output_name}",
            ]

            if onefile:
                cmd.append("--onefile")
            else:
                cmd.append("--standalone")

            # Windows console behavior
            if sys.platform == "win32" and not console:
                cmd.append("--windows-disable-console")

            # Icon support
            if self.config.icon:
                cmd.append(f"--windows-icon-from-ico={self.config.icon}")

            # Include data files
            for file in self.config.include_files.get("files", []):
                cmd.append(f"--include-data-file={file}={Path(file).name}")

            for folder in self.config.include_files.get("folders", []):
                cmd.append(f"--include-data-dir={folder}={folder}")

            # Include packages/modules
            for pkg in self.config.packages:
                cmd.append(f"--include-package={pkg}")

            for mod in self.config.includes:
                cmd.append(f"--include-module={mod}")

            # Exclude modules
            for mod in self.config.excludes:
                cmd.append(f"--nofollow-import-to={mod}")

            # Run Nuitka
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True
            )  # noqa: S603
            if result.returncode != 0:
                error_detail = result.stderr or result.stdout
                raise CompilationError(
                    f"Nuitka compilation failed: {error_detail.strip()}"
                )

        except Exception as e:
            if isinstance(e, CompilationError):
                raise
            raise CompilationError(f"Nuitka compilation failed: {str(e)}") from e
