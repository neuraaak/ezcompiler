# ///////////////////////////////////////////////////////////////
# TEST UTILS - Unit tests for utility modules
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Unit tests for utility modules (FileUtils, ValidationUtils, ZipUtils).

Tests the basic functionality of utility classes.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ezcompiler.utils import FileUtils, ValidationUtils, ZipUtils

# ///////////////////////////////////////////////////////////////
# TESTS - FILE UTILS
# ///////////////////////////////////////////////////////////////


class TestFileUtils:
    """Test FileUtils class."""

    def test_file_utils_exists(self) -> None:
        """Test that FileUtils can be imported."""
        assert FileUtils is not None

    def test_file_utils_instantiate(self) -> None:
        """Test that FileUtils can be instantiated."""
        file_utils = FileUtils()
        assert isinstance(file_utils, FileUtils)


# ///////////////////////////////////////////////////////////////
# TESTS - VALIDATION UTILS
# ///////////////////////////////////////////////////////////////


class TestValidationUtils:
    """Test ValidationUtils class."""

    def test_validation_utils_exists(self) -> None:
        """Test that ValidationUtils can be imported."""
        assert ValidationUtils is not None

    def test_validation_utils_instantiate(self) -> None:
        """Test that ValidationUtils can be instantiated."""
        validation_utils = ValidationUtils()
        assert isinstance(validation_utils, ValidationUtils)


# ///////////////////////////////////////////////////////////////
# TESTS - ZIP UTILS
# ///////////////////////////////////////////////////////////////


class TestZipUtils:
    """Test ZipUtils class."""

    def test_zip_utils_exists(self) -> None:
        """Test that ZipUtils can be imported."""
        assert ZipUtils is not None

    def test_zip_utils_instantiate(self) -> None:
        """Test that ZipUtils can be instantiated."""
        zip_utils = ZipUtils()
        assert isinstance(zip_utils, ZipUtils)
