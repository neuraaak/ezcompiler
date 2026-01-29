# ///////////////////////////////////////////////////////////////
# CONFIG_SERVICE - Configuration orchestration service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Configuration service - Configuration loading and cascade orchestration.

This module provides the ConfigService class that orchestrates configuration
loading from multiple sources (pyproject.toml, YAML, JSON) with a cascade
merge system and CLI overrides.

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
from ..shared.compiler_config import CompilerConfig
from ..shared.exceptions import ConfigurationError
from ..shared.exceptions.utils.config_exceptions import (
    ConfigFileNotFoundError,
    ConfigFileParseError,
    TomlNotAvailableError,
)
from ..utils.config_utils import ConfigUtils

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ConfigService:
    """
    Configuration orchestration service.

    Orchestrates configuration loading from multiple sources with a cascade
    merge system. Sources are merged in priority order (later wins):

    1. pyproject.toml [project] + [tool.ezcompiler] (base)
    2. ezcompiler.yaml or ezcompiler.json (override)
    3. CLI arguments (final override)

    Example:
        >>> config = ConfigService.build_compiler_config()
        >>> config = ConfigService.build_compiler_config(
        ...     config_path=Path("ezcompiler.yaml"),
        ...     cli_overrides={"compiler": "PyInstaller"},
        ... )
    """

    # ////////////////////////////////////////////////
    # CONFIG LOADING
    # ////////////////////////////////////////////////

    @staticmethod
    def load_config(
        config_path: Path | None = None,
        pyproject_path: Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
        search_dir: Path | None = None,
    ) -> dict[str, Any]:
        """
        Load configuration with full cascade.

        Merges configuration from multiple sources in priority order:
        1. pyproject.toml [project] + [tool.ezcompiler] (base layer)
        2. ezcompiler.yaml or .json - explicit or auto-discovered (override)
        3. CLI overrides (final override)

        Args:
            config_path: Explicit config file path for YAML/JSON (skips auto-discovery)
            pyproject_path: Explicit pyproject.toml path (default: search_dir/pyproject.toml)
            cli_overrides: Dict of CLI-provided overrides (only non-default values)
            search_dir: Directory to search for config files (default: cwd)

        Returns:
            dict[str, Any]: Merged configuration dictionary

        Raises:
            ConfigurationError: If no configuration source found or loading fails
        """
        search_dir = search_dir or Path.cwd()
        merged: dict[str, Any] = {}

        try:
            # Step 1: pyproject.toml as base layer
            merged = ConfigService._load_pyproject_layer(
                pyproject_path, search_dir, merged
            )

            # Step 2: YAML/JSON overlay (explicit or auto-discovered)
            merged = ConfigService._load_config_file_layer(
                config_path, search_dir, merged
            )

            # Step 3: CLI overrides (final layer)
            if cli_overrides:
                merged = ConfigUtils.merge_config_dicts(merged, cli_overrides)

            if not merged:
                raise ConfigurationError(
                    "No configuration source found. Provide a config file, "
                    "add [tool.ezcompiler] to pyproject.toml, or use CLI options."
                )

            return merged

        except ConfigurationError:
            raise
        except (
            ConfigFileNotFoundError,
            ConfigFileParseError,
            TomlNotAvailableError,
        ) as e:
            raise ConfigurationError(f"Configuration loading failed: {e}") from e
        except Exception as e:
            raise ConfigurationError(
                f"Unexpected error loading configuration: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # CONFIG BUILDING
    # ////////////////////////////////////////////////

    @staticmethod
    def build_compiler_config(
        config_path: Path | None = None,
        pyproject_path: Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
        search_dir: Path | None = None,
    ) -> CompilerConfig:
        """
        Load configuration and create a CompilerConfig instance.

        Convenience method that combines load_config() with
        CompilerConfig.from_dict().

        Args:
            config_path: Explicit config file path for YAML/JSON
            pyproject_path: Explicit pyproject.toml path
            cli_overrides: Dict of CLI-provided overrides
            search_dir: Directory to search for config files (default: cwd)

        Returns:
            CompilerConfig: Validated configuration instance

        Raises:
            ConfigurationError: If configuration is invalid or not found
        """
        config_dict = ConfigService.load_config(
            config_path=config_path,
            pyproject_path=pyproject_path,
            cli_overrides=cli_overrides,
            search_dir=search_dir,
        )

        try:
            return CompilerConfig.from_dict(config_dict)
        except Exception as e:
            raise ConfigurationError(f"Failed to build CompilerConfig: {e}") from e

    # ////////////////////////////////////////////////
    # PRIVATE HELPERS
    # ////////////////////////////////////////////////

    @staticmethod
    def _load_pyproject_layer(
        pyproject_path: Path | None,
        search_dir: Path,
        merged: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Load pyproject.toml as the base configuration layer.

        Args:
            pyproject_path: Explicit pyproject.toml path or None for auto-discovery
            search_dir: Directory to search in
            merged: Current merged config dict

        Returns:
            dict[str, Any]: Updated merged config
        """
        toml_path = pyproject_path or (search_dir / "pyproject.toml")

        if not toml_path.exists():
            return merged

        try:
            toml_data = ConfigUtils.load_toml_config(toml_path)
            pyproject_config = ConfigUtils.extract_pyproject_config(toml_data)
            if pyproject_config:
                merged = ConfigUtils.merge_config_dicts(merged, pyproject_config)
        except TomlNotAvailableError:
            pass  # Skip TOML if parser not available

        return merged

    @staticmethod
    def _load_config_file_layer(
        config_path: Path | None,
        search_dir: Path,
        merged: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Load YAML/JSON config file as overlay layer.

        Args:
            config_path: Explicit config path or None for auto-discovery
            search_dir: Directory to search in
            merged: Current merged config dict

        Returns:
            dict[str, Any]: Updated merged config
        """
        if config_path:
            overlay = ConfigService._load_file_by_extension(config_path)
            return ConfigUtils.merge_config_dicts(merged, overlay)

        # Auto-discover (YAML/JSON only, pyproject already handled)
        discovered = ConfigUtils.discover_config_file(search_dir)
        if discovered and discovered.suffix.lower() != ".toml":
            overlay = ConfigService._load_file_by_extension(discovered)
            return ConfigUtils.merge_config_dicts(merged, overlay)

        return merged

    @staticmethod
    def _load_file_by_extension(path: Path) -> dict[str, Any]:
        """
        Load a config file based on its extension.

        Args:
            path: Path to the config file

        Returns:
            dict[str, Any]: Parsed configuration dictionary

        Raises:
            ConfigFileNotFoundError: If file not found
            ConfigFileParseError: If parsing fails
            ConfigurationError: If extension is unsupported
        """
        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            return ConfigUtils.load_yaml_config(path)
        if suffix == ".json":
            return ConfigUtils.load_json_config(path)
        if suffix == ".toml":
            toml_data = ConfigUtils.load_toml_config(path)
            return ConfigUtils.extract_pyproject_config(toml_data)
        raise ConfigurationError(f"Unsupported config file format: {suffix}")
