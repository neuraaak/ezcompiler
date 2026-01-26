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

    def test_import_from_ezcompiler_main(self) -> None:
        """Test importing main class from ezcompiler."""
        from ezcompiler import EzCompiler

        assert EzCompiler is not None

    def test_import_config_from_ezcompiler(self) -> None:
        """Test importing CompilerConfig from ezcompiler."""
        from ezcompiler import CompilerConfig

        assert CompilerConfig is not None

    def test_import_compilers(self) -> None:
        """Test importing compiler classes."""
        from ezcompiler import BaseCompiler, CxFreezeCompiler, PyInstallerCompiler

        assert BaseCompiler is not None
        assert CxFreezeCompiler is not None
        assert PyInstallerCompiler is not None

    def test_import_generators(self) -> None:
        """Test importing generator classes."""
        from ezcompiler import SetupGenerator, VersionGenerator

        assert VersionGenerator is not None
        assert SetupGenerator is not None

    def test_import_uploaders(self) -> None:
        """Test importing uploader classes."""
        from ezcompiler import (
            BaseUploader,
            DiskUploader,
            ServerUploader,
            UploaderFactory,
        )

        assert BaseUploader is not None
        assert DiskUploader is not None
        assert ServerUploader is not None
        assert UploaderFactory is not None

    def test_import_utils(self) -> None:
        """Test importing utility classes."""
        from ezcompiler import FileUtils, ValidationUtils, ZipUtils

        assert FileUtils is not None
        assert ZipUtils is not None
        assert ValidationUtils is not None
