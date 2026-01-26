# ///////////////////////////////////////////////////////////////
# HELPER - Template-based file generation helpers
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Helper - Utility functions for generating setup and version files.

This module provides static helper methods for generating setup.py and
version information files using the template system.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Local imports
from .templates import TemplateManager

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class Helper:
    """
    Helper class providing utilities for file generation.

    Provides static methods for generating setup.py and version files
    using the template management system with variable substitution.

    Example:
        >>> Helper.generate_setup_file("setup.py")
        >>> Helper.generate_version_file(
        ...     "version_info.txt",
        ...     "1.0.0",
        ...     "MyCompany",
        ...     "My Application",
        ...     "MyApp"
        ... )
    """

    # ////////////////////////////////////////////////
    # FILE GENERATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def generate_setup_file(file_path: Path | str) -> None:
        """
        Generate a setup.py file at the specified path.

        Creates a setup.py file by loading and writing the setup template
        with no variable substitution (raw template).

        Args:
            file_path: Path where the setup.py file will be created

        Raises:
            OSError: If file writing fails (permissions, disk space, etc.)
            Exception: For other unexpected errors

        Example:
            >>> Helper.generate_setup_file("./setup.py")
        """
        try:
            template_manager = TemplateManager()
            setup_content = template_manager.load_template("setup", "py")

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(setup_content)

        except OSError as e:
            raise OSError(f"Failed to write setup file to {file_path}: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error generating setup file: {e}") from e

    @staticmethod
    def generate_version_file(
        file_path: Path | str,
        version: str,
        company_name: str,
        project_description: str,
        project_name: str,
    ) -> None:
        """
        Generate a version information file at the specified path.

        Creates a version file by processing the version template with
        the provided project information.

        Args:
            file_path: Path where the version file will be created
            version: Project version (e.g., "1.0.0")
            company_name: Company or organization name
            project_description: Project description
            project_name: Project name

        Raises:
            ValueError: If version format is invalid
            OSError: If file writing fails (permissions, disk space, etc.)
            Exception: For other unexpected errors

        Example:
            >>> Helper.generate_version_file(
            ...     "version_info.txt",
            ...     "1.0.0",
            ...     "Acme Inc.",
            ...     "Compiler for Python projects",
            ...     "EzCompiler"
            ... )
        """
        try:
            template_manager = TemplateManager()
            version_content = template_manager.process_version_template(
                format_type="txt",
                version=version,
                company_name=company_name,
                project_description=project_description,
                project_name=project_name,
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(version_content)

        except ValueError as e:
            raise ValueError(f"Invalid version format: {e}") from e
        except OSError as e:
            raise OSError(f"Failed to write version file to {file_path}: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error generating version file: {e}") from e
