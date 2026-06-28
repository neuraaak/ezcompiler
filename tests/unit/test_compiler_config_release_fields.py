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


def _base(main_file: Path, **extra) -> CompilerConfig:
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=main_file.parent / "dist",
        **extra,
    )


# ── new field names ────────────────────────────────────────────────────────────


def test_tuf_enabled_defaults_false(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.tuf_enabled is False


def test_tuf_dir_fields_default_none(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.tuf_repo_dir is None
    assert cfg.tuf_keys_dir is None


def test_tuf_fields_settable(main_file: Path) -> None:
    cfg = _base(
        main_file,
        tuf_enabled=True,
        tuf_repo_dir=main_file.parent / "repo",
        tuf_keys_dir=main_file.parent / "keystore",
    )
    assert cfg.tuf_enabled is True
    assert cfg.tuf_repo_dir == main_file.parent / "repo"
    assert cfg.tuf_keys_dir == main_file.parent / "keystore"


def test_tuf_dirs_coerced_from_str_to_path(main_file: Path) -> None:
    cfg = _base(
        main_file,
        tuf_repo_dir=str(main_file.parent / "repo"),
        tuf_keys_dir=str(main_file.parent / "keystore"),
    )
    assert isinstance(cfg.tuf_repo_dir, Path)
    assert isinstance(cfg.tuf_keys_dir, Path)


# ── unified endpoints ──────────────────────────────────────────────────────────


def test_repo_endpoint_defaults_empty(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.repo_endpoint == ""


def test_release_endpoint_defaults_empty(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.release_endpoint == ""


def test_repo_endpoint_settable(main_file: Path) -> None:
    cfg = _base(main_file, repo_endpoint="./dist/repo")
    assert cfg.repo_endpoint == "./dist/repo"


def test_release_endpoint_settable(main_file: Path) -> None:
    cfg = _base(main_file, release_endpoint="./dist/release")
    assert cfg.release_endpoint == "./dist/release"


# ── resolved properties ────────────────────────────────────────────────────────


def test_resolved_repo_destination_returns_repo_endpoint(main_file: Path) -> None:
    cfg = _base(main_file, repo_endpoint="./dist/repo")
    assert cfg.resolved_repo_destination == "./dist/repo"


def test_resolved_repo_destination_returns_none_when_empty(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.resolved_repo_destination is None


def test_resolved_release_destination_returns_release_endpoint(main_file: Path) -> None:
    cfg = _base(main_file, release_endpoint="https://srv.example.com")
    assert cfg.resolved_release_destination == "https://srv.example.com"


def test_resolved_release_destination_returns_none_when_empty(main_file: Path) -> None:
    cfg = _base(main_file)
    assert cfg.resolved_release_destination is None


# ── validation: endpoint required for non-disk ────────────────────────────────


def test_repo_destination_server_requires_repo_endpoint(main_file: Path) -> None:
    with pytest.raises(ConfigurationError, match="repo_endpoint"):
        _base(main_file, repo_destination="server", repo_endpoint="")


def test_repo_destination_r2_requires_repo_endpoint(main_file: Path) -> None:
    with pytest.raises(ConfigurationError, match="repo_endpoint"):
        _base(main_file, repo_destination="r2", repo_endpoint="")


def test_repo_destination_disk_allows_empty_repo_endpoint(main_file: Path) -> None:
    cfg = _base(main_file, repo_destination="disk", repo_endpoint="")
    assert cfg.repo_endpoint == ""


def test_release_destination_server_requires_release_endpoint(main_file: Path) -> None:
    with pytest.raises(ConfigurationError, match="release_endpoint"):
        _base(main_file, release_destination="server", release_endpoint="")


def test_release_destination_disk_allows_empty_release_endpoint(
    main_file: Path,
) -> None:
    cfg = _base(main_file, release_destination="disk", release_endpoint="")
    assert cfg.release_endpoint == ""


# ── destination values unchanged ───────────────────────────────────────────────


@pytest.mark.parametrize("value", ["disk", "server", "r2"])
def test_repo_destination_accepts_valid_values(main_file: Path, value: str) -> None:
    endpoint = (
        "bucket/prefix"
        if value == "r2"
        else ("https://x.com" if value == "server" else "")
    )
    cfg = _base(main_file, repo_destination=value, repo_endpoint=endpoint)
    assert cfg.repo_destination == value


@pytest.mark.parametrize("value", ["s3", "vcs", "ftp", ""])
def test_repo_destination_rejects_invalid_values(main_file: Path, value: str) -> None:
    with pytest.raises(ConfigurationError, match="repo_destination"):
        _base(main_file, repo_destination=value)


@pytest.mark.parametrize("value", ["disk", "server"])
def test_release_destination_accepts_valid_values(main_file: Path, value: str) -> None:
    endpoint = "https://x.com" if value == "server" else ""
    cfg = _base(main_file, release_destination=value, release_endpoint=endpoint)
    assert cfg.release_destination == value


@pytest.mark.parametrize("value", ["r2", "s3", "vcs", "ftp", ""])
def test_release_destination_rejects_invalid_values(
    main_file: Path, value: str
) -> None:
    with pytest.raises(ConfigurationError, match="release_destination"):
        _base(main_file, release_destination=value)


# ── to_dict / from_dict roundtrip ─────────────────────────────────────────────


def test_tuf_fields_in_to_dict(main_file: Path) -> None:
    d = _base(main_file).to_dict()
    release = d["release"]
    assert "tuf_enabled" in release
    assert "tuf_repo_dir" in release
    assert "tuf_keys_dir" in release


def test_endpoint_fields_in_to_dict(main_file: Path) -> None:
    d = _base(
        main_file, repo_endpoint="./dist/repo", release_endpoint="./dist/release"
    ).to_dict()
    upload = d["upload"]
    assert upload["repo_endpoint"] == "./dist/repo"
    assert upload["release_endpoint"] == "./dist/release"


def test_from_dict_roundtrip_preserves_endpoints(main_file: Path) -> None:
    cfg = _base(
        main_file, repo_endpoint="./dist/repo", release_endpoint="./dist/release"
    )
    restored = CompilerConfig.from_dict(cfg.to_dict())
    assert restored.repo_endpoint == "./dist/repo"
    assert restored.release_endpoint == "./dist/release"


# ── migration errors for removed keys ─────────────────────────────────────────


def _raw(main_file: Path, **upload_overrides) -> dict:
    return {
        "version": "1.0.0",
        "project_name": "App",
        "main_file": str(main_file),
        "include_files": {"files": [], "folders": []},
        "output_folder": str(main_file.parent / "dist"),
        "upload": {
            "repo_destination": "disk",
            "release_destination": "disk",
            **upload_overrides,
        },
    }


@pytest.mark.parametrize(
    "removed_key",
    ["repo_path", "server_url", "update_repo_url", "r2_bucket", "r2_remote_prefix"],
)
def test_from_dict_raises_on_removed_upload_keys(
    main_file: Path, removed_key: str
) -> None:
    with pytest.raises(ConfigurationError):
        CompilerConfig.from_dict(_raw(main_file, **{removed_key: "anything"}))


@pytest.mark.parametrize(
    "removed_key", ["release_needed", "release_type", "repo_needed"]
)
def test_from_dict_raises_on_removed_release_keys(
    main_file: Path, removed_key: str
) -> None:
    raw = _raw(main_file)
    raw["release"] = {removed_key: True}
    with pytest.raises(ConfigurationError):
        CompilerConfig.from_dict(raw)


def test_from_dict_raises_on_upload_structure(main_file: Path) -> None:
    with pytest.raises(ConfigurationError, match="upload_structure"):
        CompilerConfig.from_dict(_raw(main_file, structure="disk"))
