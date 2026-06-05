# ///////////////////////////////////////////////////////////////
# PORTS - Structural contracts for adapter implementations
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Ports module - Structural contracts (Protocol) for compiler and uploader adapters.

Re-exports CompilerPort and UploaderPort from ezcompiler.types so that
adapter-layer code can import from a single, discoverable location.
"""

from __future__ import annotations

from ..types import CompilerPort, UploaderPort

__all__ = [
    "CompilerPort",
    "UploaderPort",
]
