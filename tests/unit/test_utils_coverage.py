# ///////////////////////////////////////////////////////////////
# TEST UTILS COVERAGE - Focused tests for uncovered util branches
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Coverage-focused tests for utility modules.

Targets previously uncovered branches in CompilerUtils, ConfigUtils,
UploaderUtils, and validator modules (format, meta, string).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from ezcompiler.shared import CompilerConfig
from ezcompiler.shared.exceptions.utils import (
    CompilerConfigValidationError,
    CompilerOptionError,
    ConfigFileNotFoundError,
    ConfigFileParseError,
    ConfigPathError,
    MainFileNotFoundError,
    MissingRequiredConfigError,
    OutputDirectoryError,
    PatternValidationError,
    SchemaValidationError,
    ServerConfigError,
    SourcePathError,
    UploaderTypeError,
)
from ezcompiler.utils import CompilerUtils, ConfigUtils, UploaderUtils
from ezcompiler.utils.validators import (
    sanitize_filename,
    validate_email,
    validate_multiple,
    validate_pattern,
    validate_url,
    validate_version_string,
)

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _make_config(tmp_path: Path, **overrides) -> CompilerConfig:
    """Build a minimal valid CompilerConfig pointing at a real file in tmp_path."""
    main = tmp_path / "main.py"
    main.write_text("print('ok')\n", encoding="utf-8")
    base = {
        "version": "1.0.0",
        "project_name": "TestApp",
        "main_file": str(main),
        "include_files": {"files": [], "folders": []},
        "output_folder": tmp_path / "dist",
    }
    base.update(overrides)
    return CompilerConfig(**base)


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER UTILS
# ///////////////////////////////////////////////////////////////


