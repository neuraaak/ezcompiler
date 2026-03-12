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
from pathlib import Path

import pytest

from ezcompiler.shared.exceptions.utils.file_exceptions import (
    FileNotFoundError,
)
from ezcompiler.shared.exceptions.utils.template_exceptions import (
    TemplateFileWriteError,
    TemplateValidationError,
)
from ezcompiler.shared.exceptions.utils.validation_exceptions import (
    ChoiceValidationError,
    LengthValidationError,
    RangeValidationError,
    RequiredFieldError,
    SchemaValidationError,
    TypeValidationError,
)
from ezcompiler.shared.exceptions.utils.zip_exceptions import (
    ZipCreationError,
    ZipExtractionError,
    ZipFileCorruptedError,
)
from ezcompiler.utils import FileUtils, ZipUtils, validators
from ezcompiler.utils.template_utils import TemplateProcessor
from ezcompiler.utils.validators.schema_validators import (
    validate_config_dict,
    validate_dict_schema,
    validate_field_types,
    validate_required_fields,
)
from ezcompiler.utils.validators.value_validators import (
    validate_choice,
    validate_length,
    validate_list_length,
    validate_not_empty,
    validate_numeric_range,
    validate_one_of,
    validate_string_length,
    validate_value_in_range,
)

# ///////////////////////////////////////////////////////////////
# TESTS - FILE UTILS
# ///////////////////////////////////////////////////////////////


class TestFileUtils:
    """Test FileUtils class."""

    def test_should_be_importable_when_file_utils_is_loaded(self) -> None:
        """Test that FileUtils can be imported."""
        assert FileUtils is not None

    def test_should_instantiate_when_file_utils_is_created(self) -> None:
        """Test that FileUtils can be instantiated."""
        file_utils = FileUtils()
        assert isinstance(file_utils, FileUtils)


# ///////////////////////////////////////////////////////////////
# TESTS - VALIDATION UTILS
# ///////////////////////////////////////////////////////////////


class TestValidators:
    """Test validators module."""

    def test_should_be_importable_when_validators_module_is_loaded(self) -> None:
        """Test that validators module can be imported."""
        assert validators is not None

    def test_should_have_expected_functions_when_validators_module_is_loaded(
        self,
    ) -> None:
        """Test that validators module has expected functions."""
        assert hasattr(validators, "validate_version_string")
        assert hasattr(validators, "validate_compiler_name")
        assert hasattr(validators, "validate_upload_structure")


# ///////////////////////////////////////////////////////////////
# TESTS - ZIP UTILS
# ///////////////////////////////////////////////////////////////


class TestZipUtils:
    """Test ZipUtils class."""

    def test_should_be_importable_when_zip_utils_is_loaded(self) -> None:
        """Test that ZipUtils can be imported."""
        assert ZipUtils is not None

    def test_should_instantiate_when_zip_utils_is_created(self) -> None:
        """Test that ZipUtils can be instantiated."""
        zip_utils = ZipUtils()
        assert isinstance(zip_utils, ZipUtils)


# ///////////////////////////////////////////////////////////////
# TESTS - FILE UTILS METHODS
# ///////////////////////////////////////////////////////////////


