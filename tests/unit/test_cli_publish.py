from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.cli_interface import main
from ezcompiler.shared.exceptions import PublishAuthError, PublishError, ReleaseError

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


def _sign_tree(tmp_path: Path, version: str) -> None:
    """Simule un arbre TUF signe contenant l'archive App-<version>."""
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    doc = {"signed": {"targets": {f"App-{version}.tar.gz": {}}}}
    (meta / "targets.json").write_text(json.dumps(doc), encoding="utf-8")


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


# ------------------------------------------------
# publish update
# ------------------------------------------------


def test_update_should_abort_without_uploading_when_declined(tmp_path):
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3")
    _sign_tree(tmp_path, "1.2.3")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_update"
        ) as pub,
    ):
        result = CliRunner().invoke(main, ["publish", "update"], input="n\n")
    assert result.exit_code == 1
    pub.assert_not_called()


def test_update_should_upload_when_confirmed(tmp_path):
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3")
    _sign_tree(tmp_path, "1.2.3")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_update"
        ) as pub,
    ):
        result = CliRunner().invoke(main, ["publish", "update", "--yes"])
    assert result.exit_code == 0
    pub.assert_called_once()


def test_update_should_name_the_version_in_the_recap(tmp_path):
    """Sans la version, l'operateur confirme a l'aveugle."""
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3")
    _sign_tree(tmp_path, "1.2.3")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch("ezcompiler.interfaces.cli_interface.PublishService.publish_update"),
    ):
        result = CliRunner().invoke(main, ["publish", "update"], input="n\n")
    assert "1.2.3" in result.output


def test_update_should_refuse_a_missing_tuf_tree(tmp_path):
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_update"
        ) as pub,
    ):
        result = CliRunner().invoke(main, ["publish", "update", "--yes"])
    assert result.exit_code == 1
    pub.assert_not_called()
    assert "pipeline" in result.output.lower()


# ------------------------------------------------
# Garde-fous (revue tasks 8-10)
# ------------------------------------------------


def test_should_report_a_missing_login_before_the_recap(tmp_path, staged):
    """Spec 6.1 etape 3 : l'auth est verifiee avant exists() et le recap."""
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.preflight.side_effect = PublishAuthError(
        "'gh' n'est pas authentifié. Lancer `gh auth login`."
    )
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release", "--yes"])
    assert result.exit_code == 1
    assert "auth login" in result.output
    publisher.exists.assert_not_called()
    publisher.publish.assert_not_called()


def test_should_stop_when_existence_cannot_be_determined(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.side_effect = PublishError("Impossible de déterminer")
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release", "--yes"])
    assert result.exit_code == 1
    publisher.publish.assert_not_called()


def test_should_stop_when_artifacts_are_missing(tmp_path):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.resolve_publisher",
            return_value=publisher,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PipelineService.stage_versioned_assets",
            side_effect=ReleaseError("Installeur introuvable"),
        ),
    ):
        result = CliRunner().invoke(main, ["publish", "release", "--yes"])
    assert result.exit_code == 1
    publisher.publish.assert_not_called()


def test_should_reject_destination_on_a_platform(tmp_path, staged):
    """-d n'a pas de sens pour gh : refuser plutot que l'ignorer en silence."""
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(
            main, ["publish", "release", "--yes", "-d", "autre/depot"]
        )
    assert result.exit_code != 0
    publisher.publish.assert_not_called()


def test_should_forward_tag_title_and_draft(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.publish.return_value = "u"
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        CliRunner().invoke(
            main,
            ["publish", "release", "--yes", "--tag", "r1", "--title", "T", "--draft"],
        )
    kwargs = publisher.publish.call_args.kwargs
    assert (kwargs["tag"], kwargs["title"], kwargs["draft"]) == ("r1", "T", True)
    publisher.exists.assert_called_once_with("r1")


def test_should_name_the_repository_even_when_inferred(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    publisher = MagicMock()
    publisher.exists.return_value = False
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(main, ["publish", "release"], input="n\n")
    assert "remote git" in result.output


def test_should_reject_a_non_utf8_notes_file(tmp_path, staged):
    cfg = _make_config(tmp_path, release_destination="github", version="1.2.3")
    notes = tmp_path / "n.md"
    notes.write_bytes("Notes".encode("utf-16"))
    publisher = MagicMock()
    p1, p2, p3 = _patches(cfg, staged, publisher)
    with p1, p2, p3:
        result = CliRunner().invoke(
            main, ["publish", "release", "--yes", "--notes-file", str(notes)]
        )
    assert result.exit_code == 2
    assert "UTF-8" in result.output
    publisher.publish.assert_not_called()


def test_should_warn_about_platform_flags_on_a_file_destination(tmp_path, staged):
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
        ),
    ):
        result = CliRunner().invoke(main, ["publish", "release", "--draft"])
    assert result.exit_code == 0
    assert "--draft" in result.output


def test_update_should_name_the_tree_version_not_the_config(tmp_path):
    """Config bumpee sans rebuild : le recap annonce ce que l'arbre porte."""
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.3.0")
    _sign_tree(tmp_path, "1.2.9")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch("ezcompiler.interfaces.cli_interface.PublishService.publish_update"),
    ):
        result = CliRunner().invoke(main, ["publish", "update"], input="n\n")
    assert "1.2.9" in result.output
    assert "1.3.0" in result.output  # avertissement de divergence


