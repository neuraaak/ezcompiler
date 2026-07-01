from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.services.updater_service import UpdaterService
from ezcompiler.shared import CompilerConfig
from ezcompiler.shared.exceptions import UpdaterConfigError


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    (meta / "root.json").write_text('{"signed": {}}', encoding="utf-8")
    return tmp_path / "repo"


@pytest.fixture()
def cfg(tmp_path: Path, tmp_repo: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="1.2.3",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tmp_repo,
        repo_destination="disk",
        repo_endpoint=str(tmp_repo),
    )


def test_generate_disk_writes_files(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater"
    out.mkdir()
    files = UpdaterService.generate(cfg, out)
    names = {f.name for f in files}
    assert names == {"settings.py", "update.py", "root.json"}


def test_generate_disk_url_uses_file_scheme(
    cfg: CompilerConfig, tmp_path: Path
) -> None:
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert "file://" in settings


def test_generate_server_url_uses_public_url(tmp_path: Path, tmp_repo: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tmp_repo,
        repo_destination="server",
        repo_endpoint="https://internal/upload",
        repo_public_url="https://updates.myapp.com",
    )
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert "https://updates.myapp.com" in settings


def test_generate_r2_url_uses_public_url(tmp_path: Path, tmp_repo: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tmp_repo,
        repo_destination="r2",
        repo_endpoint="bucket/prefix",
        repo_public_url="https://pub.r2.myapp.com",
    )
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert "https://pub.r2.myapp.com" in settings


def test_generate_embeds_app_name_and_version(
    cfg: CompilerConfig, tmp_path: Path
) -> None:
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert "MyApp" in settings
    assert "1.2.3" in settings


def test_generate_copies_root_json(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    assert (out / "root.json").read_text(encoding="utf-8") == '{"signed": {}}'


def test_tuf_disabled_raises_config_error(tmp_path: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=False,
    )
    with pytest.raises(UpdaterConfigError, match="tuf_enabled"):
        UpdaterService.generate(cfg, tmp_path / "out")


def test_missing_root_json_raises_config_error(tmp_path: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    repo = tmp_path / "repo"
    repo.mkdir()
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=repo,
        repo_destination="disk",
        repo_endpoint=str(repo),
    )
    with pytest.raises(UpdaterConfigError, match="root.json"):
        UpdaterService.generate(cfg, tmp_path / "out")


def test_disk_url_includes_update_subdir(cfg: CompilerConfig, tmp_path: Path) -> None:
    """Client URL must point at the /update subtree where the TUF repo is
    uploaded (UploaderService._upload_tuf_repo)."""
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert "/update" in settings
    assert 'UPDATE_URL = "file://' in settings
    assert settings.count("/update") >= 1


def test_server_url_includes_update_subdir(tmp_path: Path, tmp_repo: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tmp_repo,
        repo_destination="server",
        repo_endpoint="https://internal/upload",
        repo_public_url="https://updates.myapp.com",
    )
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert "https://updates.myapp.com/update" in settings


def test_r2_url_has_no_update_subdir(tmp_path: Path, tmp_repo: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tmp_repo,
        repo_destination="r2",
        repo_endpoint="bucket/prefix",
        repo_public_url="https://pub.r2.myapp.com",
    )
    out = tmp_path / "updater"
    out.mkdir()
    UpdaterService.generate(cfg, out)
    settings = (out / "settings.py").read_text(encoding="utf-8")
    assert 'UPDATE_URL = "https://pub.r2.myapp.com"' in settings


def test_generate_returns_three_paths(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater"
    out.mkdir()
    files = UpdaterService.generate(cfg, out)
    assert len(files) == 3
    assert all(f.exists() for f in files)
