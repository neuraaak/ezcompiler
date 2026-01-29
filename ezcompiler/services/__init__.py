# ///////////////////////////////////////////////////////////////
# SERVICES - Business logic layer
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Services module - Business logic services for EzCompiler.

This module provides services that implement the core business logic:
- Compiler service for compilation operations
- Config service for configuration management
- Template service for template processing
- Uploader service for artifact distribution

Services can call other services and utils, but not interfaces.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ..shared import CompilerConfig
from .compiler_service import CompilationResult, CompilerService
from .config_service import ConfigService
from .template_service import TemplateService
from .uploader_service import UploaderService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Services
    "CompilerService",
    "CompilerConfig",
    "ConfigService",
    "TemplateService",
    "UploaderService",
    # Result types
    "CompilationResult",
]
