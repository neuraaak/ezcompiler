# ///////////////////////////////////////////////////////////////
# BASE - Base exception for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base exception - Core exception class for all EzCompiler errors.

This module defines the base exception class that all other exceptions inherit from.
"""

from __future__ import annotations

from ..utils.base import EzCompilerError


class EzCompilerServiceError(EzCompilerError):
    """Base exception for all EzCompiler services errors."""
