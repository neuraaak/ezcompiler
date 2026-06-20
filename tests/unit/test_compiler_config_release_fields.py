from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.shared import CompilerConfig


@pytest.fixture()
def main_file(tmp_path: Path) -> Path:
    f = tmp_path / "main.py"
    f.write_text("# main", encoding="utf-8")
    return f


def _base(main_file: Path, **extra) -> CompilerConfig:
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=main_file.parent / "dist",
        **extra,
    )


def test_release_defaults(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.release_needed is False
    assert cfg.release_type == "tufup"
    assert cfg.tufup_repo_dir is None
    assert cfg.update_repo_url is None


def test_release_fields_settable(main_file: Path) -> None:
    cfg = _base(
        main_file,
        release_needed=True,
        tufup_repo_dir=main_file.parent / "repo",
        tufup_keys_dir=main_file.parent / "keystore",
        update_repo_url="https://updates.example.com",
    )
    assert cfg.release_needed is True
    assert cfg.tufup_repo_dir == main_file.parent / "repo"
    assert cfg.update_repo_url == "https://updates.example.com"


def test_release_fields_in_to_dict(main_file: Path) -> None:
    result = _base(main_file).to_dict()
    assert "release_needed" in result.get("release", result)
