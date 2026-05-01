# ///////////////////////////////////////////////////////////////
# TEMPLATE_SERVICE - Template processing and file generation service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Template service - Template processing and file generation service for EzCompiler.

This module provides the TemplateService class that orchestrates template
processing and file generation (setup.py, version_info.txt, config files).

Services layer can use WARNING and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Local imports
from ..adapters import BaseFileWriter
from ..adapters._disk_file_writer import DiskFileWriter
from ..assets import TemplateLoader
from ..shared.exceptions import TemplateError, VersionError
from ..utils import FileUtils, TemplateProcessor

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class TemplateService:
    """
    Template processing and file generation service.

    Orchestrates template loading, processing, and file generation for
    configuration files, setup.py, and version information files.

    Attributes:
        _template_loader: TemplateLoader instance for template operations
        _processor: TemplateProcessor instance for variable substitution

    Example:
        >>> service = TemplateService()
        >>> config = {"version": "1.0.0", "project_name": "MyApp"}
        >>> service.generate_setup_file(config, Path("setup.py"))
        >>> service.generate_version_file(config, Path("version_info.txt"))
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self, file_writer: BaseFileWriter | None = None) -> None:
        """
        Initialize the template service.

        Creates TemplateLoader and TemplateProcessor instances for
        template operations.
        """
        if TemplateLoader is None:
            raise TemplateError("TemplateLoader is not available")
        if TemplateProcessor is None:
            raise TemplateError("TemplateProcessor is not available")

        self._template_loader = TemplateLoader()
        self._processor = TemplateProcessor()
        self._file_writer = file_writer or DiskFileWriter()

    # ////////////////////////////////////////////////
    # CONFIG FILE GENERATION
    # ////////////////////////////////////////////////

    def generate_config_file(
        self,
        config: dict[str, Any],
        output_path: Path,
        format_type: str = "yaml",
    ) -> None:
        """
        Generate a configuration file (YAML or JSON) from template.

        Args:
            config: Project configuration dictionary
            output_path: Path where to save the config file
            format_type: Format type ("yaml" or "json")

        Raises:
            TemplateError: If generation fails

        Example:
            >>> config = {"version": "1.0.0", "project_name": "MyApp"}
            >>> service.generate_config_file(config, Path("ezcompiler.yaml"), "yaml")
        """
        try:
            # Ensure output directory exists
            FileUtils.ensure_parent_directory_exists(output_path)

            # Process template
            content = self._template_loader.process_config_template(format_type, config)

            # Write file
            self._file_writer.write_text(output_path, content, encoding="utf-8")

        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to generate config file: {str(e)}") from e

    # ////////////////////////////////////////////////
    # SETUP FILE GENERATION
    # ////////////////////////////////////////////////

    def generate_setup_file(
        self,
        config: dict[str, Any],
        output_path: Path | None = None,
        output_dir: Path | None = None,
    ) -> Path:
        """
        Generate a setup.py file from template.

        Args:
            config: Project configuration dictionary
            output_path: Direct path to setup.py file (optional)
            output_dir: Directory where to save setup.py (optional, defaults to current dir)

        Returns:
            Path: Path to the generated setup.py file

        Raises:
            TemplateError: If generation fails

        Example:
            >>> config = {"version": "1.0.0", "project_name": "MyApp"}
            >>> setup_path = service.generate_setup_file(config, output_dir=Path("build"))
        """
        try:
            # Determine output path
            final_path: Path
            if output_path is not None:
                final_path = Path(output_path)
                FileUtils.ensure_parent_directory_exists(final_path)
            else:
                target_dir = output_dir if output_dir is not None else Path.cwd()
                target_dir = Path(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)
                final_path = target_dir / "setup.py"

            # Process template
            content = self._template_loader.process_setup_template("py", config)

            # Write file
            self._file_writer.write_text(final_path, content, encoding="utf-8")

            return final_path

        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to generate setup file: {str(e)}") from e

    # ////////////////////////////////////////////////
    # VERSION FILE GENERATION
    # ////////////////////////////////////////////////

    def generate_version_file(
        self,
        config: dict[str, Any],
        output_path: Path | None = None,
        format_type: str = "txt",
    ) -> Path:
        """
        Generate a version information file from template.

        Args:
            config: Project configuration dictionary
            output_path: Path where to save the version file (optional)
            format_type: Template format type (default: "txt")

        Returns:
            Path: Path to the generated version file

        Raises:
            VersionError: If generation fails

        Note:
            If output_path is None, uses version_filename and output_folder from config.

        Example:
            >>> config = {
            ...     "version": "1.0.0",
            ...     "project_name": "MyApp",
            ...     "version_filename": "version_info.txt",
            ...     "output_folder": "dist"
            ... }
            >>> version_path = service.generate_version_file(config)
        """
        try:
            # Determine output path
            final_path: Path
            if output_path is not None:
                final_path = Path(output_path)
            else:
                version_file = config.get("version_filename", "version_info.txt")
                output_folder = Path(config.get("output_folder", "dist"))
                final_path = output_folder / version_file

            # Ensure output directory exists
            FileUtils.ensure_parent_directory_exists(final_path)

            # Extract required fields with defaults
            version = config.get("version", "1.0.0")
            company_name = config.get("company_name", "")
            project_description = config.get("project_description", "")
            project_name = config.get("project_name", "MyProject")

            # Process template
            content = self._template_loader.process_version_template(
                format_type=format_type,
                version=version,
                company_name=company_name,
                project_description=project_description,
                project_name=project_name,
            )

            # Write file
            self._file_writer.write_text(final_path, content, encoding="utf-8")

            return final_path

        except VersionError:
            raise
        except Exception as e:
            raise VersionError(f"Failed to generate version file: {str(e)}") from e

    # ////////////////////////////////////////////////
    # TEMPLATE UTILITIES
    # ////////////////////////////////////////////////

    def process_config_template(self, format_type: str, config: dict[str, Any]) -> str:
        """
        Process a configuration template with values.

        Args:
            format_type: Format type ("yaml" or "json")
            config: Configuration dictionary

        Returns:
            str: Processed template content

        Example:
            >>> config = {"version": "1.0.0", "project_name": "MyApp"}
            >>> content = service.process_config_template("yaml", config)
        """
        return self._template_loader.process_config_template(format_type, config)

    def process_setup_template(self, config: dict[str, Any]) -> str:
        """
        Process a setup template with values.

        Args:
            config: Configuration dictionary

        Returns:
            str: Processed template content

        Example:
            >>> config = {"version": "1.0.0", "project_name": "MyApp"}
            >>> content = service.process_setup_template(config)
        """
        return self._template_loader.process_setup_template("py", config)

    def process_version_template(
        self,
        version: str,
        company_name: str,
        project_description: str,
        project_name: str,
        format_type: str = "txt",
    ) -> str:
        """
        Process a version template with values.

        Args:
            version: Project version
            company_name: Company name
            project_description: Project description
            project_name: Project name
            format_type: Format type (default: "txt")

        Returns:
            str: Processed template content

        Example:
            >>> content = service.process_version_template(
            ...     "1.0.0", "MyCompany", "Description", "MyApp"
            ... )
        """
        return self._template_loader.process_version_template(
            format_type, version, company_name, project_description, project_name
        )

    # ////////////////////////////////////////////////
    # TEMPLATE MANAGEMENT
    # ////////////////////////////////////////////////

    def list_available_templates(self) -> dict[str, list[str]]:
        """
        List all available templates.

        Returns:
            dict[str, list[str]]: Dictionary mapping template types to available formats

        Example:
            >>> templates = service.list_available_templates()
            >>> print(templates)
            {'config': ['yaml', 'json'], 'version': ['txt'], 'setup': ['py']}
        """
        return self._template_loader.list_available_templates()

    def validate_template(self, template_type: str, format_type: str) -> bool:
        """
        Validate a template file.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template

        Returns:
            bool: True if template is valid, False otherwise

        Example:
            >>> is_valid = service.validate_template("config", "yaml")
        """
        return self._template_loader.validate_template(template_type, format_type)

    # ////////////////////////////////////////////////
    # RAW TEMPLATE GENERATION
    # ////////////////////////////////////////////////

    def generate_mockup_template(
        self,
        template_type: str,
        format_type: str,
        output_path: Path,
    ) -> None:
        """
        Generate a template file with mockup values instead of placeholders.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template (yaml, json, py, txt)
            output_path: Path where to save the generated file

        Raises:
            TemplateError: If generation fails

        Example:
            >>> service.generate_mockup_template("config", "yaml", Path("ezcompiler.yaml"))
        """
        try:
            self._template_loader.generate_template_with_mockup(
                template_type, format_type, output_path
            )
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to generate mockup template: {str(e)}") from e

    def generate_raw_template(
        self,
        template_type: str,
        format_type: str,
        output_path: Path,
    ) -> None:
        """
        Generate a raw template file with placeholders.

        Args:
            template_type: Type of template (config, version, setup)
            format_type: Format of the template (yaml, json, py, txt)
            output_path: Path where to save the template file

        Raises:
            TemplateError: If generation fails

        Example:
            >>> service.generate_raw_template("config", "yaml", Path("template.yaml"))
        """
        try:
            self._template_loader.generate_raw_template(
                template_type, format_type, output_path
            )
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to generate raw template: {str(e)}") from e
