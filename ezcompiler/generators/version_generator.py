# ///////////////////////////////////////////////////////////////
# VERSION_GENERATOR - Version file generator
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Version generator - Version information file generator for EzCompiler.

This module provides functionality for generating version information files
using templates and configuration values. Supports multiple format types
and integrates with the template management system.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Local imports
from ..core.exceptions import VersionError
from ..templates import TemplateManager

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class VersionGenerator:
    """
    Generator for version information files.

    Handles the generation of version files using templates and the
    TemplateManager system. Supports various output formats and
    automatic directory creation.

    Attributes:
        template_manager: TemplateManager instance for template processing

    Example:
        >>> generator = VersionGenerator()
        >>> config = {"version": "1.0.0", "project_name": "MyApp"}
        >>> generator.generate_from_config(config)
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self) -> None:
        """
        Initialize the version generator.

        Note:
            Automatically creates a TemplateManager instance for
            template processing operations.
        """
        self.template_manager = TemplateManager()

    # ////////////////////////////////////////////////
    # GENERATION METHODS
    # ////////////////////////////////////////////////

    def generate(
        self, config: dict[str, Any], output_path: Path, format_type: str = "txt"
    ) -> None:
        """
        Generate a version file from template.

        Args:
            config: Project configuration dictionary
            output_path: Path where to save the version file
            format_type: Template format type (txt, py, etc.)

        Raises:
            VersionError: If version generation fails

        Note:
            Extracts version, company_name, project_description, and
            project_name from config with sensible defaults.

        Example:
            >>> config = {
            ...     "version": "1.0.0",
            ...     "project_name": "MyApp",
            ...     "company_name": "MyCompany"
            ... }
            >>> generator.generate(config, Path("version_info.txt"))
        """
        try:
            # Extract required fields from config with defaults
            version = config.get("version", "1.0.0")
            company_name = config.get("company_name", "")
            project_description = config.get("project_description", "")
            project_name = config.get("project_name", "MyProject")

            # Generate version content using template
            version_content = self.template_manager.process_version_template(
                format_type=format_type,
                version=version,
                company_name=company_name,
                project_description=project_description,
                project_name=project_name,
            )

            # Write the version file
            output_path.write_text(version_content, encoding="utf-8")

        except Exception as e:
            raise VersionError(f"Failed to generate version file: {str(e)}") from e

    def generate_from_config(self, config: dict[str, Any]) -> None:
        """
        Generate version file using configuration.

        Automatically determines output path from config settings
        (version_filename and output_folder). Creates output directory
        if it doesn't exist.

        Args:
            config: Project configuration dictionary

        Raises:
            VersionError: If version generation fails

        Note:
            Uses version_filename (default: "version_info.txt") and
            output_folder (default: "dist") from config.

        Example:
            >>> config = {
            ...     "version": "1.0.0",
            ...     "version_filename": "version_info.txt",
            ...     "output_folder": "dist"
            ... }
            >>> generator.generate_from_config(config)
        """
        try:
            # Get version file path from config with defaults
            version_file = config.get("version_filename", "version_info.txt")
            output_folder = Path(config.get("output_folder", "dist"))
            output_path = output_folder / version_file

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate the version file
            self.generate(config, output_path)

        except Exception as e:
            raise VersionError(
                f"Failed to generate version file from config: {str(e)}"
            ) from e
