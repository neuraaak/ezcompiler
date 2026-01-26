# ///////////////////////////////////////////////////////////////
# TEMPLATES - Template processing and management
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Templates module - Template processing and management for EzCompiler.

This module provides template management and processing functionality for
generating configuration files, version info files, and setup scripts from
templates with variable substitution.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .template_manager import TemplateManager
from .template_utils import TemplateProcessor

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["TemplateManager", "TemplateProcessor"]
