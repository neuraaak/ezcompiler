# ///////////////////////////////////////////////////////////////
# INTERFACES - Public interfaces layer
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Interfaces module - Public interfaces for EzCompiler.

This module provides the top-level interfaces that users interact with:
- CLI interface for command-line operations
- Python API interface for programmatic usage

Interfaces can call services but not utils directly.

Ezpl logging is initialized here and configured during EzCompiler instantiation.
Instances of ezpl, ezprinter, and ezlogger are accessible via this module.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import cast

# Third-party imports
from ezpl import EzLogger, Ezpl, EzPrinter

# Local imports
from .cli_interface import main as cli_main
from .python_api import EzCompiler

# ///////////////////////////////////////////////////////////////
# EZPL INITIALIZATION
# ///////////////////////////////////////////////////////////////

# Global ezpl instance - initialized on first use
_ezpl_instance: Ezpl | None = None
_printer_instance: EzPrinter | None = None
_logger_instance: EzLogger | None = None


def _initialize_ezpl(log_file: Path | None = None) -> Ezpl:
    """
    Initialize ezpl instance if not already created.

    Args:
        log_file: Optional path to log file (default: None)

    Returns:
        Ezpl: Initialized ezpl instance
    """
    global _ezpl_instance, _printer_instance, _logger_instance

    if _ezpl_instance is None:
        _ezpl_instance = Ezpl(log_file=log_file) if log_file else Ezpl()
        _printer_instance = cast(EzPrinter, _ezpl_instance.get_printer())
        _logger_instance = _ezpl_instance.get_logger()

    return _ezpl_instance


def configure_ezpl(
    log_file: Path | None = None,
    log_rotation: str = "1 day",
    log_retention: str = "14 days",
    log_compression: str = "zip",
    log_level: str = "INFO",
) -> Ezpl:
    """
    Configure ezpl instance with specified settings.

    Initializes ezpl if not already created and configures it with
    the provided settings. This is typically called during EzCompiler
    instantiation.

    Args:
        log_file: Optional path to log file (default: None)
        log_rotation: Log rotation setting (default: "1 day")
        log_retention: Log retention setting (default: "14 days")
        log_compression: Log compression setting (default: "zip")
        log_level: Log level (default: "INFO")

    Returns:
        Ezpl: Configured ezpl instance

    Example:
        >>> ezpl = configure_ezpl(log_file=Path("app.log"), log_level="DEBUG")
    """
    global _ezpl_instance, _printer_instance, _logger_instance

    # Initialize if needed
    if _ezpl_instance is None:
        _ezpl_instance = Ezpl(log_file=log_file) if log_file else Ezpl()
        _printer_instance = cast(EzPrinter, _ezpl_instance.get_printer())
        _logger_instance = _ezpl_instance.get_logger()

    # Configure
    _ezpl_instance.configure(
        log_rotation=log_rotation,
        log_retention=log_retention,
        log_compression=log_compression,
    )
    _ezpl_instance.set_level(log_level)

    return _ezpl_instance


def get_ezpl() -> Ezpl:
    """
    Get the global ezpl instance.

    Returns:
        Ezpl: Global ezpl instance (initialized if needed)

    Example:
        >>> ezpl = get_ezpl()
    """
    return _initialize_ezpl()


def get_printer() -> EzPrinter:
    """
    Get the global printer instance.

    Returns:
        EzPrinter: Global printer instance (initialized if needed)

    Example:
        >>> printer = get_printer()
        >>> printer.info("Message")
    """
    global _printer_instance

    if _printer_instance is None:
        _initialize_ezpl()

    return cast(EzPrinter, _printer_instance)


def get_logger() -> EzLogger:
    """
    Get the global logger instance.

    Returns:
        EzLogger: Global logger instance (initialized if needed)

    Example:
        >>> logger = get_logger()
        >>> logger.info("Message")
    """
    global _logger_instance

    if _logger_instance is None:
        _initialize_ezpl()

    return cast(EzLogger, _logger_instance)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Main interfaces
    "EzCompiler",
    "cli_main",
    # Ezpl access
    "get_ezpl",
    "get_printer",
    "get_logger",
    "configure_ezpl",
]
