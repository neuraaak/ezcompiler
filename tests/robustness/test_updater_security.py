from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.services.updater_service import UpdaterService
from ezcompiler.shared import CompilerConfig


@pytest.fixture()
def tuf_repo(tmp_path: Path) -> Path:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    original = '{"signed": {"_type": "root", "version": 1}}'
    (meta / "root.json").write_text(original, encoding="utf-8")
    return tmp_path / "repo"


@pytest.fixture()
def cfg(tmp_path: Path, tuf_repo: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tuf_repo,
        repo_destination="disk",
        repo_endpoint=str(tuf_repo),
    )


def test_root_json_source_not_mutated(
    cfg: CompilerConfig, tmp_path: Path, tuf_repo: Path
) -> None:
    source = tuf_repo / "metadata" / "root.json"
    original_content = source.read_text(encoding="utf-8")
    out = tmp_path / "out"
    UpdaterService.generate(cfg, out)
    assert source.read_text(encoding="utf-8") == original_content


def test_root_json_copy_matches_source(
    cfg: CompilerConfig, tmp_path: Path, tuf_repo: Path
) -> None:
    source = tuf_repo / "metadata" / "root.json"
    out = tmp_path / "out"
    UpdaterService.generate(cfg, out)
    assert (out / "root.json").read_bytes() == source.read_bytes()


def test_update_url_not_injected_in_update_py(
    cfg: CompilerConfig, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    UpdaterService.generate(cfg, out)
    update_text = (out / "update.py").read_text(encoding="utf-8")
    assert "file://" not in update_text
    assert "UPDATE_URL" in update_text
