from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from ezcompiler.interfaces.cli_interface import main


def test_updater_generate_command_exists() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["updater", "generate", "--help"])
    assert result.exit_code == 0
    assert "--config" in result.output or "generate" in result.output.lower()


@patch("ezcompiler.interfaces.cli_interface.UpdaterService")
@patch("ezcompiler.interfaces.cli_interface.ConfigService")
def test_updater_generate_calls_service(mock_cs, mock_us, tmp_path: Path) -> None:
    main_file = tmp_path / "main.py"
    main_file.write_text("# main", encoding="utf-8")
    repo = tmp_path / "repo"
    (repo / "metadata").mkdir(parents=True)
    (repo / "metadata" / "root.json").write_text("{}", encoding="utf-8")

    mock_cs.return_value.load_config.return_value = {
        "version": "1.0.0",
        "project_name": "App",
        "main_file": str(main_file),
        "include_files": {"files": [], "folders": []},
        "output_folder": str(tmp_path / "dist"),
        "release": {
            "tuf_enabled": True,
            "tuf_repo_dir": str(repo),
            "tuf_keys_dir": None,
        },
        "upload": {
            "repo_destination": "disk",
            "release_destination": "disk",
            "repo_endpoint": str(repo),
            "release_endpoint": "",
            "repo_public_url": "",
        },
    }
    mock_us.generate.return_value = []

    runner = CliRunner()
    result = runner.invoke(main, ["updater", "generate"])
    assert result.exit_code == 0
    assert mock_us.generate.called
