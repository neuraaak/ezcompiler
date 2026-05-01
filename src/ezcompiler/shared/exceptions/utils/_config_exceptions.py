# ///////////////////////////////////////////////////////////////
# CONFIG_EXCEPTIONS - Configuration exceptions
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Configuration exceptions - Specialized exceptions for configuration operations.

This module defines exceptions for various configuration-related failures
used by ConfigUtils and configuration validation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ._base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ConfigError(EzCompilerError):
    """Base exception for configuration errors."""


class ConfigFieldValidationError(ConfigError):
    """Raised when configuration field validation fails."""


class ConfigPathError(ConfigError):
    """Raised when configuration paths are invalid."""


class CompilerOptionError(ConfigError):
    """Raised when compiler option is invalid."""


class OutputFolderError(ConfigError):
    """Raised when output folder configuration is invalid."""


class IncludeFilesError(ConfigError):
    """Raised when include files configuration is invalid."""


class MissingRequiredConfigError(ConfigError):
    """Raised when required configuration is missing."""


class ConfigFileNotFoundError(ConfigError):
    """Raised when a configuration file cannot be found."""


class ConfigFileParseError(ConfigError):
    """Raised when a configuration file cannot be parsed."""


class TomlNotAvailableError(ConfigError):
    """Raised when TOML parsing is requested but tomllib/tomli is not available."""
