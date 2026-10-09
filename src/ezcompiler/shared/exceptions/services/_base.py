# ///////////////////////////////////////////////////////////////
# BASE - Base exception for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Base exception - Core exception class for all EzCompiler errors.

This module defines the base exception class that all other exceptions inherit from.
"""

from __future__ import annotations

from ..utils._base import EzCompilerError


# Note: `UploadError` is defined once (services/_service_exceptions.py);
# the granular uploader exceptions (utils/_uploader_exceptions.py) inherit from it.
# Il n'y a donc plus de doublon `UploadError` entre les deux sous-arbres.
class EzCompilerServiceError(EzCompilerError):
    """Base exception for all EzCompiler services errors."""
