# ///////////////////////////////////////////////////////////////
# TEST_CLI_GENERATE_ISS - Standalone installer script generation
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from ezcompiler.interfaces.cli_interface import main


def _write_config(tmp_path: Path, installer: str = "") -> None:
    (tmp_path / "main.py").write_text("# main", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ezcompiler]\nversion = "1.0.0"\nproject_name = "MyApp"\n'
        'company_name = "ACME"\nmain_file = "main.py"\noutput_folder = "dist"\n'
        "include_files = { files = [], folders = [] }\n" + installer,
        encoding="utf-8",
    )


def test_should_write_standalone_script_when_output_is_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_config(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["generate", "iss"])

    assert result.exit_code == 0, result.output
    target = tmp_path / "installer" / "MyApp.iss"
    assert target.read_bytes().startswith(b"\xef\xbb\xbf")
    content = target.read_text(encoding="utf-8-sig")
    assert '#define MyAppName "MyApp"' in content
    assert "#ifndef MyAppVersion" in content
    assert '#define MyAppPublisher "ACME"' in content


@pytest.mark.parametrize("option", ["--output", "-o"])
def test_should_write_custom_path_when_output_is_provided(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, option: str
) -> None:
    _write_config(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["generate", "iss", option, "custom/x.iss"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "custom" / "x.iss").is_file()
    assert not (tmp_path / "installer" / "MyApp.iss").exists()


def test_should_preserve_existing_script_when_force_is_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "installer" / "MyApp.iss"
    target.parent.mkdir()
    target.write_text("; hand-edited", encoding="utf-8")

    result = CliRunner().invoke(main, ["generate", "iss"])

    assert result.exit_code == 1, result.output
    assert "--force" in result.output
    assert target.read_text(encoding="utf-8") == "; hand-edited"


@pytest.mark.parametrize("option", ["--force", "-f"])
def test_should_overwrite_existing_script_when_force_is_provided(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, option: str
) -> None:
    _write_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "installer" / "MyApp.iss"
    target.parent.mkdir()
    target.write_text("; hand-edited", encoding="utf-8")

    result = CliRunner().invoke(main, ["generate", "iss", option])

    assert result.exit_code == 0, result.output
    assert "[Setup]" in target.read_text(encoding="utf-8-sig")
    assert "; hand-edited" not in target.read_text(encoding="utf-8-sig")


def test_should_print_adoption_line_and_warning_when_script_is_generated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_config(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["generate", "iss"])

    assert result.exit_code == 0, result.output
    assert "[tool.ezcompiler.installer]" in result.output
    assert 'iss_path = "installer/MyApp.iss"' in result.output
    assert "ignored" in result.output.lower()


def test_should_report_configuration_error_when_installer_options_are_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_config(tmp_path, '\n[tool.ezcompiler.installer]\narchitecture = "bad"\n')
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["generate", "iss"])

    assert result.exit_code == 1, result.output
    assert "architecture" in result.output
    assert isinstance(result.exception, SystemExit)
    assert not (tmp_path / "installer").exists()


def test_should_report_config_error_when_project_configuration_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["generate", "iss"])

    assert result.exit_code == 1, result.output
    assert isinstance(result.exception, SystemExit)
    assert result.output.strip()
    assert not (tmp_path / "installer").exists()
