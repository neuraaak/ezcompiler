# ///////////////////////////////////////////////////////////////
# COMPILER_SERVICE - Compilation orchestration service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Compiler service - Compilation orchestration service for EzCompiler.

This module provides the CompilerService class that orchestrates project
compilation using different compiler backends (Cx_Freeze, PyInstaller, Nuitka).

Services layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Literal

# Third-party imports
from InquirerPy.resolver import prompt

# Local imports
from ..adapters import (
    BaseCompiler,
    CompilerFactory,
)
from ..shared.compilation_result import CompilationResult
from ..shared.compiler_config import CompilerConfig
from ..shared.exceptions import CompilationError, ConfigurationError
from ..utils.validators import validate_compiler_name
from ..utils.zip_utils import ZipUtils

# ///////////////////////////////////////////////////////////////
# TYPE ALIASES
# ///////////////////////////////////////////////////////////////

CompilerName = Literal["Cx_Freeze", "PyInstaller", "Nuitka", "auto"]

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CompilerService:
    """
    Compilation orchestration service.

    Orchestrates project compilation using different compiler backends.
    Handles compiler selection, validation, and execution.

    Attributes:
        config: CompilerConfig instance with project settings

    Example:
        >>> config = CompilerConfig(...)
        >>> service = CompilerService(config)
        >>> result = service.compile(console=True, compiler="PyInstaller")
        >>> print(result.zip_needed)
        False
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: CompilerConfig) -> None:
        """
        Initialize the compiler service.

        Args:
            config: CompilerConfig instance with project settings

        Raises:
            ConfigurationError: If config is None or invalid
        """
        if not config:
            raise ConfigurationError("CompilerConfig is required")

        self.config = config
        self._compiler_instance: BaseCompiler | None = None

    # ////////////////////////////////////////////////
    # COMPILATION METHODS
    # ////////////////////////////////////////////////

    def compile(
        self,
        console: bool = True,
        compiler: CompilerName | None = None,
    ) -> CompilationResult:
        """
        Compile the project using specified or auto-selected compiler.

        Validates configuration, selects compiler if not specified, and
        executes compilation. Returns result with zip_needed flag.

        Args:
            console: Whether to show console window (default: True)
            compiler: Compiler to use or None for auto-selection
                - "Cx_Freeze": Creates directory with dependencies
                - "PyInstaller": Creates single executable
                - "Nuitka": Creates standalone folder or single executable
                - "auto" or None: Prompt user for choice or use config default

        Returns:
            CompilationResult: Result with zip_needed flag and compiler instance

        Raises:
            ConfigurationError: If project not initialized
            CompilationError: If compilation fails

        Example:
            >>> service = CompilerService(config)
            >>> result = service.compile(console=False, compiler="PyInstaller")
            >>> if result.zip_needed:
            ...     # Create ZIP archive
        """
        try:
            # Determine compiler choice
            compiler_choice = self._determine_compiler(compiler)

            # Validate compiler choice
            if not validate_compiler_name(compiler_choice):
                raise CompilationError(f"Invalid compiler: {compiler_choice}")

            # Ensure output directory exists (moved out of CompilerConfig to avoid side effects)
            self.config.output_folder.mkdir(parents=True, exist_ok=True)

            # Create and execute compiler
            self._compiler_instance = self._create_compiler(compiler_choice)
            self._compiler_instance.compile(console=console)

            return CompilationResult(
                zip_needed=self._compiler_instance.zip_needed,
                compiler_name=compiler_choice,
                compiler_instance=self._compiler_instance,
            )
        except CompilationError:
            raise
        except ConfigurationError:
            raise
        except Exception as e:
            raise CompilationError(f"Compilation failed: {str(e)}") from e

    # ////////////////////////////////////////////////
    # PRIVATE HELPER METHODS
    # ////////////////////////////////////////////////

    def _determine_compiler(self, compiler: CompilerName | None) -> str:
        """
        Determine which compiler to use.

        Args:
            compiler: Explicit compiler choice or None/auto

        Returns:
            str: Compiler name to use

        Note:
            Priority: explicit choice > config.compiler > interactive prompt
        """
        # Use explicit choice if provided
        if compiler and compiler != "auto":
            return compiler

        # Use config default if set and not auto
        if self.config.compiler and self.config.compiler != "auto":
            return self.config.compiler

        # Interactive prompt for user choice
        return self._choose_compiler_interactively()

    def _choose_compiler_interactively(
        self, argv_flags: list[str] | None = None
    ) -> str:
        """
        Prompt user to choose a compiler interactively.

        Checks command-line flags first, then prompts if needed.

        Args:
            argv_flags: List of CLI flags to check. Defaults to sys.argv.
                Inject a custom list in tests to avoid reading global state.

        Returns:
            str: Chosen compiler name

        Raises:
            CompilationError: If selection fails
        """
        flags = argv_flags if argv_flags is not None else sys.argv
        try:
            # Check command line arguments first
            if "-cxf" in flags:
                return "Cx_Freeze"
            elif "-pyi" in flags:
                return "PyInstaller"
            elif "-nka" in flags:
                return "Nuitka"

            # Prompt user for choice
            questions = [
                {
                    "type": "list",
                    "name": "compiler",
                    "message": "Which compiler to use?",
                    "choices": ["Cx_Freeze", "PyInstaller", "Nuitka"],
                    "default": "Cx_Freeze",
                }
            ]

            result = prompt(questions)
            return result["compiler"]  # type: ignore[return-value]

        except Exception as e:
            raise CompilationError(f"Failed to choose compiler: {e}") from e

    def _create_compiler(self, compiler_name: str) -> BaseCompiler:
        """
        Create compiler instance for the specified compiler.

        Args:
            compiler_name: Name of the compiler to create

        Returns:
            BaseCompiler: Compiler instance

        Raises:
            CompilationError: If compiler name is unsupported
        """
        return CompilerFactory.create_compiler(
            config=self.config,
            compiler_name=compiler_name,
        )

    def zip_artifact(
        self,
        output_path: str | Path,
        progress_callback: Callable[[str, int], None] | None = None,
    ) -> None:
        """
        Create ZIP archive of the compiled output.

        Args:
            output_path: Path for the output ZIP file
            progress_callback: Optional callback(filename, progress) for progress updates

        Raises:
            ZipError: If ZIP creation fails
        """
        ZipUtils.create_zip_archive(
            source_path=self.config.output_folder,
            output_path=output_path,
            progress_callback=progress_callback,
        )

    # ////////////////////////////////////////////////
    # PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def compiler_instance(self) -> BaseCompiler | None:
        """
        Get the current compiler instance.

        Returns:
            BaseCompiler | None: Current compiler instance or None if not compiled yet
        """
        return self._compiler_instance