class TestFileUtilsMethods:
    """Test FileUtils methods."""

    def test_should_create_directory_when_path_does_not_exist(self, temp_dir) -> None:
        """Test FileUtils.create_directory_if_not_exists method."""
        test_dir = temp_dir / "test_directory"
        assert not test_dir.exists()

        FileUtils.create_directory_if_not_exists(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_should_not_raise_when_directory_already_exists(self, temp_dir) -> None:
        """Test FileUtils.create_directory_if_not_exists on existing directory."""
        FileUtils.create_directory_if_not_exists(temp_dir)
        assert temp_dir.exists()

    def test_should_return_size_when_file_exists(self, temp_dir) -> None:
        """Test FileUtils.get_file_size method."""
        test_file = temp_dir / "test_file.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        size = FileUtils.get_file_size(test_file)
        assert size > 0
        assert size == len(test_content.encode())

    def test_should_return_true_when_file_exists_and_false_when_not(
        self, temp_dir
    ) -> None:
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

    def test_should_return_true_when_version_string_is_valid(self) -> None:
        """Test validators.validate_version_string with valid versions."""
        assert validators.validate_version_string("1.0.0") is True
        assert validators.validate_version_string("2.1.0") is True
        assert validators.validate_version_string("0.0.1") is True

    def test_should_return_false_when_version_string_is_invalid(self) -> None:
        """Test validators.validate_version_string with invalid versions."""
        assert validators.validate_version_string("invalid") is False
        assert validators.validate_version_string("") is False
        assert validators.validate_version_string("1.a.0") is False

    def test_should_return_true_when_compiler_name_is_valid(self) -> None:
        """Test validators.validate_compiler_name with valid names."""
        assert validators.validate_compiler_name("Cx_Freeze") is True
        assert validators.validate_compiler_name("PyInstaller") is True
        assert validators.validate_compiler_name("Nuitka") is True
        assert validators.validate_compiler_name("auto") is True

    def test_should_return_false_when_compiler_name_is_invalid(self) -> None:
        """Test validators.validate_compiler_name with invalid names."""
        assert validators.validate_compiler_name("InvalidCompiler") is False
        assert validators.validate_compiler_name("") is False

    def test_should_return_true_when_upload_structure_is_valid(self) -> None:
        """Test validators.validate_upload_structure with valid structures."""
        assert validators.validate_upload_structure("disk") is True
        assert validators.validate_upload_structure("server") is True

    def test_should_return_false_when_upload_structure_is_invalid(self) -> None:
        """Test validators.validate_upload_structure with invalid structures."""
        assert validators.validate_upload_structure("ftp") is False
        assert validators.validate_upload_structure("") is False


# ///////////////////////////////////////////////////////////////
# TESTS - ZIP UTILS METHODS
# ///////////////////////////////////////////////////////////////


class TestZipUtilsMethods:
    """Test ZipUtils methods."""

    def test_should_create_zip_when_source_directory_has_files(self, temp_dir) -> None:
        """Test ZipUtils.create_zip_archive method."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        zip_path = temp_dir / "archive.zip"
        ZipUtils.create_zip_archive(source_dir, zip_path)

        assert zip_path.exists()
        assert zip_path.suffix == ".zip"

    def test_should_return_contents_when_zip_is_listed(self, temp_dir) -> None:
        """Test ZipUtils.list_zip_contents method."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        zip_path = temp_dir / "archive.zip"
        ZipUtils.create_zip_archive(source_dir, zip_path)

        contents = ZipUtils.list_zip_contents(zip_path)
        assert isinstance(contents, list)
        assert len(contents) > 0

    def test_should_archive_single_file_when_source_is_a_file(
        self, temp_dir: Path
    ) -> None:
        source_file = temp_dir / "single.txt"
        source_file.write_text("hello")
        zip_path = temp_dir / "out.zip"

        ZipUtils.create_zip_archive(source_file, zip_path)

        assert zip_path.exists()
        assert "single.txt" in ZipUtils.list_zip_contents(zip_path)

    def test_should_call_progress_callback_when_archiving_single_file(
        self, temp_dir: Path
    ) -> None:
        source_file = temp_dir / "cb.txt"
        source_file.write_text("data")
        zip_path = temp_dir / "cb.zip"
        calls: list[tuple[str, int]] = []

        ZipUtils.create_zip_archive(
            source_file, zip_path, progress_callback=lambda f, p: calls.append((f, p))
        )

        assert len(calls) == 1
        assert calls[0][1] == 100

    def test_should_call_progress_callback_when_archiving_directory(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "a.txt").write_text("a")
        (src / "b.txt").write_text("b")
        zip_path = temp_dir / "dir.zip"
        calls: list[int] = []

        ZipUtils.create_zip_archive(
            src, zip_path, progress_callback=lambda _f, p: calls.append(p)
        )

        assert len(calls) == 2
        assert calls[-1] == 100

    def test_should_exclude_hidden_files_when_include_hidden_is_false(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "visible.txt").write_text("v")
        (src / ".hidden.txt").write_text("h")
        zip_path = temp_dir / "nohidden.zip"

        ZipUtils.create_zip_archive(src, zip_path, include_hidden=False)

        contents = ZipUtils.list_zip_contents(zip_path)
        assert "visible.txt" in contents
        assert ".hidden.txt" not in contents

    def test_should_include_hidden_files_when_include_hidden_is_true(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "visible.txt").write_text("v")
        (src / ".hidden.txt").write_text("h")
        zip_path = temp_dir / "withhidden.zip"

        ZipUtils.create_zip_archive(src, zip_path, include_hidden=True)

        contents = ZipUtils.list_zip_contents(zip_path)
        assert ".hidden.txt" in contents

    def test_should_raise_zip_creation_error_when_source_does_not_exist(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(ZipCreationError):
            ZipUtils.create_zip_archive(temp_dir / "missing", temp_dir / "out.zip")

    def test_should_extract_files_when_zip_is_valid(self, temp_dir: Path) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "extract_me.txt").write_text("content")
        zip_path = temp_dir / "archive.zip"
        ZipUtils.create_zip_archive(src, zip_path)
        extract_dir = temp_dir / "extracted"

        ZipUtils.extract_zip_archive(zip_path, extract_dir)

        assert (extract_dir / "extract_me.txt").exists()

    def test_should_call_progress_callback_when_extracting_zip(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "f.txt").write_text("x")
        zip_path = temp_dir / "ex.zip"
        ZipUtils.create_zip_archive(src, zip_path)
        calls: list[int] = []
        extract_dir = temp_dir / "out"

        ZipUtils.extract_zip_archive(
            zip_path, extract_dir, progress_callback=lambda _f, p: calls.append(p)
        )

        assert len(calls) > 0

    def test_should_raise_zip_extraction_error_when_zip_does_not_exist(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(ZipExtractionError):
            ZipUtils.extract_zip_archive(temp_dir / "ghost.zip", temp_dir / "out")

    def test_should_raise_zip_extraction_error_when_path_is_a_directory(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(ZipExtractionError):
            ZipUtils.extract_zip_archive(temp_dir, temp_dir / "out")

    def test_should_raise_zip_file_corrupted_error_when_zip_missing_for_list(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(ZipFileCorruptedError):
            ZipUtils.list_zip_contents(temp_dir / "ghost.zip")

    def test_should_return_correct_metadata_when_zip_contains_known_files(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "a.txt").write_text("hello")
        zip_path = temp_dir / "info.zip"
        ZipUtils.create_zip_archive(src, zip_path)

        info = ZipUtils.get_zip_info(zip_path)

        assert info["file_count"] == 1
        assert "a.txt" in info["files"]
        assert info["total_size"] >= 0

    def test_should_return_zero_compression_ratio_when_zip_is_empty(
        self, temp_dir: Path
    ) -> None:
        import zipfile as _zf

        zip_path = temp_dir / "empty.zip"
        with _zf.ZipFile(zip_path, "w"):
            pass

        info = ZipUtils.get_zip_info(zip_path)
        assert info["compression_ratio"] == 0
        assert info["file_count"] == 0

    def test_should_raise_zip_file_corrupted_error_when_zip_missing_for_info(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(ZipFileCorruptedError):
            ZipUtils.get_zip_info(temp_dir / "ghost.zip")

    def test_should_return_true_when_zip_is_valid(self, temp_dir: Path) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "f.txt").write_text("x")
        zip_path = temp_dir / "valid.zip"
        ZipUtils.create_zip_archive(src, zip_path)

        assert ZipUtils.is_valid_zip(zip_path) is True

    def test_should_return_false_when_file_does_not_exist_for_is_valid(
        self, temp_dir: Path
    ) -> None:
        assert ZipUtils.is_valid_zip(temp_dir / "ghost.zip") is False

    def test_should_return_false_when_file_is_not_a_zip(self, temp_dir: Path) -> None:
        not_a_zip = temp_dir / "file.zip"
        not_a_zip.write_text("this is not a zip")

        assert ZipUtils.is_valid_zip(not_a_zip) is False

    def test_should_add_file_to_existing_zip_when_arcname_is_default(
        self, temp_dir: Path
    ) -> None:
        import zipfile as _zf

        zip_path = temp_dir / "add.zip"
        with _zf.ZipFile(zip_path, "w"):
            pass
        new_file = temp_dir / "extra.txt"
        new_file.write_text("extra")

        ZipUtils.add_file_to_zip(zip_path, new_file)

        assert "extra.txt" in ZipUtils.list_zip_contents(zip_path)

    def test_should_add_file_with_custom_arcname_when_arcname_is_provided(
        self, temp_dir: Path
    ) -> None:
        import zipfile as _zf

        zip_path = temp_dir / "add2.zip"
        with _zf.ZipFile(zip_path, "w"):
            pass
        new_file = temp_dir / "extra.txt"
        new_file.write_text("extra")

        ZipUtils.add_file_to_zip(zip_path, new_file, arcname="custom_name.txt")

        assert "custom_name.txt" in ZipUtils.list_zip_contents(zip_path)

    def test_should_raise_zip_creation_error_when_file_to_add_does_not_exist(
        self, temp_dir: Path
    ) -> None:
        import zipfile as _zf

        zip_path = temp_dir / "add3.zip"
        with _zf.ZipFile(zip_path, "w"):
            pass

        with pytest.raises(ZipCreationError):
            ZipUtils.add_file_to_zip(zip_path, temp_dir / "ghost.txt")

    def test_should_remove_file_when_it_exists_in_zip(self, temp_dir: Path) -> None:
        src = temp_dir / "src"
        src.mkdir()
        (src / "keep.txt").write_text("keep")
        (src / "remove.txt").write_text("remove")
        zip_path = temp_dir / "rem.zip"
        ZipUtils.create_zip_archive(src, zip_path)

        ZipUtils.remove_file_from_zip(zip_path, "remove.txt")

        contents = ZipUtils.list_zip_contents(zip_path)
        assert "keep.txt" in contents
        assert "remove.txt" not in contents

    def test_should_raise_zip_creation_error_when_zip_missing_for_remove(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(ZipCreationError):
            ZipUtils.remove_file_from_zip(temp_dir / "ghost.zip", "file.txt")

    def test_should_return_true_when_filename_starts_with_dot(
        self, temp_dir: Path
    ) -> None:
        hidden = temp_dir / ".dotfile"
        hidden.write_text("h")
        assert ZipUtils._is_hidden_file(hidden) is True

    def test_should_return_false_when_filename_is_normal(self, temp_dir: Path) -> None:
        normal = temp_dir / "normal.txt"
        normal.write_text("n")
        assert ZipUtils._is_hidden_file(normal) is False


# ///////////////////////////////////////////////////////////////
# TESTS - FILE UTILS METHODS (extended)
# ///////////////////////////////////////////////////////////////


class TestFileUtilsMethodsExtended:
    """Extended tests for FileUtils methods."""

    def test_should_return_true_when_directory_exists(self, temp_dir: Path) -> None:
        assert FileUtils.validate_directory_exists(temp_dir) is True

    def test_should_return_false_when_path_is_a_file_not_directory(
        self, temp_dir: Path
    ) -> None:
        f = temp_dir / "f.txt"
        f.write_text("x")
        assert FileUtils.validate_directory_exists(f) is False

    def test_should_return_false_when_directory_does_not_exist(
        self, temp_dir: Path
    ) -> None:
        assert FileUtils.validate_directory_exists(temp_dir / "missing") is False

    def test_should_create_parent_dirs_when_path_is_nested(
        self, temp_dir: Path
    ) -> None:
        nested = temp_dir / "a" / "b" / "c.txt"
        FileUtils.ensure_parent_directory_exists(nested)
        assert (temp_dir / "a" / "b").is_dir()

    def test_should_not_raise_when_parent_already_exists(self, temp_dir: Path) -> None:
        f = temp_dir / "existing.txt"
        FileUtils.ensure_parent_directory_exists(f)  # temp_dir already exists

    def test_should_raise_file_not_found_error_when_file_missing_for_size(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(FileNotFoundError):
            FileUtils.get_file_size(temp_dir / "ghost.txt")

    def test_should_copy_file_with_metadata_when_preserve_metadata_is_true(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src.txt"
        src.write_text("copy me")
        dst = temp_dir / "dst.txt"

        FileUtils.copy_file(src, dst, preserve_metadata=True)

        assert dst.exists()
        assert dst.read_text() == "copy me"

    def test_should_copy_file_without_metadata_when_preserve_metadata_is_false(
        self, temp_dir: Path
    ) -> None:
        src = temp_dir / "src2.txt"
        src.write_text("no meta")
        dst = temp_dir / "dst2.txt"

        FileUtils.copy_file(src, dst, preserve_metadata=False)

        assert dst.exists()
        assert dst.read_text() == "no meta"

    def test_should_raise_file_not_found_error_when_copy_source_missing(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(FileNotFoundError):
            FileUtils.copy_file(temp_dir / "ghost.txt", temp_dir / "dst.txt")

    def test_should_move_file_when_source_exists(self, temp_dir: Path) -> None:
        src = temp_dir / "move_me.txt"
        src.write_text("move")
        dst = temp_dir / "moved.txt"

        FileUtils.move_file(src, dst)

        assert not src.exists()
        assert dst.exists()
        assert dst.read_text() == "move"

    def test_should_raise_file_not_found_error_when_move_source_missing(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(FileNotFoundError):
            FileUtils.move_file(temp_dir / "ghost.txt", temp_dir / "dst.txt")

    def test_should_delete_file_when_file_exists(self, temp_dir: Path) -> None:
        f = temp_dir / "del.txt"
        f.write_text("bye")

        FileUtils.delete_file(f)

        assert not f.exists()

    def test_should_not_raise_when_deleting_nonexistent_file(
        self, temp_dir: Path
    ) -> None:
        FileUtils.delete_file(temp_dir / "ghost.txt")  # must not raise

    def test_should_list_files_when_directory_contains_files(
        self, temp_dir: Path
    ) -> None:
        (temp_dir / "a.txt").write_text("a")
        (temp_dir / "b.txt").write_text("b")

        files = FileUtils.list_files(temp_dir)

        names = [f.name for f in files]
        assert "a.txt" in names
        assert "b.txt" in names

    def test_should_filter_by_pattern_when_pattern_is_provided(
        self, temp_dir: Path
    ) -> None:
        (temp_dir / "a.txt").write_text("a")
        (temp_dir / "b.py").write_text("b")

        files = FileUtils.list_files(temp_dir, pattern="*.txt")

        names = [f.name for f in files]
        assert "a.txt" in names
        assert "b.py" not in names

    def test_should_raise_file_not_found_error_when_list_directory_missing(
        self, temp_dir: Path
    ) -> None:
        with pytest.raises(FileNotFoundError):
            FileUtils.list_files(temp_dir / "ghost_dir")

    def test_should_return_extension_when_file_has_one(self) -> None:
        assert FileUtils.get_file_extension("file.txt") == ".txt"
        assert FileUtils.get_file_extension("archive.tar.gz") == ".gz"

    def test_should_return_empty_string_when_file_has_no_extension(self) -> None:
        assert FileUtils.get_file_extension("noext") == ""

    def test_should_return_stem_when_file_has_extension(self) -> None:
        assert FileUtils.get_file_name_without_extension("file.txt") == "file"
        assert FileUtils.get_file_name_without_extension("app.exe") == "app"

    def test_should_return_true_when_filename_starts_with_dot(self) -> None:
        assert FileUtils.is_hidden_file(".hidden") is True
        assert FileUtils.is_hidden_file(".gitignore") is True

    def test_should_return_false_when_filename_is_normal(self) -> None:
        assert FileUtils.is_hidden_file("visible.txt") is False

    def test_should_return_relative_path_when_target_is_under_base(
        self, temp_dir: Path
    ) -> None:
        target = temp_dir / "sub" / "file.txt"
        result = FileUtils.get_relative_path(temp_dir, target)
        assert "sub" in result
        assert "file.txt" in result

    def test_should_return_absolute_path_when_target_is_not_under_base(
        self, temp_dir: Path
    ) -> None:
        import tempfile

        other_dir = Path(tempfile.gettempdir())
        result = FileUtils.get_relative_path(temp_dir, other_dir)
        assert Path(result).is_absolute()

    def test_should_return_absolute_path_when_normalizing_relative_path(self) -> None:
        result = FileUtils.normalize_path(".")
        assert result.is_absolute()

    def test_should_return_original_path_when_file_does_not_exist(
        self, temp_dir: Path
    ) -> None:
        p = temp_dir / "new.txt"
        assert FileUtils.ensure_unique_filename(p) == p

    def test_should_return_suffixed_path_when_file_exists(self, temp_dir: Path) -> None:
        p = temp_dir / "dup.txt"
        p.write_text("x")

        result = FileUtils.ensure_unique_filename(p)

        assert result != p
        assert "dup_1" in result.name

    def test_should_increment_counter_when_multiple_conflicts_exist(
        self, temp_dir: Path
    ) -> None:
        p = temp_dir / "dup.txt"
        p.write_text("x")
        (temp_dir / "dup_1.txt").write_text("x")

        result = FileUtils.ensure_unique_filename(p)

        assert "dup_2" in result.name


# ///////////////////////////////////////////////////////////////
# TESTS - TEMPLATE PROCESSOR
# ///////////////////////////////////////////////////////////////


class TestTemplateProcessor:
    """Test TemplateProcessor methods."""

    def test_should_return_dict_with_expected_keys_when_create_mockup_config_called(
        self,
    ) -> None:
        config = TemplateProcessor.create_mockup_config()
        assert isinstance(config, dict)
        for key in ("version", "project_name", "main_file", "include_files"):
            assert key in config

    def test_should_replace_placeholders_when_processing_with_mockup(self) -> None:
        template = "version=#VERSION# name=#PROJECT_NAME#"
        result = TemplateProcessor.process_template_with_mockup(template)
        assert "#VERSION#" not in result
        assert "#PROJECT_NAME#" not in result

    def test_should_return_string_unchanged_when_template_has_no_placeholders(
        self,
    ) -> None:
        template = "no placeholders here"
        result = TemplateProcessor.process_template_with_mockup(template)
        assert result == "no placeholders here"

    def test_should_replace_version_placeholder_when_version_is_standard(self) -> None:
        result = TemplateProcessor.process_version_template(
            template="#FIXED_VERSION# #STRING_VERSION#",
            version="2.1.0",
            company_name="ACME",
            project_description="Desc",
            project_name="App",
        )
        assert "(2, 1, 0, 0)" in result
        assert "2.1.0" in result

    def test_should_pad_version_to_4_parts_when_version_has_fewer_parts(self) -> None:
        result = TemplateProcessor.process_version_template(
            template="#FIXED_VERSION#",
            version="1.0",
            company_name="C",
            project_description="D",
            project_name="P",
        )
        assert "(1, 0, 0, 0)" in result

    def test_should_include_current_year_when_year_placeholder_present(self) -> None:
        from datetime import datetime

        result = TemplateProcessor.process_version_template(
            template="#YEAR#",
            version="1.0.0",
            company_name="C",
            project_description="D",
            project_name="P",
        )
        assert str(datetime.now().year) in result

    def test_should_replace_company_name_in_version_template(self) -> None:
        result = TemplateProcessor.process_version_template(
            template="#COMPANY_NAME# #LEGAL_COPYRIGHT#",
            version="1.0.0",
            company_name="MyCompany",
            project_description="D",
            project_name="P",
        )
        assert "MyCompany" in result

    def test_should_replace_all_placeholders_in_config_template(self) -> None:
        placeholders = [
            "#VERSION#",
            "#PROJECT_NAME#",
            "#MAIN_FILE#",
            "#CONSOLE#",
            "#COMPILER#",
            "#ZIP_NEEDED#",
        ]
        template = " ".join(placeholders)
        result = TemplateProcessor.process_config_template(
            template,
            {
                "version": "1.0.0",
                "project_name": "App",
                "main_file": "main.py",
                "compilation": {
                    "console": True,
                    "compiler": "auto",
                    "zip_needed": True,
                },
            },
        )
        for p in placeholders:
            assert p not in result

    def test_should_serialize_booleans_as_lowercase_in_config_template(self) -> None:
        result = TemplateProcessor.process_config_template(
            "#CONSOLE# #ZIP_NEEDED# #REPO_NEEDED#",
            {
                "compilation": {
                    "console": True,
                    "zip_needed": False,
                    "repo_needed": False,
                }
            },
        )
        assert "true" in result
        assert "false" in result
        assert "True" not in result
        assert "False" not in result

    def test_should_serialize_lists_as_json_in_config_template(self) -> None:
        result = TemplateProcessor.process_config_template(
            "#PACKAGES#",
            {"packages": ["requests", "click"]},
        )
        assert '["requests", "click"]' in result

    def test_should_replace_all_placeholders_in_setup_template(self) -> None:
        placeholders = [
            "#VERSION#",
            "#PROJECT_NAME#",
            "#MAIN_FILE#",
            "#INCLUDE_FILES#",
            "#PACKAGES#",
        ]
        template = " ".join(placeholders)
        result = TemplateProcessor.process_setup_template(
            template,
            {
                "version": "1.0.0",
                "project_name": "App",
                "main_file": "main.py",
                "include_files": {"files": [], "folders": []},
                "packages": [],
            },
        )
        for p in placeholders:
            assert p not in result

    def test_should_format_include_files_as_python_dict_in_setup_template(
        self,
    ) -> None:
        result = TemplateProcessor.process_setup_template(
            "#INCLUDE_FILES#",
            {"include_files": {"files": ["a.txt"], "folders": ["assets"]}},
        )
        assert "files" in result
        assert "folders" in result

    def test_should_write_template_to_file_when_output_path_is_valid(
        self, temp_dir: Path
    ) -> None:
        out = temp_dir / "out.txt"
        TemplateProcessor.create_config_file("content here", {}, out)
        assert out.read_text(encoding="utf-8") == "content here"

    def test_should_raise_template_file_write_error_when_path_is_invalid(
        self, temp_dir: Path
    ) -> None:
        bad_path = temp_dir / "no_such_dir" / "out.txt"
        with pytest.raises(TemplateFileWriteError):
            TemplateProcessor.create_config_file("x", {}, bad_path)

    def test_should_return_true_when_template_is_balanced(self) -> None:
        assert TemplateProcessor.validate_template('{"key": "value"}') is True

    def test_should_raise_template_validation_error_when_braces_unbalanced(
        self,
    ) -> None:
        with pytest.raises(TemplateValidationError):
            TemplateProcessor.validate_template("{unclosed")

    def test_should_raise_template_validation_error_when_quotes_unbalanced(
        self,
    ) -> None:
        with pytest.raises(TemplateValidationError):
            TemplateProcessor.validate_template('"unclosed')


# ///////////////////////////////////////////////////////////////
# TESTS - VALUE VALIDATORS
# ///////////////////////////////////////////////////////////////


class TestValueValidators:
    """Test value_validators module functions."""

    # --- validate_string_length ---

    def test_should_return_true_when_length_is_within_bounds(self) -> None:
        assert validate_string_length("hello", min_length=3, max_length=10) is True

    def test_should_return_false_when_length_is_below_minimum(self) -> None:
        assert validate_string_length("hi", min_length=3) is False

    def test_should_return_false_when_length_exceeds_maximum(self) -> None:
        assert validate_string_length("toolong", max_length=5) is False

    def test_should_return_false_when_value_is_not_a_string(self) -> None:
        assert validate_string_length(42, min_length=0) is False  # type: ignore[arg-type]

    def test_should_return_true_when_no_bounds_are_specified(self) -> None:
        assert validate_string_length("anything") is True

    # --- validate_numeric_range ---

    @pytest.mark.parametrize("value", [0, 5, 10])
    def test_should_return_true_when_numeric_value_is_within_range(
        self, value: int
    ) -> None:
        assert validate_numeric_range(value, min_value=0, max_value=10) is True

    def test_should_return_false_when_value_is_below_minimum(self) -> None:
        assert validate_numeric_range(-1, min_value=0) is False

    def test_should_return_false_when_value_exceeds_maximum(self) -> None:
        assert validate_numeric_range(11, max_value=10) is False

    def test_should_return_false_when_value_is_not_numeric(self) -> None:
        assert validate_numeric_range("five", min_value=0) is False  # type: ignore[arg-type]

    # --- validate_list_length ---

    def test_should_return_true_when_list_has_valid_length(self) -> None:
        assert validate_list_length([1, 2, 3], min_length=2, max_length=5) is True

    def test_should_return_false_when_list_is_too_short(self) -> None:
        assert validate_list_length([1], min_length=2) is False

    def test_should_return_false_when_list_is_too_long(self) -> None:
        assert validate_list_length([1, 2, 3, 4], max_length=3) is False

    def test_should_return_false_when_value_is_not_a_list(self) -> None:
        assert validate_list_length("not a list", min_length=0) is False  # type: ignore[arg-type]

    # --- validate_choice ---

    def test_should_return_true_when_value_is_in_choices(self) -> None:
        assert validate_choice("red", ["red", "green", "blue"]) is True

    def test_should_return_false_when_value_is_not_in_choices(self) -> None:
        assert validate_choice("yellow", ["red", "green", "blue"]) is False

    # --- validate_not_empty ---

    def test_should_not_raise_when_value_is_non_empty_string(self) -> None:
        validate_not_empty("hello")  # must not raise

    def test_should_raise_required_field_error_when_value_is_empty_string(
        self,
    ) -> None:
        with pytest.raises(RequiredFieldError):
            validate_not_empty("")

    def test_should_raise_required_field_error_when_value_is_empty_list(self) -> None:
        with pytest.raises(RequiredFieldError):
            validate_not_empty([])

    def test_should_include_field_name_in_error_message(self) -> None:
        with pytest.raises(RequiredFieldError, match="MyField"):
            validate_not_empty("", field_name="MyField")

    # --- validate_one_of ---

    def test_should_not_raise_when_value_is_valid_choice(self) -> None:
        validate_one_of("disk", ["disk", "server"])  # must not raise

    def test_should_raise_choice_validation_error_when_value_is_invalid(self) -> None:
        with pytest.raises(ChoiceValidationError):
            validate_one_of("ftp", ["disk", "server"])

    def test_should_include_valid_values_in_error_message(self) -> None:
        with pytest.raises(ChoiceValidationError, match="disk"):
            validate_one_of("ftp", ["disk", "server"])

    # --- validate_value_in_range ---

    def test_should_not_raise_when_value_is_within_range(self) -> None:
        validate_value_in_range(5, min_value=0, max_value=10)  # must not raise

    def test_should_raise_range_validation_error_when_below_minimum(self) -> None:
        with pytest.raises(RangeValidationError):
            validate_value_in_range(-1, min_value=0)

    def test_should_raise_range_validation_error_when_above_maximum(self) -> None:
        with pytest.raises(RangeValidationError):
            validate_value_in_range(11, max_value=10)

    # --- validate_length ---

    def test_should_not_raise_when_string_length_is_valid(self) -> None:
        validate_length("hello", min_length=3, max_length=10)  # must not raise

    def test_should_not_raise_when_list_length_is_valid(self) -> None:
        validate_length([1, 2], min_length=1, max_length=5)  # must not raise

    def test_should_raise_length_validation_error_when_string_too_short(self) -> None:
        with pytest.raises(LengthValidationError):
            validate_length("hi", min_length=5)

    def test_should_raise_length_validation_error_when_string_too_long(self) -> None:
        with pytest.raises(LengthValidationError):
            validate_length("toolong", max_length=3)

    def test_should_raise_type_error_when_value_is_not_string_or_list(self) -> None:
        with pytest.raises(TypeError):
            validate_length(42, min_length=0)  # type: ignore[arg-type]


# ///////////////////////////////////////////////////////////////
# TESTS - SCHEMA VALIDATORS
# ///////////////////////////////////////////////////////////////


class TestSchemaValidators:
    """Test schema_validators module functions."""

    # --- validate_required_fields ---

    def test_should_not_raise_when_all_required_fields_are_present(self) -> None:
        validate_required_fields({"a": 1, "b": 2}, ["a", "b"])

    def test_should_raise_required_field_error_when_field_is_missing(self) -> None:
        with pytest.raises(RequiredFieldError):
            validate_required_fields({"a": 1}, ["a", "b"])

    def test_should_raise_required_field_error_when_field_value_is_none(self) -> None:
        with pytest.raises(RequiredFieldError):
            validate_required_fields({"a": None}, ["a"])

    def test_should_raise_type_error_when_data_is_not_a_dict(self) -> None:
        with pytest.raises(TypeError):
            validate_required_fields("not a dict", ["a"])  # type: ignore[arg-type]

    def test_should_report_all_missing_fields_in_single_error(self) -> None:
        with pytest.raises(RequiredFieldError, match="b") as exc_info:
            validate_required_fields({"a": 1}, ["a", "b", "c"])
        assert "c" in str(exc_info.value)

    # --- validate_field_types ---

    def test_should_not_raise_when_all_field_types_are_correct(self) -> None:
        validate_field_types({"name": "test", "age": 25}, {"name": str, "age": int})

    def test_should_raise_type_validation_error_when_field_has_wrong_type(
        self,
    ) -> None:
        with pytest.raises(TypeValidationError):
            validate_field_types({"age": "25"}, {"age": int})

    def test_should_raise_type_error_when_data_is_not_dict_for_field_types(
        self,
    ) -> None:
        with pytest.raises(TypeError):
            validate_field_types("not a dict", {"a": str})  # type: ignore[arg-type]

    def test_should_skip_none_fields_when_field_is_optional(self) -> None:
        validate_field_types({"age": None}, {"age": int})  # must not raise

    # --- validate_config_dict ---

    def test_should_not_raise_when_config_is_minimally_valid(self) -> None:
        validate_config_dict(
            {
                "version": "1.0.0",
                "project_name": "MyApp",
                "main_file": "main.py",
            }
        )

    def test_should_raise_schema_validation_error_when_config_is_not_dict(
        self,
    ) -> None:
        with pytest.raises(SchemaValidationError):
            validate_config_dict("not a dict")  # type: ignore[arg-type]

    def test_should_raise_required_field_error_when_project_name_is_missing(
        self,
    ) -> None:
        with pytest.raises(RequiredFieldError):
            validate_config_dict({"version": "1.0.0", "main_file": "main.py"})

    def test_should_raise_format_validation_error_when_version_format_is_invalid(
        self,
    ) -> None:
        from ezcompiler.shared.exceptions.utils.validation_exceptions import (
            FormatValidationError,
        )

        with pytest.raises(FormatValidationError):
            validate_config_dict(
                {
                    "version": "not-a-version",
                    "project_name": "App",
                    "main_file": "main.py",
                }
            )

    def test_should_raise_length_validation_error_when_project_name_is_empty(
        self,
    ) -> None:
        with pytest.raises(LengthValidationError):
            validate_config_dict(
                {
                    "version": "1.0.0",
                    "project_name": "",
                    "main_file": "main.py",
                }
            )

    # --- validate_dict_schema ---

    def test_should_not_raise_when_required_field_is_present(self) -> None:
        validate_dict_schema(
            {"name": "test"},
            {"name": {"type": str, "required": True}},
        )

    def test_should_raise_schema_validation_error_when_required_field_is_missing(
        self,
    ) -> None:
        with pytest.raises(SchemaValidationError):
            validate_dict_schema(
                {},
                {"name": {"type": str, "required": True}},
            )

    def test_should_raise_schema_validation_error_when_data_is_not_dict(self) -> None:
        with pytest.raises(SchemaValidationError):
            validate_dict_schema("not a dict", {})  # type: ignore[arg-type]

    def test_should_validate_choice_constraint_when_choices_are_specified(
        self,
    ) -> None:
        with pytest.raises(ChoiceValidationError):
            validate_dict_schema(
                {"color": "yellow"},
                {"color": {"choices": ["red", "green", "blue"]}},
            )

    def test_should_validate_min_length_when_string_is_too_short(self) -> None:
        with pytest.raises(LengthValidationError):
            validate_dict_schema(
                {"name": "ab"},
                {"name": {"type": str, "min_length": 5}},
            )

    def test_should_validate_max_length_when_string_is_too_long(self) -> None:
        with pytest.raises(LengthValidationError):
            validate_dict_schema(
                {"name": "toolongname"},
                {"name": {"type": str, "max_length": 5}},
            )

    def test_should_validate_min_value_when_integer_is_too_low(self) -> None:
        with pytest.raises(RangeValidationError):
            validate_dict_schema(
                {"port": 0},
                {"port": {"type": int, "min_value": 1}},
            )

    def test_should_validate_max_value_when_integer_is_too_high(self) -> None:
        with pytest.raises(RangeValidationError):
            validate_dict_schema(
                {"port": 99999},
                {"port": {"type": int, "max_value": 65535}},
            )

    def test_should_validate_pattern_when_string_does_not_match_regex(self) -> None:
        from ezcompiler.shared.exceptions.utils.validation_exceptions import (
            PatternValidationError,
        )

        with pytest.raises(PatternValidationError):
            validate_dict_schema(
                {"version": "abc"},
                {"version": {"type": str, "pattern": r"^\d+\.\d+\.\d+$"}},
            )

    def test_should_skip_validation_when_optional_field_is_none(self) -> None:
        validate_dict_schema(
            {"name": None},
            {"name": {"type": str, "required": False}},
        )  # must not raise

    def test_should_validate_empty_constraint_when_empty_is_false(self) -> None:
        with pytest.raises(RequiredFieldError):
            validate_dict_schema(
                {"name": ""},
                {"name": {"type": str, "empty": False}},
            )
