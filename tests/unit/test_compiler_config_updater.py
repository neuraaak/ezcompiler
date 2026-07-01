from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.shared import CompilerConfig
from ezcompiler.shared.exceptions import ConfigurationError


@pytest.fixture()
def main_file(tmp_path: Path) -> Path:
    f = tmp_path / "main.py"
    f.write_text("# main", encoding="utf-8")
    return f


def _base(main_file: Path, **extra: object) -> CompilerConfig:
    return CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=main_file.parent / "dist",
        **extra,
    )


def test_repo_public_url_defaults_to_empty(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.repo_public_url == ""


def test_repo_public_url_accepted(main_file: Path) -> None:
    cfg = _base(main_file, repo_public_url="https://updates.myapp.com")
    assert cfg.repo_public_url == "https://updates.myapp.com"


def test_repo_public_url_roundtrips(main_file: Path) -> None:
    cfg = _base(main_file, repo_public_url="https://updates.myapp.com")
    restored = CompilerConfig.from_dict(cfg.to_dict())
    assert restored.repo_public_url == "https://updates.myapp.com"


def test_repo_public_url_in_upload_section_of_to_dict(main_file: Path) -> None:
    cfg = _base(main_file, repo_public_url="https://updates.myapp.com")
    d = cfg.to_dict()
    assert d["upload"]["repo_public_url"] == "https://updates.myapp.com"


def test_tuf_enabled_server_no_public_url_raises(main_file: Path) -> None:
    with pytest.raises(ConfigurationError, match="repo_public_url"):
        _base(
            main_file,
            tuf_enabled=True,
            tuf_repo_dir=main_file.parent / "repo",
            repo_destination="server",
            repo_endpoint="https://internal/upload",
        )


def test_tuf_enabled_r2_no_public_url_raises(main_file: Path) -> None:
    with pytest.raises(ConfigurationError, match="repo_public_url"):
        _base(
            main_file,
            tuf_enabled=True,
            tuf_repo_dir=main_file.parent / "repo",
            repo_destination="r2",
            repo_endpoint="bucket/prefix",
        )


def test_tuf_enabled_disk_no_public_url_ok(main_file: Path) -> None:
    cfg = _base(
        main_file,
        tuf_enabled=True,
        tuf_repo_dir=main_file.parent / "repo",
        repo_destination="disk",
        repo_endpoint=str(main_file.parent / "repo"),
    )
    assert cfg.repo_public_url == ""


def test_tuf_disabled_server_no_public_url_ok(main_file: Path) -> None:
    cfg = _base(
        main_file,
        tuf_enabled=False,
        repo_destination="server",
        repo_endpoint="https://internal/upload",
    )
    assert cfg.repo_public_url == ""
