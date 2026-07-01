from __future__ import annotations

import py_compile
from pathlib import Path

import pytest

from ezcompiler.services.updater_service import UpdaterService
from ezcompiler.shared import CompilerConfig


@pytest.fixture()
def tuf_repo(tmp_path: Path) -> Path:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    (meta / "root.json").write_text('{"signed": {"_type": "root"}}', encoding="utf-8")
    return tmp_path / "repo"


@pytest.fixture()
def cfg(tmp_path: Path, tuf_repo: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="2.0.0",
        project_name="IntegApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=tuf_repo,
        repo_destination="disk",
        repo_endpoint=str(tuf_repo),
    )


def test_all_files_generated(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater_out"
    files = UpdaterService.generate(cfg, out)
    assert len(files) == 3
    for f in files:
        assert f.exists(), f"{f} not found"


def test_settings_contains_correct_values(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    text = (out / "settings.py").read_text(encoding="utf-8")
    assert 'APP_NAME = "IntegApp"' in text
    assert 'VERSION = "2.0.0"' in text
    assert "file://" in text


def test_root_json_content_matches_source(
    cfg: CompilerConfig, tmp_path: Path, tuf_repo: Path
) -> None:
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    src = (tuf_repo / "metadata" / "root.json").read_text(encoding="utf-8")
    dst = (out / "root.json").read_text(encoding="utf-8")
    assert src == dst


def test_update_py_is_valid_syntax(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    py_compile.compile(str(out / "update.py"), doraise=True)


def test_settings_py_is_valid_syntax(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    py_compile.compile(str(out / "settings.py"), doraise=True)


def test_output_dir_created_if_absent(cfg: CompilerConfig, tmp_path: Path) -> None:
    out = tmp_path / "new" / "nested" / "dir"
    assert not out.exists()
    UpdaterService.generate(cfg, out)
    assert out.exists()


def test_update_py_uses_tufup_010_client_api(
    cfg: CompilerConfig, tmp_path: Path
) -> None:
    """Guard against regressing to the pre-0.10 tufup Client signature."""
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    text = (out / "update.py").read_text(encoding="utf-8")
    # tufup 0.10 requires local metadata/target caches.
    assert "metadata_dir" in text
    assert "target_dir" in text
    # Removed in tufup 0.10 — their presence means the old API leaked back.
    assert "trusted_root_path" not in text
    assert "highest_version" not in text


def test_update_py_handles_file_url_scheme(cfg: CompilerConfig, tmp_path: Path) -> None:
    """disk-served repos need a custom fetcher (tufup's default can't read
    file://). Guard that the file:// fetcher stays in the generated client."""
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    text = (out / "update.py").read_text(encoding="utf-8")
    assert "_FileFetcher" in text
    assert "DownloadHTTPError" in text
    assert 'UPDATE_URL.startswith("file://")' in text


def test_update_py_resets_cache_on_root_mismatch(
    cfg: CompilerConfig, tmp_path: Path
) -> None:
    """A stale cached trust root (regenerated keystore) must not deadlock the
    client with 'signed by 0/1 keys' — the bundled root wins."""
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    text = (out / "update.py").read_text(encoding="utf-8")
    assert "_bootstrap_trust_root" in text
    assert "read_bytes()" in text
    assert "rmtree" in text


def test_update_py_applies_update_in_main(cfg: CompilerConfig, tmp_path: Path) -> None:
    """main() must apply a detected update (not just report it)."""
    out = tmp_path / "updater_out"
    UpdaterService.generate(cfg, out)
    text = (out / "update.py").read_text(encoding="utf-8")
    assert "download_and_apply_update" in text
    assert "sys.exit(0)" in text
