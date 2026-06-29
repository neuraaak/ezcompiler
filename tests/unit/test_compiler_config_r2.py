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


def test_r2_repo_endpoint_accepted(main_file: Path) -> None:
    cfg = _base(main_file, repo_destination="r2", repo_endpoint="my-bucket/tuf")
    assert cfg.repo_destination == "r2"
    assert cfg.repo_endpoint == "my-bucket/tuf"


def test_r2_repo_endpoint_roundtrips(main_file: Path) -> None:
    cfg = _base(main_file, repo_destination="r2", repo_endpoint="my-bucket/tuf")
    restored = CompilerConfig.from_dict(cfg.to_dict())
    assert restored.repo_destination == "r2"
    assert restored.repo_endpoint == "my-bucket/tuf"


def test_r2_resolved_repo_destination_returns_endpoint(main_file: Path) -> None:
    cfg = _base(main_file, repo_destination="r2", repo_endpoint="my-bucket/tuf")
    assert cfg.resolved_repo_destination == "my-bucket/tuf"
