# ///////////////////////////////////////////////////////////////
# CX_FREEZE_COMPILER - Cx_Freeze compiler implementation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Cx_Freeze compiler - Cx_Freeze compiler implementation for EzCompiler.

This module provides a compiler implementation using Cx_Freeze, which
creates a directory containing the executable and all dependencies.

Compilation is executed in a subprocess to isolate cx_Freeze stdout/stderr
from the main process (preserving DLP rendering).

Protocols layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Local imports
from ..shared.compiler_config import CompilerConfig
from ..shared.exceptions import CompilationError
from .base_compiler import BaseCompiler

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CxFreezeCompiler(BaseCompiler):
    """
    Cx_Freeze compiler implementation.

    Handles project compilation using Cx_Freeze, which creates a
    directory structure containing the executable and all dependencies.
    The output is typically zipped for distribution.

    Compilation runs in a separate subprocess to prevent cx_Freeze
    output from interfering with the main process display (DLP).

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

    def __init__(self, config: CompilerConfig) -> None:
        """
        Initialize Cx_Freeze compiler.

        Args:
            config: CompilerConfig instance with project settings

        Note:
            Cx_Freeze output requires zipping, so _zip_needed is set to True.
        """
        super().__init__(config)
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
        Compile the project using Cx_Freeze in a subprocess.

        Generates a temporary setup script and executes it in a separate
        process to isolate cx_Freeze stdout/stderr from the main process.

        Args:
            console: Whether to show console window (default: True)

        Raises:
            CompilationError: If compilation fails

        Note:
            On Windows with console=False, uses Win32GUI base.
            Runs in subprocess to preserve DLP rendering in main process.

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

            # Determine base for executable (Win32GUI for no-console on Windows)
            from ..utils.compiler_utils import CompilerUtils

            base = CompilerUtils.get_windows_base_for_console(console)

            # Normalize version to PEP 440 format to avoid setuptools warning
            from packaging.version import Version

            normalized_version = str(Version(self.config.version))

            # Build default build_exe options
            build_exe_options = {
                "include_files": data,
                "packages": self.config.packages,
                "includes": self.config.includes,
                "excludes": self.config.excludes,
                "build_exe": str(self.config.output_folder),
                "optimize": 1 if self.config.optimize else 0,
                "silent_level": 0 if self.config.debug else 1,
            }

            # Merge with compiler-specific options (overrides defaults)
            if self.config.compiler_options:
                build_exe_options.update(self.config.compiler_options)

            # Build setup script configuration
            setup_config = {
                "name": self.config.project_name,
                "version": normalized_version,
                "description": self.config.project_description,
                "author": self.config.author,
                "main_file": self.config.main_file,
                "target_name": f"{self.config.project_name}.exe",
                "base": base,
                "icon": self.config.icon if self.config.icon else None,
                "debug": self.config.debug,
                "build_exe_options": build_exe_options,
            }

            # Generate and execute temporary setup script
            self._run_setup_subprocess(setup_config)

        except Exception as e:
            if isinstance(e, CompilationError):
                raise
            raise CompilationError(f"Cx_Freeze compilation failed: {str(e)}") from e

    # ////////////////////////////////////////////////
    # PRIVATE METHODS
    # ////////////////////////////////////////////////

    _SETUP_SCRIPT = """\
import sys
import json
import warnings
from pathlib import Path

sys.setrecursionlimit(5000)

from cx_Freeze import Executable, setup

config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

# Get build_exe_options directly from config (already merged with compiler_options)
build_exe_options = config["build_exe_options"]

executables = [
    Executable(
        config["main_file"],
        base=config["base"],
        target_name=config["target_name"],
        icon=config["icon"],
        init_script=config.get("init_script"),
    )
]

sys.argv = [sys.argv[0], "build_exe"]

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    setup(
        name=config["name"],
        version=config["version"],
        description=config["description"],
        author=config["author"],
        options={"build_exe": build_exe_options},
        executables=executables,
    )
"""

    def _run_setup_subprocess(self, setup_config: dict[str, Any]) -> None:
        """
        Execute cx_Freeze setup in a subprocess.

        Writes the configuration as a separate JSON file and runs
        a setup script that reads it, avoiding escape issues with
        inline JSON in Python strings.

        Args:
            setup_config: Configuration dictionary for the setup script

        Raises:
            CompilationError: If the subprocess fails
        """
        project_dir = Path(setup_config["main_file"]).resolve().parent

        # Write temporary config JSON file
        config_fd, config_file_str = tempfile.mkstemp(
            suffix="_cx_config.json", dir=str(project_dir)
        )
        config_file = Path(config_file_str)

        # Write temporary setup script
        script_fd, script_file_str = tempfile.mkstemp(
            suffix="_cx_setup.py", dir=str(project_dir)
        )
        script_file = Path(script_file_str)

        try:
            with open(config_fd, "w", encoding="utf-8") as f:
                json.dump(setup_config, f)

            with open(script_fd, "w", encoding="utf-8") as f:
                f.write(self._SETUP_SCRIPT)

            # Run cx_Freeze in subprocess with captured output
            result = subprocess.run(  # noqa: S603
                [sys.executable, str(script_file), str(config_file)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(project_dir),
            )

            if result.returncode != 0:
                raw_output = result.stderr or result.stdout
                error_detail = self.extract_error_summary(raw_output)
                raise CompilationError(f"Cx_Freeze compilation failed: {error_detail}")

        finally:
            script_file.unlink(missing_ok=True)
            config_file.unlink(missing_ok=True)