class TestCompilerUtilsValidate:
    def test_should_raise_when_main_file_is_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.main_file = ""
        with pytest.raises(CompilerConfigValidationError):
            CompilerUtils.validate_compiler_config(config)

    def test_should_raise_when_main_file_does_not_exist(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.main_file = str(tmp_path / "missing.py")
        with pytest.raises(MainFileNotFoundError):
            CompilerUtils.validate_compiler_config(config)

    def test_should_raise_when_output_folder_is_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.output_folder = ""  # type: ignore[assignment]
        with pytest.raises(OutputDirectoryError):
            CompilerUtils.validate_compiler_config(config)

    def test_should_pass_validation_when_config_is_valid(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        CompilerUtils.validate_compiler_config(config)


class TestCompilerUtilsPrepareDirectory:
    def test_should_create_output_directory_when_missing(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path, output_folder=tmp_path / "newdist")
        CompilerUtils.prepare_compiler_output_directory(config)
        assert (tmp_path / "newdist").is_dir()


class TestCompilerUtilsFormatIncludes:
    def test_should_combine_files_and_folders_with_trailing_slash(
        self, tmp_path: Path
    ) -> None:
        config = _make_config(
            tmp_path,
            include_files={"files": ["config.yaml"], "folders": ["lib", "assets"]},
        )
        result = CompilerUtils.format_include_files_data(config)
        assert result == ["config.yaml", "lib/", "assets/"]


class TestCompilerUtilsHelpers:
    def test_should_return_win32gui_when_no_console_on_windows(self) -> None:
        with patch.object(sys, "platform", "win32"):
            assert CompilerUtils.get_windows_base_for_console(False) == "Win32GUI"

    def test_should_return_none_when_console_is_true(self) -> None:
        with patch.object(sys, "platform", "win32"):
            assert CompilerUtils.get_windows_base_for_console(True) is None

    def test_should_return_none_when_not_windows(self) -> None:
        with patch.object(sys, "platform", "linux"):
            assert CompilerUtils.get_windows_base_for_console(False) is None

    def test_should_detect_onefile_in_argv(self) -> None:
        with patch.object(sys, "argv", ["script.py", "--onefile"]):
            assert CompilerUtils.check_onefile_mode() is True

    def test_should_not_detect_onefile_when_absent(self) -> None:
        with patch.object(sys, "argv", ["script.py"]):
            assert CompilerUtils.check_onefile_mode() is False


# ///////////////////////////////////////////////////////////////
# TESTS - CONFIG UTILS
# ///////////////////////////////////////////////////////////////


class TestConfigUtilsRequiredFields:
    def test_should_raise_when_version_is_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.version = ""
        with pytest.raises(MissingRequiredConfigError):
            ConfigUtils.validate_required_config_fields(config)

    def test_should_raise_when_project_name_is_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.project_name = ""
        with pytest.raises(MissingRequiredConfigError):
            ConfigUtils.validate_required_config_fields(config)

    def test_should_raise_when_main_file_is_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.main_file = ""
        with pytest.raises(MissingRequiredConfigError):
            ConfigUtils.validate_required_config_fields(config)

    def test_should_raise_when_include_files_is_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.include_files = {}
        with pytest.raises(MissingRequiredConfigError):
            ConfigUtils.validate_required_config_fields(config)

    def test_should_pass_when_all_required_fields_set(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        ConfigUtils.validate_required_config_fields(config)


class TestConfigUtilsPathValidation:
    def test_should_raise_when_main_file_missing(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.main_file = str(tmp_path / "ghost.py")
        with pytest.raises(ConfigPathError):
            ConfigUtils.validate_config_paths(config)

    def test_should_normalize_output_folder_string(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.output_folder = str(tmp_path / "dist")  # type: ignore[assignment]
        ConfigUtils.validate_config_paths(config)
        assert isinstance(config.output_folder, Path)


class TestConfigUtilsCompilerOption:
    def test_should_raise_when_compiler_invalid(self) -> None:
        with pytest.raises(CompilerOptionError):
            ConfigUtils.validate_compiler_option("Bogus")

    @pytest.mark.parametrize("compiler", ["auto", "Cx_Freeze", "PyInstaller", "Nuitka"])
    def test_should_pass_for_valid_compilers(self, compiler: str) -> None:
        ConfigUtils.validate_compiler_option(compiler)


class TestConfigUtilsNormalize:
    def test_should_convert_string_to_path(self) -> None:
        result = ConfigUtils.normalize_output_folder("dist")
        assert isinstance(result, Path)

    def test_should_pass_through_path(self, tmp_path: Path) -> None:
        result = ConfigUtils.normalize_output_folder(tmp_path)
        assert result is tmp_path


class TestConfigUtilsLoaders:
    def test_should_raise_when_yaml_missing(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigFileNotFoundError):
            ConfigUtils.load_yaml_config(tmp_path / "missing.yaml")

    def test_should_load_yaml_dict(self, tmp_path: Path) -> None:
        path = tmp_path / "c.yaml"
        path.write_text("name: app\nversion: 1.0\n", encoding="utf-8")
        data = ConfigUtils.load_yaml_config(path)
        assert data == {"name": "app", "version": 1.0}

    def test_should_return_empty_dict_when_yaml_not_a_mapping(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "c.yaml"
        path.write_text("- item1\n- item2\n", encoding="utf-8")
        assert ConfigUtils.load_yaml_config(path) == {}

    def test_should_raise_on_invalid_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "c.yaml"
        path.write_text("key: : value\n: nope\n", encoding="utf-8")
        with pytest.raises(ConfigFileParseError):
            ConfigUtils.load_yaml_config(path)

    def test_should_raise_when_json_missing(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigFileNotFoundError):
            ConfigUtils.load_json_config(tmp_path / "missing.json")

    def test_should_load_json_dict(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text('{"name": "app"}', encoding="utf-8")
        assert ConfigUtils.load_json_config(path) == {"name": "app"}

    def test_should_return_empty_dict_when_json_not_a_mapping(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "c.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")
        assert ConfigUtils.load_json_config(path) == {}

    def test_should_raise_on_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(ConfigFileParseError):
            ConfigUtils.load_json_config(path)

    def test_should_raise_when_toml_missing(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigFileNotFoundError):
            ConfigUtils.load_toml_config(tmp_path / "missing.toml")

    def test_should_load_toml(self, tmp_path: Path) -> None:
        path = tmp_path / "c.toml"
        path.write_text('name = "app"\n', encoding="utf-8")
        assert ConfigUtils.load_toml_config(path) == {"name": "app"}

    def test_should_raise_on_invalid_toml(self, tmp_path: Path) -> None:
        path = tmp_path / "c.toml"
        path.write_text("not = = valid\n", encoding="utf-8")
        with pytest.raises(ConfigFileParseError):
            ConfigUtils.load_toml_config(path)


class TestConfigUtilsExtractPyproject:
    def test_should_extract_project_metadata(self) -> None:
        toml = {
            "project": {
                "name": "myapp",
                "version": "2.1.0",
                "description": "demo",
                "authors": [{"name": "Alice"}],
            },
            "tool": {"ezcompiler": {"main_file": "app.py"}},
        }
        out = ConfigUtils.extract_pyproject_config(toml)
        assert out["project_name"] == "myapp"
        assert out["version"] == "2.1.0"
        assert out["project_description"] == "demo"
        assert out["author"] == "Alice"
        assert out["company_name"] == "Alice"
        assert out["main_file"] == "app.py"

    def test_should_return_empty_dict_when_no_relevant_sections(self) -> None:
        assert ConfigUtils.extract_pyproject_config({}) == {}

    def test_should_skip_authors_when_not_dict(self) -> None:
        toml = {"project": {"authors": ["Alice"]}}
        out = ConfigUtils.extract_pyproject_config(toml)
        assert "author" not in out


class TestConfigUtilsDiscovery:
    def test_should_discover_yaml_first(self, tmp_path: Path) -> None:
        (tmp_path / "ezcompiler.yaml").write_text("a: 1\n", encoding="utf-8")
        (tmp_path / "ezcompiler.json").write_text("{}", encoding="utf-8")
        result = ConfigUtils.discover_config_file(tmp_path)
        assert result is not None and result.name == "ezcompiler.yaml"

    def test_should_discover_json_when_no_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "ezcompiler.json").write_text("{}", encoding="utf-8")
        result = ConfigUtils.discover_config_file(tmp_path)
        assert result is not None and result.name == "ezcompiler.json"

    def test_should_discover_pyproject_when_has_ezcompiler_section(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "pyproject.toml").write_text(
            "[tool.ezcompiler]\nmain_file = 'm.py'\n", encoding="utf-8"
        )
        result = ConfigUtils.discover_config_file(tmp_path)
        assert result is not None and result.name == "pyproject.toml"

    def test_should_skip_pyproject_without_ezcompiler_section(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "pyproject.toml").write_text(
            "[project]\nname = 'x'\n", encoding="utf-8"
        )
        assert ConfigUtils.discover_config_file(tmp_path) is None

    def test_should_return_none_when_pyproject_invalid(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("not = = valid\n", encoding="utf-8")
        assert ConfigUtils.discover_config_file(tmp_path) is None

    def test_should_return_none_when_nothing_found(self, tmp_path: Path) -> None:
        assert ConfigUtils.discover_config_file(tmp_path) is None


class TestConfigUtilsMerge:
    def test_should_merge_nested_compilation_section(self) -> None:
        base = {"compilation": {"compiler": "auto", "console": True}}
        override = {"compilation": {"compiler": "PyInstaller"}}
        result = ConfigUtils.merge_config_dicts(base, override)
        assert result["compilation"] == {"compiler": "PyInstaller", "console": True}

    def test_should_replace_non_nested_keys(self) -> None:
        base = {"version": "1.0", "include_files": {"files": ["a"]}}
        override = {"version": "2.0", "include_files": {"files": ["b"]}}
        result = ConfigUtils.merge_config_dicts(base, override)
        assert result == {"version": "2.0", "include_files": {"files": ["b"]}}


# ///////////////////////////////////////////////////////////////
# TESTS - UPLOADER UTILS
# ///////////////////////////////////////////////////////////////


class TestUploaderUtilsValidateSource:
    def test_should_raise_when_source_does_not_exist(self, tmp_path: Path) -> None:
        with pytest.raises(SourcePathError):
            UploaderUtils.validate_source_path(tmp_path / "missing")

    def test_should_pass_when_source_is_file(self, tmp_path: Path) -> None:
        p = tmp_path / "f.txt"
        p.write_text("x", encoding="utf-8")
        UploaderUtils.validate_source_path(p)

    def test_should_pass_when_source_is_dir(self, tmp_path: Path) -> None:
        UploaderUtils.validate_source_path(tmp_path)


class TestUploaderUtilsValidateUploadType:
    @pytest.mark.parametrize("upload_type", ["disk", "server", "DISK", "Server"])
    def test_should_accept_valid_types(self, upload_type: str) -> None:
        UploaderUtils.validate_upload_type(upload_type)

    def test_should_raise_for_invalid_type(self) -> None:
        with pytest.raises(UploaderTypeError):
            UploaderUtils.validate_upload_type("ftp")


class TestUploaderUtilsValidateServerUrl:
    def test_should_raise_when_url_empty(self) -> None:
        with pytest.raises(ServerConfigError):
            UploaderUtils.validate_server_url("")

    def test_should_raise_when_url_lacks_scheme(self) -> None:
        with pytest.raises(ServerConfigError):
            UploaderUtils.validate_server_url("example.com")

    @pytest.mark.parametrize("url", ["http://example.com", "https://example.com/path"])
    def test_should_accept_http_and_https(self, url: str) -> None:
        UploaderUtils.validate_server_url(url)


class TestUploaderUtilsBackupPath:
    def test_should_generate_backup_when_target_does_not_exist(
        self, tmp_path: Path
    ) -> None:
        result = UploaderUtils.generate_backup_path(tmp_path / "f.zip")
        assert result.name == "f.zip.backup"

    def test_should_increment_counter_when_backups_exist(self, tmp_path: Path) -> None:
        original = tmp_path / "f.zip"
        original.write_text("x", encoding="utf-8")
        (tmp_path / "f.zip.backup").write_text("x", encoding="utf-8")
        (tmp_path / "f.zip.backup.1").write_text("x", encoding="utf-8")
        result = UploaderUtils.generate_backup_path(original)
        assert result.name == "f.zip.backup.2"


class TestUploaderUtilsDefaults:
    def test_should_return_default_disk_config(self) -> None:
        cfg = UploaderUtils.get_default_disk_config()
        assert cfg == {
            "preserve_permissions": True,
            "overwrite": True,
            "create_backup": False,
        }

    def test_should_return_default_server_config(self) -> None:
        cfg = UploaderUtils.get_default_server_config()
        assert cfg["server_url"] == ""
        assert cfg["timeout"] == 30
        assert cfg["verify_ssl"] is True
        assert cfg["chunk_size"] == 8192
        assert cfg["retry_attempts"] == 3


# ///////////////////////////////////////////////////////////////
# TESTS - FORMAT VALIDATORS
# ///////////////////////////////////////////////////////////////


class TestFormatValidators:
    def test_version_string_returns_false_for_non_string(self) -> None:
        assert validate_version_string(123) is False  # type: ignore[arg-type]

    @pytest.mark.parametrize("v", ["1.0.0", "1.0", "1.2.3.4"])
    def test_version_string_accepts_valid_formats(self, v: str) -> None:
        assert validate_version_string(v) is True

    def test_version_string_rejects_invalid(self) -> None:
        assert validate_version_string("not-a-version") is False

    def test_email_returns_false_for_non_string(self) -> None:
        assert validate_email(None) is False  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "email,expected",
        [
            ("user@example.com", True),
            ("a.b+c@sub.domain.io", True),
            ("invalid-email", False),
            ("missing@tld", False),
        ],
    )
    def test_email_validation(self, email: str, expected: bool) -> None:
        assert validate_email(email) is expected

    def test_url_returns_false_for_non_string(self) -> None:
        assert validate_url(42) is False  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://example.com", True),
            ("http://example.com/path?q=1", True),
            ("ftp://example.com", False),
            ("not a url", False),
        ],
    )
    def test_url_validation(self, url: str, expected: bool) -> None:
        assert validate_url(url) is expected


# ///////////////////////////////////////////////////////////////
# TESTS - META VALIDATORS
# ///////////////////////////////////////////////////////////////


class TestMetaValidators:
    def test_should_run_all_validations_successfully(self) -> None:
        validators = {
            "version": validate_version_string,
            "email": validate_email,
        }
        validate_multiple(
            [("1.0.0", "version", "v"), ("a@b.co", "email", "e")], validators
        )

    def test_should_raise_when_validator_unknown(self) -> None:
        with pytest.raises(SchemaValidationError, match="Unknown validator"):
            validate_multiple([("x", "ghost", "field")], {})

    def test_should_raise_when_value_invalid(self) -> None:
        validators = {"version": validate_version_string}
        with pytest.raises(SchemaValidationError, match="Invalid v"):
            validate_multiple([("oops", "version", "v")], validators)


# ///////////////////////////////////////////////////////////////
# TESTS - STRING VALIDATORS
# ///////////////////////////////////////////////////////////////


class TestStringValidators:
    def test_sanitize_returns_empty_for_non_string(self) -> None:
        assert sanitize_filename(123) == ""  # type: ignore[arg-type]

    def test_sanitize_replaces_invalid_chars(self) -> None:
        assert sanitize_filename("a<b>c.txt") == "a_b_c.txt"

    def test_sanitize_strips_dots_and_spaces(self) -> None:
        assert sanitize_filename("  file.txt  ") == "file.txt"

    def test_sanitize_returns_unnamed_when_empty_after_clean(self) -> None:
        assert sanitize_filename("   ...   ") == "unnamed_file"

    def test_sanitize_preserves_valid_filename(self) -> None:
        assert sanitize_filename("my_file.txt") == "my_file.txt"

    def test_validate_pattern_raises_typeerror_for_non_string(self) -> None:
        with pytest.raises(TypeError):
            validate_pattern(123, r"^\d+$")  # type: ignore[arg-type]

    def test_validate_pattern_raises_when_no_match(self) -> None:
        with pytest.raises(PatternValidationError):
            validate_pattern("abc", r"^\d+$")

    def test_validate_pattern_uses_custom_error_message(self) -> None:
        with pytest.raises(PatternValidationError, match="custom!"):
            validate_pattern("abc", r"^\d+$", error_msg="custom!")

    def test_validate_pattern_passes_on_match(self) -> None:
        validate_pattern("abc123", r"^[a-z]+\d+$")
