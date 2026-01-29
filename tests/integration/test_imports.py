# ///////////////////////////////////////////////////////////////
# TEST IMPORTS - Integration tests for module imports
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Integration tests for module imports and public API.

Tests that all public API components can be imported correctly.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# TESTS - PUBLIC API IMPORTS
# ///////////////////////////////////////////////////////////////


class TestPublicAPIImports:
    """Test that all public API components can be imported."""

    def test_import_ezcompiler_class(self) -> None:
        """Test importing main class from ezcompiler."""
        from ezcompiler import EzCompiler

        assert EzCompiler is not None

    def test_import_compiler_config(self) -> None:
        """Test importing CompilerConfig from ezcompiler."""
        from ezcompiler import CompilerConfig

        assert CompilerConfig is not None

    def test_import_exceptions(self) -> None:
        """Test importing all public exceptions."""
        from ezcompiler import (
            CompilationError,
            ConfigurationError,
            EzCompilerError,
            FileOperationError,
            TemplateError,
            UploadError,
            VersionError,
        )

        assert EzCompilerError is not None
        assert CompilationError is not None
        assert ConfigurationError is not None
        assert TemplateError is not None
        assert UploadError is not None
        assert VersionError is not None
        assert FileOperationError is not None

    def test_import_metadata(self) -> None:
        """Test importing metadata attributes."""
        from ezcompiler import __author__, __version__

        assert __version__ is not None
        assert __author__ is not None

    def test_exception_hierarchy(self) -> None:
        """Test that all exceptions inherit from EzCompilerError."""
        from ezcompiler import (
            CompilationError,
            ConfigurationError,
            EzCompilerError,
            TemplateError,
            UploadError,
            VersionError,
        )

        assert issubclass(CompilationError, EzCompilerError)
        assert issubclass(ConfigurationError, EzCompilerError)
        assert issubclass(TemplateError, EzCompilerError)
        assert issubclass(UploadError, EzCompilerError)
        assert issubclass(VersionError, EzCompilerError)
