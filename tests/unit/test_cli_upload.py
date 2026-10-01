from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.cli_interface import main
from ezcompiler.shared.exceptions import UploadError

_CLI = "ezcompiler.interfaces.cli_interface"


def _cfg(tmp_path: Path, **kwargs: Any) -> CompilerConfig:
    main_file = tmp_path / "main.py"
    main_file.write_text("# m", encoding="utf-8")
    kwargs.setdefault("tuf_enabled", True)
    kwargs.setdefault("repo_public_url", "https://h/update/")
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        **kwargs,
    )


class _Recorder:
    """Enregistre l'ordre des appels aux deux publications."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def update(self, _cfg: CompilerConfig, **kw: Any) -> None:
        self.calls.append(("update", kw))

    def release(self, _cfg: CompilerConfig, assets: list[Path], **kw: Any) -> None:
        self.calls.append(("release", {"assets": assets, **kw}))

    @property
    def names(self) -> list[str]:
        return [name for name, _ in self.calls]


def _invoke(cfg: CompilerConfig, rec: _Recorder, *args: str):
    with (
        patch(f"{_CLI}.ConfigService.build_compiler_config", return_value=cfg),
        patch(f"{_CLI}.PublishService.read_tree_version", return_value="1.0.0"),
        patch(f"{_CLI}.PublishService.publish_update", side_effect=rec.update),
        patch(f"{_CLI}.PublishService.publish_release", side_effect=rec.release),
    ):
        # Aucune entrée fournie : un prompt de confirmation ferait échouer.
        return CliRunner().invoke(main, ["upload", *args])


def test_upload_should_chain_publish_update_then_release_without_prompt(
    tmp_path: Path,
) -> None:
    rec = _Recorder()
    result = _invoke(_cfg(tmp_path), rec)

    assert result.exit_code == 0, result.output
    assert rec.names == ["update", "release"]
    assert "Publier cet arbre ?" not in result.output
    assert "Publier cette release ?" not in result.output


def test_upload_should_forward_overrides_to_both_publications(tmp_path: Path) -> None:
    rec = _Recorder()
    result = _invoke(
        _cfg(tmp_path),
        rec,
        "--repo-destination",
        "server",
        "--release-destination",
        "disk",
        "--destination",
        "https://h/up",
    )

    assert result.exit_code == 0, result.output
    update_kw = rec.calls[0][1]
    release_kw = rec.calls[1][1]
    assert update_kw["repo_destination"] == "server"
    assert update_kw["destination"] == "https://h/up"
    assert release_kw["release_destination"] == "disk"
    assert release_kw["destination"] == "https://h/up"
    assert release_kw["assets"] == []


def test_upload_should_publish_r2_tree_and_disk_release_both(tmp_path: Path) -> None:
    """L'ancienne règle qui sautait la release en r2 + disk disparaît."""
    rec = _Recorder()
    result = _invoke(_cfg(tmp_path), rec, "-rd", "r2", "-rld", "disk")

    assert result.exit_code == 0, result.output
    assert rec.names == ["update", "release"]


def test_upload_should_skip_update_tree_when_tuf_is_disabled(tmp_path: Path) -> None:
    rec = _Recorder()
    cfg = _cfg(tmp_path, tuf_enabled=False, repo_public_url=None)
    result = _invoke(cfg, rec)

    assert result.exit_code == 0, result.output
    assert rec.names == ["release"]


@pytest.mark.parametrize("platform", ["github", "gitlab"])
def test_upload_should_refuse_a_platform_release_destination(
    tmp_path: Path, platform: str
) -> None:
    rec = _Recorder()
    cfg = _cfg(tmp_path, release_destination=platform, release_endpoint="o/r")
    result = _invoke(cfg, rec)

    assert result.exit_code == 1
    assert rec.calls == []
    assert "ezcompiler publish release" in result.output


def test_upload_should_not_publish_release_when_update_fails(tmp_path: Path) -> None:
    rec = _Recorder()

    def boom(*_a: Any, **_kw: Any) -> None:
        raise UploadError("boom")

    rec.update = boom  # type: ignore[method-assign]
    result = _invoke(_cfg(tmp_path), rec)

    assert result.exit_code == 1
    assert rec.names == []


def test_upload_command_should_announce_its_deprecation(tmp_path: Path) -> None:
    result = _invoke(_cfg(tmp_path), _Recorder())
    assert result.exit_code == 0, result.output
    assert "ezcompiler publish" in result.output


def test_upload_command_help_says_deprecated() -> None:
    result = CliRunner().invoke(main, ["upload", "--help"])
    assert "Déprécié" in result.output
