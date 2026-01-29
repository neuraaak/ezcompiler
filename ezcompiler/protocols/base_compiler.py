# ///////////////////////////////////////////////////////////////
# BASE_COMPILER - Abstract compiler interface
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base compiler - Abstract base class for EzCompiler compilers.

This module defines the abstract base class that all compiler implementations
must inherit from, establishing the interface and common functionality for
project compilation operations.

Protocols layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from abc import ABC, abstractmethod

# Local imports
from ..shared.compiler_config import CompilerConfig

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
            Uses CompilerUtils internally.
        """
        from ..utils.compiler_utils import CompilerUtils

        CompilerUtils.validate_compiler_config(self.config)

    def prepare_output_directory(self) -> None:
        """
        Prepare the output directory for compilation.

        Creates the output directory if it doesn't exist, including
        any parent directories as needed.

        Note:
            Called before compilation to ensure output directory is ready.
            Uses CompilerUtils internally.
        """
        from ..utils.compiler_utils import CompilerUtils

        CompilerUtils.prepare_compiler_output_directory(self.config)

    def get_include_files_data(self) -> list[str]:
        """
        Get formatted include files data for compilation.

        Combines individual files and folders from configuration,
        formatting folders with trailing slashes for compatibility.

        Returns:
            list[str]: List of formatted include paths

        Note:
            Uses CompilerUtils internally.

        Example:
            >>> config.include_files = {
            ...     "files": ["config.yaml"],
            ...     "folders": ["lib", "assets"]
            ... }
            >>> files = compiler.get_include_files_data()
            >>> print(files)
            ['config.yaml', 'lib/', 'assets/']
        """
        from ..utils.compiler_utils import CompilerUtils

        return CompilerUtils.format_include_files_data(self.config)
