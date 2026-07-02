from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ezcompiler.interfaces.cli_interface import main


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
            str(main_file),
            "--installer-enabled",
            "--output",
            str(tmp_path),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "ezcompiler.json").exists()
