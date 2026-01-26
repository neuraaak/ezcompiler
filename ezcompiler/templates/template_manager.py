# ///////////////////////////////////////////////////////////////
# TEMPLATE_MANAGER - Template loading and management
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Template manager - Template loading and processing manager for EzCompiler.

This module provides functionality for loading template files, processing them
with variable substitution, and generating output files from templates.
Supports config, version, and setup template types.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Local imports
from .template_utils import TemplateProcessor

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class TemplateManager:
    """
    Manager for loading and processing template files.

    Provides methods to load templates from .template files and process
    them with variable substitution for configuration, version info,
    and setup scripts.

    Attributes:
        templates_dir: Base directory containing template subdirectories
        processor: TemplateProcessor instance for variable substitution

    Example:
        >>> manager = TemplateManager()
        >>> template = manager.load_template("config", "yaml")
        >>> content = manager.process_config_template("yaml", config_dict)
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self) -> None:
        """
        Initialize the template manager.

        Note:
            Automatically detects templates_dir from module location.
        """
        self.templates_dir = Path(__file__).parent
        self.processor = TemplateProcessor()

    # ////////////////////////////////////////////////
    # PATH AND LOADING METHODS
    # ////////////////////////////////////////////////

    def get_template_path(self, template_type: str, format_type: str) -> Path:
        """
        Get the path to a specific template file.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template (yaml, json, txt, py)

        Returns:
            Path: Path to the template file

        Note:
            Version templates have special naming: version_info.{format}.template
            Other templates follow: {type}.{format}.template
        """
        if template_type == "version":
            # Special case for version templates
            return (
                self.templates_dir
                / template_type
                / f"version_info.{format_type}.template"
            )
        else:
            return (
                self.templates_dir
                / template_type
                / f"{template_type}.{format_type}.template"
            )

    def load_template(self, template_type: str, format_type: str) -> str:
        """
        Load a template file.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template (yaml, json, txt, py)

        Returns:
            str: Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.get_template_path(template_type, format_type)

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, encoding="utf-8") as f:
            return f.read()

    def list_available_templates(self) -> dict[str, list[str]]:
        """
        List all available templates.

        Returns:
            dict[str, list[str]]: Dictionary mapping template types to available formats

        Example:
            >>> manager.list_available_templates()
            {'config': ['yaml', 'json'], 'version': ['txt'], 'setup': ['py']}
        """
        templates: dict[str, list[str]] = {}

        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                template_type = template_dir.name
                formats = []

                for template_file in template_dir.glob("*.template"):
                    # Extract format from filename (e.g., "config.yaml.template" -> "yaml")
                    format_type = template_file.stem.split(".")[-1]
                    formats.append(format_type)

                templates[template_type] = formats

        return templates

    # ////////////////////////////////////////////////
    # TEMPLATE PROCESSING METHODS
    # ////////////////////////////////////////////////

    def process_config_template(self, format_type: str, config: dict[str, Any]) -> str:
        """
        Process a configuration template.

        Args:
            format_type: Format of the template (yaml, json)
            config: Configuration values dictionary

        Returns:
            str: Processed template string

        Example:
            >>> config = {"version": "1.0.0", "project_name": "MyApp"}
            >>> content = manager.process_config_template("yaml", config)
        """
        template = self.load_template("config", format_type)
        return self.processor.process_config_template(template, config)

    def process_version_template(
        self,
        format_type: str,
        version: str,
        company_name: str,
        project_description: str,
        project_name: str,
    ) -> str:
        """
        Process a version template.

        Args:
            format_type: Format of the template (txt)
            version: Project version (e.g., "1.0.0")
            company_name: Company name
            project_description: Project description
            project_name: Project name

        Returns:
            str: Processed template string
        """
        template = self.load_template("version", format_type)
        return self.processor.process_version_template(
            template, version, company_name, project_description, project_name
        )

    def process_setup_template(self, format_type: str, config: dict[str, Any]) -> str:
        """
        Process a setup template.

        Args:
            format_type: Format of the template (py)
            config: Configuration values dictionary

        Returns:
            str: Processed template string
        """
        template = self.load_template("setup", format_type)
        return self.processor.process_setup_template(template, config)

    # ////////////////////////////////////////////////
    # FILE GENERATION METHODS
    # ////////////////////////////////////////////////

    def create_file_from_template(
        self, template_type: str, format_type: str, output_path: Path, **kwargs: Any
    ) -> None:
        """
        Create a file from a template.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template
            output_path: Path where to save the file
            **kwargs: Additional arguments for template processing

        Raises:
            ValueError: If template_type is unknown

        Note:
            Automatically creates parent directories if they don't exist.
        """
        if template_type == "config":
            content = self.process_config_template(
                format_type, kwargs.get("config", {})
            )
        elif template_type == "version":
            content = self.process_version_template(
                format_type,
                kwargs.get("version", "1.0.0"),
                kwargs.get("company_name", "Company"),
                kwargs.get("project_description", "Description"),
                kwargs.get("project_name", "Project"),
            )
        elif template_type == "setup":
            content = self.process_setup_template(format_type, kwargs.get("config", {}))
        else:
            raise ValueError(f"Unknown template type: {template_type}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the processed template
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def generate_template_with_mockup(
        self, template_type: str, format_type: str, output_path: Path
    ) -> None:
        """
        Generate a template file with mockup values instead of placeholders.

        Creates a valid file that can be used as a starting point and
        edited manually with real values.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template
            output_path: Path where to save the file

        Raises:
            ValueError: If template_type is unknown
            Exception: If generation fails
        """
        try:
            # Load the template
            template = self.load_template(template_type, format_type)

            # Process with mockup values
            if template_type == "config":
                content = self.processor.process_template_with_mockup(template)
            elif template_type == "version":
                mockup_config = self.processor.create_mockup_config()
                content = self.processor.process_version_template(
                    template,
                    mockup_config["version"],
                    mockup_config["company_name"],
                    mockup_config["project_description"],
                    mockup_config["project_name"],
                )
            elif template_type == "setup":
                mockup_config = self.processor.create_mockup_config()
                content = self.processor.process_setup_template(template, mockup_config)
            else:
                raise ValueError(f"Unknown template type: {template_type}")

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the processed template with mockup values
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            raise Exception(f"Failed to generate template with mockup: {e}") from e

    def generate_raw_template(
        self, template_type: str, format_type: str, output_path: Path
    ) -> None:
        """
        Generate a raw template file with placeholders.

        Creates a template file with placeholders that can be processed
        later with real values.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template
            output_path: Path where to save the file

        Raises:
            Exception: If generation fails
        """
        try:
            # Load the template
            template = self.load_template(template_type, format_type)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the raw template with placeholders
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template)

        except Exception as e:
            raise Exception(f"Failed to generate raw template: {e}") from e

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    def validate_template(self, template_type: str, format_type: str) -> bool:
        """
        Validate a template file.

        Args:
            template_type: Type of template
            format_type: Format of the template

        Returns:
            bool: True if template is valid, False otherwise

        Note:
            Validates template syntax by loading and checking it.
        """
        try:
            template = self.load_template(template_type, format_type)
            return self.processor.validate_template(template)
        except Exception:
            return False
