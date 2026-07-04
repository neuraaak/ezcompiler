# ///////////////////////////////////////////////////////////////
# CONFIG_UTILS - Configuration-specific utility functions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Configuration utilities - Configuration-specific utility functions for EzCompiler.

This module provides specialized utility functions for configuration validation
and processing. Uses thematic utils (ValidationUtils, FileUtils) internally.

Note: These utilities are intended for use by services and other layers that
need to validate or process CompilerConfig instances. The CompilerConfig class
itself performs its own validation during initialization.

Utils layer can only use DEBUG and ERROR log levels.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import tomllib
from pathlib import Path
from typing import Any

# Third-party imports
import yaml

# Local imports
from ..shared import CompilerConfig
from ..shared.exceptions.utils import (
    CompilerOptionError,
    ConfigFileNotFoundError,
    ConfigFileParseError,
    ConfigPathError,
    MissingRequiredConfigError,
)
from ._file_utils import FileUtils
from .validators import validate_string_length

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ConfigUtils:
    """
    Utility class for configuration-specific operations.

    Provides static methods for configuration validation and processing.
    Uses thematic utils (ValidationUtils, FileUtils) internally.

    Example:
        >>> config = CompilerConfig(...)
        >>> ConfigUtils.validate_required_config_fields(config)
        >>> ConfigUtils.validate_config_paths(config)
        >>> ConfigUtils.validate_compiler_option(config.compiler)
    """

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_required_config_fields(config: CompilerConfig) -> None:
        """
        Validate required configuration fields are not empty.

        Args:
            config: CompilerConfig instance to validate

        Raises:
            ConfigurationError: If any required field is empty

        Note:
            Uses ValidationUtils for string validation.

        Example:
            >>> config = CompilerConfig(...)
            >>> ConfigUtils.validate_required_config_fields(config)
        """
        if not config.version:
            raise MissingRequiredConfigError("Version cannot be empty")

        if not validate_string_length(config.project_name, min_length=1):
            raise MissingRequiredConfigError("Project name cannot be empty")

        if not validate_string_length(config.main_file, min_length=1):
            raise MissingRequiredConfigError("Main file cannot be empty")

        if not config.include_files:
            raise MissingRequiredConfigError("Include files cannot be empty")

    @staticmethod
    def validate_config_paths(config: CompilerConfig) -> None:
        """
        Validate file and folder paths in configuration.

        Ensures main file exists and normalizes output_folder to Path.
        Does not create the output folder (that's done during compilation).

        Args:
            config: CompilerConfig instance to validate

        Raises:
            ConfigurationError: If main file doesn't exist

        Note:
            Uses FileUtils for file existence checks.

        Example:
            >>> config = CompilerConfig(..., main_file="main.py", output_folder="dist")
            >>> ConfigUtils.validate_config_paths(config)
        """
        if not FileUtils.validate_file_exists(config.main_file):
            raise ConfigPathError(f"Main file not found: {config.main_file}")

        # Normalize output_folder to Path if it's a string
        if isinstance(config.output_folder, str):
            config.output_folder = Path(config.output_folder)

    @staticmethod
    def validate_compiler_option(compiler: str) -> None:
        """
        Validate compiler option value.

        Args:
            compiler: Compiler name to validate

        Raises:
            ConfigurationError: If compiler is not valid

        Example:
            >>> ConfigUtils.validate_compiler_option("PyInstaller")
            >>> ConfigUtils.validate_compiler_option("invalid")
            ConfigurationError: Invalid compiler: invalid
        """
        valid_compilers = ["Cx_Freeze", "PyInstaller", "Nuitka"]
        if compiler not in valid_compilers:
            raise CompilerOptionError(
                f"Invalid compiler: {compiler}. Must be one of {valid_compilers}"
            )

    @staticmethod
    def normalize_output_folder(output_folder: str | Path) -> Path:
        """
        Normalize output folder path to Path object.

        Args:
            output_folder: Output folder as string or Path

        Returns:
            Path: Normalized Path object

        Example:
            >>> folder = ConfigUtils.normalize_output_folder("dist")
            >>> print(type(folder))
            <class 'pathlib.Path'>
        """
        if isinstance(output_folder, str):
            return Path(output_folder)
        return output_folder

    # ////////////////////////////////////////////////
    # FILE LOADING METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def load_yaml_config(path: Path) -> dict[str, Any]:
        """
        Load configuration from a YAML file.

        Args:
            path: Path to the YAML file

        Returns:
            dict[str, Any]: Parsed configuration dictionary

        Raises:
            ConfigFileNotFoundError: If the file does not exist
            ConfigFileParseError: If the file cannot be parsed
        """
        if not path.exists():
            raise ConfigFileNotFoundError(f"YAML config file not found: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError as e:
            raise ConfigFileParseError(f"Failed to parse YAML file {path}: {e}") from e

    @staticmethod
    def load_json_config(path: Path) -> dict[str, Any]:
        """
        Load configuration from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            dict[str, Any]: Parsed configuration dictionary

        Raises:
            ConfigFileNotFoundError: If the file does not exist
            ConfigFileParseError: If the file cannot be parsed
        """
        if not path.exists():
            raise ConfigFileNotFoundError(f"JSON config file not found: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError as e:
            raise ConfigFileParseError(f"Failed to parse JSON file {path}: {e}") from e

    @staticmethod
    def load_toml_config(path: Path) -> dict[str, Any]:
        """
        Load and return the full parsed TOML dictionary.

        Args:
            path: Path to the TOML file

        Returns:
            dict[str, Any]: Parsed TOML dictionary

        Raises:
            ConfigFileNotFoundError: If the file does not exist
            ConfigFileParseError: If the file cannot be parsed
        """
        if not path.exists():
            raise ConfigFileNotFoundError(f"TOML config file not found: {path}")
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            raise ConfigFileParseError(f"Failed to parse TOML file {path}: {e}") from e

    # ////////////////////////////////////////////////
    # PYPROJECT.TOML EXTRACTION
    # ////////////////////////////////////////////////

    @staticmethod
    def extract_pyproject_config(toml_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract ezcompiler configuration from pyproject.toml structure.

        Maps [project] fields (name, version, description, authors) and
        [tool.ezcompiler] fields into the flat config dict format expected
        by CompilerConfig.from_dict().

        Args:
            toml_data: Full parsed pyproject.toml dictionary

        Returns:
            dict[str, Any]: Extracted configuration dictionary (may be empty)
        """
        result: dict[str, Any] = {}

        # Extract from [project] section
        project = toml_data.get("project", {})
        if "name" in project:
            result["project_name"] = project["name"]
        if "version" in project:
            result["version"] = project["version"]
        if "description" in project:
            result["project_description"] = project["description"]
        if "authors" in project and project["authors"]:
            first_author = project["authors"][0]
            if isinstance(first_author, dict):
                author_name = first_author.get("name", "")
                result["author"] = author_name
                result["company_name"] = author_name

        # Extract from [tool.ezcompiler] section
        tool_config = toml_data.get("tool", {}).get("ezcompiler", {})
        if tool_config:
            result.update(tool_config)

        return result

    # ////////////////////////////////////////////////
    # CONFIG DISCOVERY
    # ////////////////////////////////////////////////

    @staticmethod
    def discover_config_file(search_dir: Path) -> Path | None:
        """
        Auto-discover configuration file in the given directory.

        Priority order:
        1. ezcompiler.yaml
        2. ezcompiler.json
        3. pyproject.toml (only if [tool.ezcompiler] section exists)

        Args:
            search_dir: Directory to search in

        Returns:
            Path | None: Path to discovered config file, or None if not found
        """
        # Check YAML first
        yaml_path = search_dir / "ezcompiler.yaml"
        if yaml_path.exists():
            return yaml_path

        # Check JSON
        json_path = search_dir / "ezcompiler.json"
        if json_path.exists():
            return json_path

        # Check pyproject.toml (only if it has [tool.ezcompiler])
        toml_path = search_dir / "pyproject.toml"
        if toml_path.exists():
            try:
                with open(toml_path, "rb") as f:
                    data = tomllib.load(f)
                if data.get("tool", {}).get("ezcompiler"):
                    return toml_path
            except Exception:  # noqa: S110  # nosec B110 - découverte best-effort : un pyproject illisible ne doit pas interrompre la recherche
                pass

        return None

    # ////////////////////////////////////////////////
    # CONFIG MERGING
    # ////////////////////////////////////////////////

    @staticmethod
    def merge_config_dicts(
        base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge two configuration dictionaries.

        Override replaces base values. For known nested sections
        (compilation, upload, advanced, release, installer), keys are merged
        within the section. All other values (including include_files, lists)
        are replaced entirely.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary

        Returns:
            dict[str, Any]: Merged configuration dictionary
        """
        result = base.copy()
        nested_sections = {"compilation", "upload", "advanced", "release", "installer"}

        for key, value in override.items():
            if (
                key in nested_sections
                and key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = {**result[key], **value}
            else:
                result[key] = value

        return result
