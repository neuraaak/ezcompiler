# ///////////////////////////////////////////////////////////////
# SERVICES - Business logic layer
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Services module - Business logic services for EzCompiler.

This module provides services that implement the core business logic:
- Compiler service for compilation operations
- Config service for configuration management
- Pipeline service for build pipeline orchestration
- Template service for template processing
- Uploader service for artifact distribution

Services can call other services and utils, but not interfaces.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ..shared import CompilationResult, CompilerConfig
from .compiler_service import CompilerService
from .config_service import ConfigService
from .pipeline_service import PipelineService
from .release_service import ReleaseService
from .template_service import TemplateService
from .updater_service import UpdaterService
from .uploader_service import UploaderService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Services
    "CompilerService",
    "CompilerConfig",
    "ConfigService",
    "PipelineService",
    "ReleaseService",
    "TemplateService",
    "UpdaterService",
    "UploaderService",
    # Result types
    "CompilationResult",
]
