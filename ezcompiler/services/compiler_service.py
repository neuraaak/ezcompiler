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
from typing import Literal

# Third-party imports
from InquirerPy.resolver import prompt

# Local imports
from ..protocols import (
    BaseCompiler,
    CxFreezeCompiler,
    NuitkaCompiler,
    PyInstallerCompiler,
)
from ..shared.compiler_config import CompilerConfig
from ..shared.exceptions import CompilationError, ConfigurationError
from ..utils.validators import validate_compiler_name

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

    def _choose_compiler_interactively(self) -> str:
        """
        Prompt user to choose a compiler interactively.

        Checks command-line arguments first, then prompts if needed.

        Returns:
            str: Chosen compiler name

        Raises:
            CompilationError: If selection fails
        """
        try:
            # Check command line arguments first
            if "-cxf" in sys.argv:
                return "Cx_Freeze"
            elif "-pyi" in sys.argv:
                return "PyInstaller"
            elif "-nka" in sys.argv:
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
        if compiler_name == "Cx_Freeze":
            return CxFreezeCompiler(config=self.config)
        elif compiler_name == "PyInstaller":
            return PyInstallerCompiler(config=self.config)
        elif compiler_name == "Nuitka":
            return NuitkaCompiler(config=self.config)
        else:
            raise CompilationError(f"Unsupported compiler: {compiler_name}")

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


# ///////////////////////////////////////////////////////////////
# RESULT CLASSES
# ///////////////////////////////////////////////////////////////


class CompilationResult:
    """
    Result of a compilation operation.

    Contains information about the compilation result, including whether
    the output needs to be zipped and the compiler instance used.

    Attributes:
        zip_needed: Whether the compiled output needs to be zipped
        compiler_name: Name of the compiler used
        compiler_instance: The compiler instance that performed the compilation

    Example:
        >>> result = service.compile(compiler="PyInstaller")
        >>> if result.zip_needed:
        ...     # Create ZIP archive
    """

    def __init__(
        self,
        zip_needed: bool,
        compiler_name: str,
        compiler_instance: BaseCompiler,
    ) -> None:
        """
        Initialize compilation result.

        Args:
            zip_needed: Whether output needs to be zipped
            compiler_name: Name of compiler used
            compiler_instance: Compiler instance that performed compilation
        """
        self.zip_needed = zip_needed
        self.compiler_name = compiler_name
        self.compiler_instance = compiler_instance
