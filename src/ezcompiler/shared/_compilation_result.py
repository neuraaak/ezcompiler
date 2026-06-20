# ///////////////////////////////////////////////////////////////
# COMPILATION_RESULT - Result type for compilation operations
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
CompilationResult - Shared result type for compilation operations.

Defined in shared/ so it can be consumed by services, pipeline,
and interfaces without creating inter-service dependencies.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import CompilerPort

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class CompilationResult:
    """
    Result of a compilation operation.

    Contains information about the compilation result, including whether
    the output needs to be zipped and the compiler instance used.

    Attributes:
        zip_needed: Whether the compiled output needs to be zipped
        compiler_name: Name of the compiler used
        _compiler_instance: The compiler instance that performed the compilation

    Example:
        >>> result = service.compile(compiler="PyInstaller")
        >>> if result.zip_needed:
        ...     # Create ZIP archive
    """

    def __init__(
        self,
        zip_needed: bool,
        compiler_name: str,
        compiler_instance: CompilerPort,
    ) -> None:
        """
        Initialize compilation result.

        Args:
            zip_needed: Whether output needs to be zipped
            compiler_name: Name of compiler used
            compiler_instance: Compiler instance that performed compilation
        """
        self.zip_needed = zip_needed
        self.compiler_name = compiler_name
        self._compiler_instance = compiler_instance
