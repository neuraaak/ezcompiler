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

Logging follows the lib_mode pattern: get_logger and get_printer return
passive proxies that are silent by default and become active once the
host application initializes Ezpl. No Ezpl() init or configure() calls
belong here — those are application-level responsibilities.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .cli_interface import main as cli_main
from .python_api import EzCompiler

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Main interfaces
    "EzCompiler",
    "cli_main",
]
