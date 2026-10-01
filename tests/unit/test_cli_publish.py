from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.cli_interface import main

pytestmark = pytest.mark.cli


def _make_config(tmp_path: Path, **kwargs: Any) -> CompilerConfig:
    """Meme construction que _cfg dans test_python_api_upload.py."""
    main_file = tmp_path / "main.py"
    if not main_file.exists():
        main_file.write_text("# main", encoding="utf-8")
    kwargs.setdefault("version", "1.0.0")
    return CompilerConfig(
        project_name="App",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
        **kwargs,
    )


@pytest.fixture
def staged(tmp_path: Path) -> list[Path]:
    asset = tmp_path / "App-1.2.3.zip"
    asset.write_bytes(b"x" * 2048)
    return [asset]


def _patches(cfg, staged, publisher):
    """Neutralise config, artefacts et plateforme."""
    return (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PipelineService.stage_versioned_assets",
            return_value=staged,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.resolve_publisher",
            return_value=publisher,
        ),
    )


def test_should_abort_without_publishing_when_the_user_declines(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release"], input="n\n")
    assert result.exit_code == 1
    publisher.publish.assert_not_called()


def test_should_publish_when_the_user_confirms(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.publish.return_value = "https://github.com/o/r/releases/tag/v1.2.3"
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release"], input="y\n")
    assert result.exit_code == 0
    publisher.publish.assert_called_once()


def test_should_skip_the_prompt_with_yes(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.publish.return_value = "u"
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release", "--yes"])
    assert result.exit_code == 0
    publisher.publish.assert_called_once()


def test_should_refuse_an_existing_tag_before_prompting(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = True
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release"])
    assert result.exit_code == 1
    publisher.publish.assert_not_called()
    assert "existe" in result.output.lower()


def test_should_show_the_recap_with_tag_title_and_sizes(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release"], input="n\n")
    assert "v1.2.3" in result.output
    assert "App-1.2.3.zip" in result.output
    assert "Ko" in result.output or "ko" in result.output


def test_should_derive_prerelease_from_the_version(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3rc1")
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.publish.return_value = "u"
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        CliRunner().invoke(main, ["publish", "release", "--yes"])
    assert publisher.publish.call_args.kwargs["prerelease"] is True


def test_should_let_no_prerelease_override_the_derivation(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3rc1")
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.publish.return_value = "u"
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        CliRunner().invoke(main, ["publish", "release", "--yes", "--no-prerelease"])
    assert publisher.publish.call_args.kwargs["prerelease"] is False


def test_should_reject_notes_and_notes_file_together(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    notes = tmp_path / "n.md"
    notes.write_text("hello", encoding="utf-8")
    publisher = MagicMock()
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(
            main,
            ["publish", "release", "--yes", "--notes", "a", "--notes-file", str(notes)],
        )
    assert result.exit_code != 0
    publisher.publish.assert_not_called()


def test_should_read_notes_from_a_file(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    notes = tmp_path / "n.md"
    notes.write_text("Corrections diverses", encoding="utf-8")
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.publish.return_value = "u"
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        CliRunner().invoke(
            main, ["publish", "release", "--yes", "--notes-file", str(notes)]
        )
    assert publisher.publish.call_args.kwargs["notes"] == "Corrections diverses"


def test_should_fail_on_a_missing_notes_file_before_prompting(tmp_path, staged):
    """Review Focus #3 : echouer avant le recap, pas pendant l'appel a gh."""
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(
            main,
            ["publish", "release", "--notes-file", str(tmp_path / "absent.md")],
        )
    assert result.exit_code != 0
    publisher.publish.assert_not_called()


def test_should_not_prompt_on_a_file_destination(tmp_path, staged):
    """disk/server/r2 : chemin actuel, sans confirmation."""
    cfg = _make_config(
        tmp_path, release_destination="disk", release_endpoint=str(tmp_path / "out")
    )
    p1, p2, p3 = _patches(cfg, staged, None)
    with (
        p1,
        p2,
        p3,
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_release",
            return_value=None,
        ) as pub,
    ):
        result = CliRunner().invoke(main, ["publish", "release"])
    assert result.exit_code == 0
    pub.assert_called_once()
