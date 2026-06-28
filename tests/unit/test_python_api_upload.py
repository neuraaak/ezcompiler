from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared.exceptions import ConfigurationError


def _cfg(tmp_path: Path, **kwargs: object) -> CompilerConfig:
    main = tmp_path / "main.py"
    if not main.exists():
        main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="2.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tufup_repo_dir=tmp_path / "repo",
        tufup_keys_dir=tmp_path / "keystore",
        **kwargs,
    )


def test_upload_release_pushes_tuf_to_update_and_zip_to_release(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _cfg(
        tmp_path,
        release_needed=True,
        repo_destination="disk",
        repo_path=str(tmp_path / "remote"),
    )
    # Créer le zip pour que assemble_release_dir le copie
    zip_path = tmp_path / "MyApp.zip"
    zip_path.write_bytes(b"zip")
    release_root = tmp_path / "dist" / "release"
    release_root.mkdir(parents=True)
    (release_root / "MyApp.zip").write_bytes(b"zip")

    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.assemble_release_dir",
        staticmethod(lambda *_a: release_root),
    )
    upload_calls: list[dict] = []
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.UploaderService.upload",
        staticmethod(lambda **kw: upload_calls.append(kw)),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload()

    assert len(upload_calls) == 2
    # 1er appel : arbre TUF vers update/
    repo_call = upload_calls[0]
    assert repo_call["upload_type"] == "disk"
    assert str(repo_call["source_path"]) == str(cfg.tufup_repo_dir)
    assert repo_call["destination"].endswith("/update") or repo_call[
        "destination"
    ].endswith("\\update")
    # 2e appel : zip vers release/
    zip_call = upload_calls[1]
    assert zip_call["upload_type"] == "disk"
    assert str(zip_call["source_path"]) == str(release_root)
    assert zip_call["destination"].endswith("/release") or zip_call[
        "destination"
    ].endswith("\\release")


def test_upload_release_r2_only_uploads_tuf(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(
        tmp_path,
        release_needed=True,
        repo_destination="r2",
        r2_bucket="my-bucket",
        r2_remote_prefix="chan",
    )
    upload_calls: list[dict] = []
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.UploaderService.upload",
        staticmethod(lambda **kw: upload_calls.append(kw)),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload()

    assert len(upload_calls) == 1
    assert upload_calls[0]["upload_type"] == "r2"


def test_upload_release_vcs_raises_not_implemented(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(
        tmp_path,
        release_needed=True,
        repo_destination="disk",
        repo_path=str(tmp_path / "remote"),
        release_destination="vcs",
    )
    release_root = tmp_path / "dist" / "release"
    release_root.mkdir(parents=True)
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.assemble_release_dir",
        staticmethod(lambda *_a: release_root),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.UploaderService.upload",
        staticmethod(lambda **_kw: None),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    with pytest.raises(NotImplementedError):
        ez.upload()


def test_upload_artifact_when_no_release(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(
        tmp_path,
        release_needed=False,
        repo_destination="disk",
        repo_path=str(tmp_path / "releases"),
    )
    captured: dict = {}
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.upload_artifact",
        lambda *_a, **kw: captured.update(kw),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload()

    assert captured["structure"] == "disk"
    assert captured["destination"] == str(tmp_path / "releases")


def test_upload_overrides_repo_and_release_destination(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _cfg(tmp_path, release_needed=False, repo_destination="disk")
    captured: dict = {}
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.upload_artifact",
        lambda *_a, **kw: captured.update(kw),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload(destination="https://h/up", repo_destination="server")

    assert captured["structure"] == "server"
    assert captured["destination"] == "https://h/up"


def test_upload_raises_when_not_initialized() -> None:
    ez = EzCompiler.__new__(EzCompiler)
    ez._config = None
    with pytest.raises(ConfigurationError):
        ez.upload()
