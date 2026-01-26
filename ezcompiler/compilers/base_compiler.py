# ///////////////////////////////////////////////////////////////
# BASE_COMPILER - Abstract compiler interface
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base compiler - Abstract base class for EzCompiler compilers.

This module defines the abstract base class that all compiler implementations
must inherit from, establishing the interface and common functionality for
project compilation operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from abc import ABC, abstractmethod
from pathlib import Path

# Local imports
from ..core.compiler_config import CompilerConfig
from ..core.exceptions import CompilationError

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class BaseCompiler(ABC):
    """
    Abstract base class for project compilers.

    Defines the interface that all compiler implementations must follow.
    Provides common functionality for compilation operations and enforces
    the contract for concrete compiler classes.

    Attributes:
        config: CompilerConfig instance with project settings
        _zip_needed: Whether compilation output needs to be zipped

    Example:
        >>> # Cannot instantiate directly, must subclass
        >>> class MyCompiler(BaseCompiler):
        ...     def compile(self, console=True) -> None:
        ...         pass
        ...     def get_compiler_name(self) -> str:
        ...         return "MyCompiler"
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, config: CompilerConfig) -> None:
        """
        Initialize the compiler with configuration.

        Args:
            config: CompilerConfig instance with project settings
        """
        self.config = config
        self._zip_needed = False

    # ////////////////////////////////////////////////
    # PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def zip_needed(self) -> bool:
        """
        Whether the compiled project needs to be zipped.

        Returns:
            bool: True if output should be zipped, False otherwise

        Note:
            Subclasses set this based on their output format.
            Cx_Freeze sets to True, PyInstaller sets to False.
        """
        return self._zip_needed

    # ////////////////////////////////////////////////
    # ABSTRACT METHODS
    # ////////////////////////////////////////////////

    @abstractmethod
    def compile(self, console: bool = True) -> None:
        """
        Compile the project.

        This method must be implemented by all subclasses to handle
        the actual compilation using their respective compiler.

        Args:
            console: Whether to show console window (default: True)

        Raises:
            CompilationError: If compilation fails

        Example:
            >>> compiler = PyInstallerCompiler(config)
            >>> compiler.compile(console=False)
        """

    @abstractmethod
    def get_compiler_name(self) -> str:
        """
        Get the name of this compiler.

        Returns:
            str: Display name of the compiler

        Example:
            >>> compiler = PyInstallerCompiler(config)
            >>> name = compiler.get_compiler_name()
            >>> print(name)
            'PyInstaller (Empaquetée)'
        """

    # ////////////////////////////////////////////////
    # VALIDATION AND PREPARATION METHODS
    # ////////////////////////////////////////////////

    def validate_config(self) -> None:
        """
        Validate configuration for this compiler.

        Checks that all required configuration fields are present
        and valid (main file exists, output folder is set).

        Raises:
            CompilationError: If validation fails

        Note:
            Called at the start of compile() to ensure config is valid.
        """
        if not self.config.main_file:
            raise CompilationError("Main file is required")

        if not Path(self.config.main_file).exists():
            raise CompilationError(f"Main file not found: {self.config.main_file}")

        if not self.config.output_folder:
            raise CompilationError("Output folder is required")

    def prepare_output_directory(self) -> None:
        """
        Prepare the output directory for compilation.

        Creates the output directory if it doesn't exist, including
        any parent directories as needed.

        Note:
            Called before compilation to ensure output directory is ready.
        """
        self.config.output_folder.mkdir(parents=True, exist_ok=True)

    def get_include_files_data(self) -> list[str]:
        """
        Get formatted include files data for compilation.

        Combines individual files and folders from configuration,
        formatting folders with trailing slashes for compatibility.

        Returns:
            list[str]: List of formatted include paths

        Example:
            >>> config.include_files = {
            ...     "files": ["config.yaml"],
            ...     "folders": ["lib", "assets"]
            ... }
            >>> files = compiler.get_include_files_data()
            >>> print(files)
            ['config.yaml', 'lib/', 'assets/']
        """
        files = self.config.include_files.get("files", [])
        folders = [
            f"{folder}/" for folder in self.config.include_files.get("folders", [])
        ]
        return files + folders

    # ////////////////////////////////////////////////
    # LOGGING HELPER METHODS
    # ////////////////////////////////////////////////

    def log_compilation_start(self, logger: object, printer: object) -> None:
        """
        Log the start of compilation.

        Args:
            logger: Logger instance for file logging
            printer: Printer instance for console output

        Note:
            Logs to both file (logger) and console (printer).
        """
        compiler_name = self.get_compiler_name()
        printer.info(f"Starting compilation with: {compiler_name}")  # type: ignore[attr-defined]
        logger.info(f"Starting compilation with: {compiler_name}")  # type: ignore[attr-defined]

    def log_compilation_success(self, logger: object, printer: object) -> None:
        """
        Log successful compilation.

        Args:
            logger: Logger instance for file logging
            printer: Printer instance for console output

        Note:
            Logs to both file (logger) and console (printer).
        """
        printer.success("Executable file generated successfully")  # type: ignore[attr-defined]
        logger.info("Executable file generated successfully")  # type: ignore[attr-defined]
