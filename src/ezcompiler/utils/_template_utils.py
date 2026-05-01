# ///////////////////////////////////////////////////////////////
# TEMPLATE_UTILS - Template processing utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Template processor - Variable substitution processor for EzCompiler templates.

This module provides utilities for processing templates with variable
substitution, including methods for config, version, and setup template
processing with placeholder replacement.

Utils layer can only use DEBUG and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path
from typing import Any

# Local imports
from ..shared.exceptions.utils import (
    TemplateFileWriteError,
    TemplateSubstitutionError,
    TemplateValidationError,
)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class TemplateProcessor:
    """
    Utility class for processing templates with variable substitution.

    Provides static methods to replace placeholders in templates with
    actual values from configuration dictionaries. Supports multiple
    template types and formats.

    Example:
        >>> processor = TemplateProcessor()
        >>> config = {"version": "1.0.0", "project_name": "MyApp"}
        >>> result = processor.process_config_template(template, config)
    """

    # ////////////////////////////////////////////////
    # MOCKUP GENERATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def create_mockup_config() -> dict[str, Any]:
        """
        Create a mockup configuration dictionary with default values.

        Provides realistic default values that can be used to generate
        valid JSON/YAML templates without placeholders.

        Returns:
            dict[str, Any]: Dictionary with mockup configuration values

        Example:
            >>> mockup = TemplateProcessor.create_mockup_config()
            >>> print(mockup["version"])
            '1.0.0'
        """
        return {
            "version": "1.0.0",
            "project_name": "MyProject",
            "project_description": "A sample project description",
            "company_name": "MyCompany",
            "author": "John Doe",
            "main_file": "main.py",
            "icon": "icon.ico",
            "version_filename": "version_info.txt",
            "output_folder": "dist",
            "include_files": {
                "files": ["config.yaml", "README.md", "requirements.txt"],
                "folders": ["assets", "data", "docs"],
            },
            "packages": ["requests", "pyyaml", "click"],
            "includes": ["utils", "helpers", "config"],
            "excludes": ["test", "debug", "temp"],
            "compilation": {
                "console": True,
                "compiler": "auto",
                "zip_needed": True,
                "repo_needed": False,
            },
            "upload": {
                "structure": "disk",
                "repo_path": "releases",
                "server_url": "https://example.com/upload",
            },
            "advanced": {"optimize": True, "strip": False, "debug": False},
        }

    @staticmethod
    def process_template_with_mockup(template: str) -> str:
        """
        Process a template using mockup values to create a valid file.

        Args:
            template: The template string with placeholders

        Returns:
            str: Processed template string with mockup values

        Raises:
            TemplateSubstitutionError: If substitution fails

        Example:
            >>> template = "version: #VERSION#\\nproject: #PROJECT_NAME#"
            >>> result = TemplateProcessor.process_template_with_mockup(template)
        """
        mockup_config = TemplateProcessor.create_mockup_config()
        return TemplateProcessor.process_config_template(template, mockup_config)

    # ////////////////////////////////////////////////
    # VERSION TEMPLATE PROCESSING
    # ////////////////////////////////////////////////

    @staticmethod
    def process_version_template(
        template: str,
        version: str,
        company_name: str,
        project_description: str,
        project_name: str,
    ) -> str:
        """
        Process version info template with project-specific values.

        Args:
            template: The version template string
            version: Project version (e.g., "1.0.0")
            company_name: Company name
            project_description: Project description
            project_name: Project name

        Returns:
            str: Processed template string

        Raises:
            TemplateSubstitutionError: If version substitution fails

        Note:
            Converts version string to tuple format (e.g., "1.0.0" -> "(1, 0, 0, 0)")
            and automatically includes current year for copyright.
        """
        try:
            # Convert version string to tuple format
            version_parts = version.split(".")
            while len(version_parts) < 4:
                version_parts.append("0")
            fixed_version = f"({', '.join(version_parts[:4])})"

            # Get current year
            from datetime import datetime

            current_year = str(datetime.now().year)

            # Replace placeholders
            replacements = {
                "#FIXED_VERSION#": fixed_version,
                "#STRING_VERSION#": version,
                "#COMPANY_NAME#": company_name,
                "#FILE_DESCRIPTION#": project_description,
                "#PRODUCT_NAME#": project_name,
                "#INTERNAL_NAME#": project_name,
                "#LEGAL_COPYRIGHT#": company_name,
                "#ORIGINAL_FILENAME#": project_name,
                "#YEAR#": current_year,
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(placeholder, str(value))

            return result
        except Exception as e:
            raise TemplateSubstitutionError(
                f"Failed to process version template: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # CONFIG TEMPLATE PROCESSING
    # ////////////////////////////////////////////////

    @staticmethod
    def process_config_template(template: str, config: dict[str, Any]) -> str:
        """
        Process configuration template with project configuration.

        Args:
            template: The configuration template string
            config: Project configuration dictionary

        Returns:
            str: Processed template string

        Raises:
            TemplateSubstitutionError: If config substitution fails

        Note:
            Handles nested dictionaries for include_files, compilation,
            upload, and advanced settings. Converts Python booleans to
            JSON-compatible lowercase strings.
        """
        try:
            # Extract values from config with defaults
            version = config.get("version", "1.0.0")
            project_name = config.get("project_name", "MyProject")
            project_description = config.get(
                "project_description", "Project Description"
            )
            company_name = config.get("company_name", "Company Name")
            author = config.get("author", "Author Name")
            icon = config.get("icon", "icon.ico")
            main_file = config.get("main_file", "main.py")
            version_file = config.get("version_filename", "version_info.txt")
            output_folder = config.get("output_folder", "dist")

            # Create include_files lists
            include_files = config.get("include_files", {"files": [], "folders": []})
            include_files_list = include_files.get("files", [])
            include_folders_list = include_files.get("folders", [])

            # Create other lists
            packages = config.get("packages", [])
            includes = config.get("includes", [])
            excludes = config.get("excludes", ["debugpy", "test", "unittest"])

            # Compilation options
            compilation = config.get("compilation", {})
            console = compilation.get("console", True)
            compiler = compilation.get("compiler", "auto")
            zip_needed = compilation.get("zip_needed", True)
            repo_needed = compilation.get("repo_needed", False)

            # Upload options
            upload = config.get("upload", {})
            upload_structure = upload.get("structure", "disk")
            repo_path = upload.get("repo_path", "releases")
            server_url = upload.get("server_url", "")

            # Advanced options
            advanced = config.get("advanced", {})
            optimize = advanced.get("optimize", True)
            strip = advanced.get("strip", False)
            debug = advanced.get("debug", False)

            # Replace placeholders with JSON-valid values
            replacements = {
                "#VERSION#": version,
                "#PROJECT_NAME#": project_name,
                "#PROJECT_DESCRIPTION#": project_description,
                "#COMPANY_NAME#": company_name,
                "#AUTHOR#": author,
                "#ICON#": icon,
                "#MAIN_FILE#": main_file,
                "#VERSION_FILE#": version_file,
                "#OUTPUT_FOLDER#": output_folder,
                "#INCLUDE_FILES#": json.dumps(include_files_list),
                "#INCLUDE_FOLDERS#": json.dumps(include_folders_list),
                "#PACKAGES#": json.dumps(packages),
                "#INCLUDES#": json.dumps(includes),
                "#EXCLUDES#": json.dumps(excludes),
                "#CONSOLE#": str(console).lower(),
                "#COMPILER#": compiler,
                "#ZIP_NEEDED#": str(zip_needed).lower(),
                "#REPO_NEEDED#": str(repo_needed).lower(),
                "#UPLOAD_STRUCTURE#": upload_structure,
                "#REPO_PATH#": repo_path,
                "#SERVER_URL#": server_url,
                "#OPTIMIZE#": str(optimize).lower(),
                "#STRIP#": str(strip).lower(),
                "#DEBUG#": str(debug).lower(),
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(placeholder, str(value))

            return result
        except Exception as e:
            raise TemplateSubstitutionError(
                f"Failed to process config template: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # SETUP TEMPLATE PROCESSING
    # ////////////////////////////////////////////////

    @staticmethod
    def process_setup_template(template: str, config: dict[str, Any]) -> str:
        """
        Process setup template with project configuration.

        Args:
            template: The setup template string
            config: Project configuration dictionary

        Returns:
            str: Processed template string

        Raises:
            TemplateSubstitutionError: If setup substitution fails

        Note:
            Formats include_files as Python dict string representation
            for setup.py compatibility.
        """
        try:
            # Extract values from config with defaults
            version = config.get("version", "1.0.0")
            project_name = config.get("project_name", "MyProject")
            project_description = config.get(
                "project_description", "Project Description"
            )
            company_name = config.get("company_name", "Company Name")
            author = config.get("author", "Author Name")
            icon = config.get("icon", "icon.ico")
            main_file = config.get("main_file", "main.py")
            version_file = config.get("version_filename", "version_info.txt")
            output_folder = config.get("output_folder", "dist")

            # Create include_files dict string representation
            include_files = config.get("include_files", {"files": [], "folders": []})
            include_files_str = (
                f'{{"files": {include_files.get("files", [])}, '
                f'"folders": {include_files.get("folders", [])}}}'
            )

            # Create other lists
            packages = config.get("packages", [])
            includes = config.get("includes", [])
            excludes = config.get("excludes", ["debugpy", "test", "unittest"])

            # Replace placeholders
            replacements = {
                "#VERSION#": version,
                "#ZIP_NEEDED#": "True",
                "#REPO_NEEDED#": "False",
                "#PROJECT_NAME#": project_name,
                "#PROJECT_DESCRIPTION#": project_description,
                "#COMPANY_NAME#": company_name,
                "#AUTHOR#": author,
                "#ICON#": icon,
                "#MAIN_FILE#": main_file,
                "#VERSION_FILE#": version_file,
                "#OUTPUT_FOLDER#": output_folder,
                "#INCLUDE_FILES#": include_files_str,
                "#PACKAGES#": str(packages),
                "#INCLUDES#": str(includes),
                "#EXCLUDES#": str(excludes),
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(placeholder, str(value))

            return result
        except Exception as e:
            raise TemplateSubstitutionError(
                f"Failed to process setup template: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # FILE CREATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def _create_config_file(
        template: str, _config: dict[str, Any], output_path: Path
    ) -> None:
        """
        Create a configuration file from template.

        Args:
            template: The configuration template
            _config: Configuration values to substitute (currently unused)
            output_path: Path where to save the config file

        Raises:
            TemplateFileWriteError: If writing the file fails

        Note:
            Currently writes template as-is. Future versions may process
            the template with config values.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template)
        except Exception as e:
            raise TemplateFileWriteError(
                f"Failed to write config file to {output_path}: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_template(template: str) -> bool:
        """
        Validate template syntax.

        Args:
            template: Template string to validate

        Returns:
            bool: True if template is valid

        Raises:
            TemplateValidationError: If template syntax is invalid

        Note:
            Performs basic validation: checks for balanced braces and quotes.
        """
        try:
            # Check for balanced braces
            brace_count = template.count("{") - template.count("}")
            if brace_count != 0:
                raise TemplateValidationError("Unbalanced braces in template")

            # Check for balanced quotes (excluding escaped quotes)
            quote_count = template.count('"') - template.count('\\"')
            if quote_count % 2 != 0:
                raise TemplateValidationError("Unbalanced quotes in template")

            return True
        except TemplateValidationError:
            raise
        except Exception as e:
            raise TemplateValidationError(f"Template validation failed: {e}") from e
