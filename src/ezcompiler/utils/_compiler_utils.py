# ///////////////////////////////////////////////////////////////
# COMPILER_UTILS - Compiler-specific utility functions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Compiler utilities - Compiler-specific utility functions for EzCompiler.

This module provides specialized utility functions for compiler operations,
including configuration validation, output directory preparation, and include
files formatting. Uses thematic utils (FileUtils, ValidationUtils) internally.

Utils layer can only use DEBUG and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Local imports
from ..shared import CompilerConfig
from ..shared.exceptions.utils import (
    CompilerConfigValidationError,
    MainFileNotFoundError,
    OutputDirectoryError,
)
from ._file_utils import FileUtils

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CompilerUtils:
    """
    Utility class for compiler-specific operations.

    Provides static methods for compiler-related tasks such as configuration
    validation, output directory preparation, and include files formatting.
    Uses thematic utils (FileUtils, ValidationUtils) internally.

    Example:
        >>> config = CompilerConfig(...)
        >>> CompilerUtils.validate_compiler_config(config)
        >>> CompilerUtils.prepare_compiler_output_directory(config)
        >>> files = CompilerUtils.format_include_files_data(config)
    """

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    # Revalidation volontaire (défense en profondeur) : CompilerConfig est une dataclass
    # mutable, donc l'état validé par __post_init__ peut avoir changé entre la construction
    # et l'appel à compile(). Ce contrôle est rejoué juste avant la compilation — ce n'est
    # pas une duplication morte mais un garde-fou au point d'usage.
    @staticmethod
    def validate_compiler_config(config: CompilerConfig) -> None:
        """
        Validate configuration for compilation.

        Checks that all required configuration fields are present
        and valid (main file exists, output folder is set).

        Args:
            config: CompilerConfig instance to validate

        Raises:
            MainFileNotFoundError: If main file doesn't exist or is required but missing
            OutputDirectoryError: If output folder is not set

        Note:
            Uses FileUtils for file existence checks.

        Example:
            >>> config = CompilerConfig(...)
            >>> CompilerUtils.validate_compiler_config(config)
        """
        if not config.main_file:
            raise CompilerConfigValidationError("Main file is required")

        main_file_path = Path(config.main_file)
        if not main_file_path.exists() or not main_file_path.is_file():
            raise MainFileNotFoundError(f"Main file not found: {config.main_file}")

        if not config.output_folder:
            raise OutputDirectoryError("Output folder is required")

    # ////////////////////////////////////////////////
    # PREPARATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def prepare_compiler_output_directory(config: CompilerConfig) -> None:
        """
        Prepare the output directory for compilation.

        Creates the output directory if it doesn't exist, including
        any parent directories as needed.

        Args:
            config: CompilerConfig instance with output_folder path

        Note:
            Uses FileUtils.create_directory_if_not_exists() internally.

        Example:
            >>> config = CompilerConfig(..., output_folder=Path("dist"))
            >>> CompilerUtils.prepare_compiler_output_directory(config)
        """
        FileUtils.create_directory_if_not_exists(config.output_folder)

    # ////////////////////////////////////////////////
    # DATA FORMATTING METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def format_include_files_data(config: CompilerConfig) -> list[str]:
        """
        Format include files data for compilation.

        Combines individual files and folders from configuration,
        formatting folders with trailing slashes for compatibility
        with different compilers.

        Args:
            config: CompilerConfig instance with include_files

        Returns:
            list[str]: List of formatted include paths

        Note:
            Files are included as-is, folders are formatted with
            trailing slashes for Cx_Freeze compatibility.

        Example:
            >>> config.include_files = {
            ...     "files": ["config.yaml"],
            ...     "folders": ["lib", "assets"]
            ... }
            >>> files = CompilerUtils.format_include_files_data(config)
            >>> print(files)
            ['config.yaml', 'lib/', 'assets/']
        """
        files = config.include_files.get("files", [])
        folders = [f"{folder}/" for folder in config.include_files.get("folders", [])]
        return files + folders

    # ////////////////////////////////////////////////
    # COMPILER-SPECIFIC HELPERS
    # ////////////////////////////////////////////////

    @staticmethod
    def get_windows_base_for_console(console: bool) -> str | None:
        """
        Get Windows base executable type based on console setting.

        Args:
            console: Whether to show console window

        Returns:
            str | None: "Win32GUI" if console=False on Windows, None otherwise

        Note:
            Used by Cx_Freeze to determine executable base type.

        Example:
            >>> base = CompilerUtils.get_windows_base_for_console(False)
            >>> print(base)
            'Win32GUI'  # On Windows
        """
        import sys

        if sys.platform == "win32" and not console:
            return "Win32GUI"
        return None

    @staticmethod
    def check_onefile_mode() -> bool:
        """
        Check if onefile mode is requested via command-line arguments.

        Returns:
            bool: True if --onefile is in sys.argv, False otherwise

        Note:
            Used by PyInstaller and Nuitka to determine output format.

        Example:
            >>> # When run with: python script.py --onefile
            >>> is_onefile = CompilerUtils.check_onefile_mode()
            >>> print(is_onefile)
            True
        """
        import sys

        return "--onefile" in sys.argv