def test_update_should_refuse_metadata_without_signed_targets(tmp_path):
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3")
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    (meta / "root.json").write_text("{}", encoding="utf-8")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_update"
        ) as pub,
    ):
        result = CliRunner().invoke(main, ["publish", "update", "--yes"])
    assert result.exit_code == 1
    pub.assert_not_called()


def test_update_should_forward_its_overrides(tmp_path):
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3")
    _sign_tree(tmp_path, "1.2.3")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_update"
        ) as pub,
    ):
        CliRunner().invoke(
            main,
            ["publish", "update", "--yes", "-rd", "server", "-d", "https://h/x"],
        )
    assert pub.call_args.kwargs == {
        "destination": "https://h/x",
        "repo_destination": "server",
    }


def test_update_should_not_warn_for_a_prerelease_spelling(tmp_path):
    """1.2.3-rc.1 en config et dans l'arbre : aucune fausse alerte."""
    cfg = _make_config(tmp_path, repo_destination="disk", version="1.2.3-rc.1")
    _sign_tree(tmp_path, "1.2.3-rc.1")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch("ezcompiler.interfaces.cli_interface.PublishService.publish_update"),
    ):
        result = CliRunner().invoke(main, ["publish", "update"], input="n\n")
    assert "1.2.3-rc.1" in result.output
    assert "configuration annonce" not in result.output


def test_should_ignore_a_bad_notes_file_on_a_file_destination(tmp_path, staged):
    cfg = _make_config(
        tmp_path, release_destination="disk", release_endpoint=str(tmp_path / "out")
    )
    notes = tmp_path / "n.md"
    notes.write_bytes("Notes".encode("utf-16"))
    p1, p2, p3 = _patches(cfg, staged, None)
    with (
        p1,
        p2,
        p3,
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_release",
            return_value=None,
        ),
    ):
        result = CliRunner().invoke(
            main, ["publish", "release", "--notes-file", str(notes)]
        )
    assert result.exit_code == 0
    assert "--notes-file" in result.output


def test_update_should_warn_that_destination_is_ignored_with_r2(tmp_path):
    cfg = _make_config(
        tmp_path, repo_destination="r2", repo_endpoint="bkt/pre", version="1.2.3"
    )
    _sign_tree(tmp_path, "1.2.3")
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch("ezcompiler.interfaces.cli_interface.PublishService.publish_update"),
    ):
        result = CliRunner().invoke(
            main, ["publish", "update", "-d", "ailleurs"], input="n\n"
        )
    assert "ignoré avec r2" in result.output


# ------------------------------------------------
# publish update après un retrait
# ------------------------------------------------


def _withdraw(tmp_path: Path, version: str) -> None:
    from ezcompiler.services.tuf_service import TufService

    (tmp_path / "repo").mkdir(parents=True, exist_ok=True)
    TufService.record_withdrawn(tmp_path / "repo", version)


def _invoke_update(cfg: CompilerConfig):
    with (
        patch(
            "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
            return_value=cfg,
        ),
        patch(
            "ezcompiler.interfaces.cli_interface.PublishService.publish_update"
        ) as publish,
    ):
        result = CliRunner().invoke(main, ["publish", "update", "--yes"])
    return result, publish


def test_update_should_explain_a_withdrawal_instead_of_a_mismatch(tmp_path):
    cfg = _make_config(
        tmp_path, version="1.0.1", tuf_enabled=True, repo_public_url="https://h/u/"
    )
    _sign_tree(tmp_path, "1.0.0")
    _withdraw(tmp_path, "1.0.1")

    result, publish = _invoke_update(cfg)

    out = " ".join(result.output.split())
    assert result.exit_code == 0, result.output
    assert "1.0.1 a été retirée" in out
    assert "n'atteigne plus de nouveaux clients" in out
    assert "Relancer le pipeline" not in out
    assert "déjà en 1.0.1 y restent" in out
    publish.assert_called_once()


def test_update_should_publish_an_emptied_tree_after_withdrawal(tmp_path):
    cfg = _make_config(
        tmp_path, version="1.0.0", tuf_enabled=True, repo_public_url="https://h/u/"
    )
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "targets.json").write_text('{"signed": {"targets": {}}}', encoding="utf-8")
    _withdraw(tmp_path, "1.0.0")

    result, publish = _invoke_update(cfg)

    out = " ".join(result.output.split())
    assert result.exit_code == 0, result.output
    assert "aucune (toutes retirées)" in out
    publish.assert_called_once()


def test_update_should_still_refuse_an_empty_tree_without_withdrawal(tmp_path):
    cfg = _make_config(
        tmp_path, version="1.0.0", tuf_enabled=True, repo_public_url="https://h/u/"
    )
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "targets.json").write_text('{"signed": {"targets": {}}}', encoding="utf-8")

    result, publish = _invoke_update(cfg)

    assert result.exit_code == 1
    assert "ne référence aucune archive" in " ".join(result.output.split())
    publish.assert_not_called()


def test_update_should_say_no_version_is_offered_when_the_tree_is_emptied(tmp_path):
    cfg = _make_config(
        tmp_path, version="1.0.1", tuf_enabled=True, repo_public_url="https://h/u/"
    )
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "targets.json").write_text('{"signed": {"targets": {}}}', encoding="utf-8")
    _withdraw(tmp_path, "1.0.0")

    result, publish = _invoke_update(cfg)

    out = " ".join(result.output.split())
    assert result.exit_code == 0, result.output
    assert "ne propose plus aucune version" in out
    assert "passeront en" not in out
    publish.assert_called_once()
