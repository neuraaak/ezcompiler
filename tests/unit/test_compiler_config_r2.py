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
        project_name="App",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=main_file.parent / "dist",
        **extra,
    )


def test_r2_config_fields_default_empty(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.r2_bucket == ""
    assert cfg.r2_remote_prefix == ""


def test_r2_config_fields_settable(main_file: Path) -> None:
    cfg = _base(
        main_file,
        upload_structure="r2",
        r2_bucket="updates",
        r2_remote_prefix="myapp",
    )
    assert cfg.upload_structure == "r2"
    assert cfg.r2_bucket == "updates"
    assert cfg.r2_remote_prefix == "myapp"


def test_r2_config_roundtrips_through_dict(main_file: Path) -> None:
    cfg = _base(main_file, r2_bucket="updates", r2_remote_prefix="myapp")
    restored = CompilerConfig.from_dict(cfg.to_dict())
    assert restored.r2_bucket == "updates"
    assert restored.r2_remote_prefix == "myapp"
