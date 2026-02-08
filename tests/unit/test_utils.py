# ///////////////////////////////////////////////////////////////
# TEST UTILS - Unit tests for utility modules
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Unit tests for utility modules (FileUtils, validators, ZipUtils).

Tests the basic functionality of utility classes and validator functions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ezcompiler.utils import FileUtils, ZipUtils, validators

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


class TestValidators:
    """Test validators module."""

    def test_validators_exists(self) -> None:
        """Test that validators module can be imported."""
        assert validators is not None

    def test_validators_has_functions(self) -> None:
        """Test that validators module has expected functions."""
        assert hasattr(validators, "validate_version_string")
        assert hasattr(validators, "validate_compiler_name")
        assert hasattr(validators, "validate_upload_structure")


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


# ///////////////////////////////////////////////////////////////
# TESTS - FILE UTILS METHODS
# ///////////////////////////////////////////////////////////////


class TestFileUtilsMethods:
    """Test FileUtils methods."""

    def test_file_utils_create_directory(self, temp_dir) -> None:
        """Test FileUtils.create_directory_if_not_exists method."""
        test_dir = temp_dir / "test_directory"
        assert not test_dir.exists()

        FileUtils.create_directory_if_not_exists(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_file_utils_create_directory_existing(self, temp_dir) -> None:
        """Test FileUtils.create_directory_if_not_exists on existing directory."""
        # Directory already exists, should not raise error
        FileUtils.create_directory_if_not_exists(temp_dir)
        assert temp_dir.exists()

    def test_file_utils_get_file_size(self, temp_dir) -> None:
        """Test FileUtils.get_file_size method."""
        test_file = temp_dir / "test_file.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        size = FileUtils.get_file_size(test_file)
        assert size > 0
        assert size == len(test_content.encode())

    def test_file_utils_validate_file_exists(self, temp_dir) -> None:
        """Test FileUtils.validate_file_exists method."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        assert FileUtils.validate_file_exists(test_file) is True
        assert FileUtils.validate_file_exists(temp_dir / "nonexistent.txt") is False


# ///////////////////////////////////////////////////////////////
# TESTS - VALIDATION UTILS METHODS
# ///////////////////////////////////////////////////////////////


class TestValidatorFunctions:
    """Test validator functions."""

    def test_validate_version_valid(self) -> None:
        """Test validators.validate_version_string with valid versions."""
        assert validators.validate_version_string("1.0.0") is True
        assert validators.validate_version_string("2.1.0") is True
        assert validators.validate_version_string("0.0.1") is True

    def test_validate_version_invalid(self) -> None:
        """Test validators.validate_version_string with invalid versions."""
        assert validators.validate_version_string("invalid") is False
        # "1" is technically valid per regex but let's test what passes
        # The regex accepts "1" as valid, so we test that it doesn't accept empty
        assert validators.validate_version_string("") is False
        # Test that it doesn't accept non-numeric
        assert validators.validate_version_string("1.a.0") is False

    def test_validate_compiler_name_valid(self) -> None:
        """Test validators.validate_compiler_name with valid names."""
        assert validators.validate_compiler_name("Cx_Freeze") is True
        assert validators.validate_compiler_name("PyInstaller") is True
        assert validators.validate_compiler_name("Nuitka") is True
        assert validators.validate_compiler_name("auto") is True

    def test_validate_compiler_name_invalid(self) -> None:
        """Test validators.validate_compiler_name with invalid names."""
        assert validators.validate_compiler_name("InvalidCompiler") is False
        assert validators.validate_compiler_name("") is False

    def test_validate_upload_structure_valid(self) -> None:
        """Test validators.validate_upload_structure with valid structures."""
        assert validators.validate_upload_structure("disk") is True
        assert validators.validate_upload_structure("server") is True

    def test_validate_upload_structure_invalid(self) -> None:
        """Test validators.validate_upload_structure with invalid structures."""
        assert validators.validate_upload_structure("ftp") is False
        assert validators.validate_upload_structure("") is False


# ///////////////////////////////////////////////////////////////
# TESTS - ZIP UTILS METHODS
# ///////////////////////////////////////////////////////////////


class TestZipUtilsMethods:
    """Test ZipUtils methods."""

    def test_create_zip_archive(self, temp_dir) -> None:
        """Test ZipUtils.create_zip_archive method."""
        # Create test directory with files
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        # Create zip
        zip_path = temp_dir / "archive.zip"
        ZipUtils.create_zip_archive(source_dir, zip_path)

        assert zip_path.exists()
        assert zip_path.suffix == ".zip"

    def test_list_zip_contents(self, temp_dir) -> None:
        """Test ZipUtils.list_zip_contents method."""
        # Create test directory with files
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        # Create zip
        zip_path = temp_dir / "archive.zip"
        ZipUtils.create_zip_archive(source_dir, zip_path)

        # List contents
        contents = ZipUtils.list_zip_contents(zip_path)
        assert isinstance(contents, list)
        assert len(contents) > 0
