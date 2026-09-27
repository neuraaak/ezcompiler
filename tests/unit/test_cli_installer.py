from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from ezcompiler.interfaces.cli_interface import main
from ezcompiler.services import ConfigService


def test_generate_config_installer_enabled_flag(tmp_path: Path) -> None:
    runner = CliRunner()
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")

    result = runner.invoke(
        main,
        [
            "generate",
            "config",
            "--project-name",
            "MyApp",
            "--version",
            "1.0.0",
            "--main-file",
            main_file.as_posix(),
            "--installer-enabled",
            "--output",
            str(tmp_path),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "ezcompiler.json").exists()
    generated = json.loads((tmp_path / "ezcompiler.json").read_text(encoding="utf-8"))
    assert generated["installer"]["enabled"] is True
    assert ConfigService.build_compiler_config(
        config_path=tmp_path / "ezcompiler.json", search_dir=tmp_path
    ).installer.enabled


@pytest.mark.parametrize("format_type", ["yaml", "json", "pyproject"])
@pytest.mark.parametrize("enabled", [False, True])
def test_should_emit_nested_installer_config_when_generating_configuration(
    tmp_path: Path, format_type: str, enabled: bool
) -> None:
    main_file = tmp_path / "main.py"
    main_file.write_text("# main", encoding="utf-8")
    args = [
        "generate",
        "config",
        "--project-name",
        "MyApp",
        "--main-file",
        main_file.as_posix(),
        "--output",
        str(tmp_path),
        "--format",
        format_type,
    ]
    if enabled:
        args.append("--installer-enabled")

    result = CliRunner().invoke(main, args)

    assert result.exit_code == 0, result.output
    if format_type == "pyproject":
        content = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
        generated = tomllib.loads(content)["tool"]["ezcompiler"]
        assert (
            "[tool.ezcompiler.installer]\n"
            f"enabled = {str(enabled).lower()}\n"
            "# per_user = true                    # installs into %LOCALAPPDATA% (required for tufup auto-update)\n"
            '# iss_path = "installer/MyApp.iss"   # script produced by `ezcompiler generate iss`\n'
            "# Full option set: `ezcompiler generate iss --help` and docs/guides/windows-installer.md\n"
        ) in content
    else:
        content = (tmp_path / f"ezcompiler.{format_type}").read_text(encoding="utf-8")
        generated = (
            json.loads(content) if format_type == "json" else yaml.safe_load(content)
        )
    assert generated["installer"] == {"enabled": enabled}


def test_should_preserve_other_pyproject_tables_when_generating_configuration(
    tmp_path: Path,
) -> None:
    target = tmp_path / "pyproject.toml"
    target.write_text('[project]\nname = "original"\n', encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "generate",
            "config",
            "--project-name",
            "MyApp",
            "--format",
            "pyproject",
            "--output",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (
        tomllib.loads(target.read_text(encoding="utf-8"))["project"]["name"]
        == "original"
    )


def test_should_preserve_windows_paths_when_generating_pyproject(
    tmp_path: Path,
) -> None:
    main_file = tmp_path / "main.py"
    main_file.write_text("# main", encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "generate",
            "config",
            "--project-name",
            "MyApp",
            "--main-file",
            str(main_file),
            "--format",
            "pyproject",
            "--output",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    generated = tomllib.loads((tmp_path / "pyproject.toml").read_text(encoding="utf-8"))
    config = generated["tool"]["ezcompiler"]
    assert config["main_file"] == str(main_file)
    assert config["pyinstaller"] == {"optimize": True, "strip": False}
    assert ConfigService.build_compiler_config(
        pyproject_path=tmp_path / "pyproject.toml", search_dir=tmp_path
    ).main_file == str(main_file)
