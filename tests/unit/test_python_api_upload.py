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


def test_upload_release_dir_when_release_needed(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(
        tmp_path,
        release_needed=True,
        upload_structure="disk",
        update_repo_url=str(tmp_path / "remote"),
    )
    release_root = tmp_path / "dist" / "release"
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.assemble_release_dir",
        staticmethod(lambda *_a, **_kw: release_root),
    )
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.UploaderService.upload",
        staticmethod(
            lambda *, source_path, destination, **_kw: calls.append(
                (str(source_path), destination)
            )
        ),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload()

    assert calls == [(str(release_root), str(tmp_path / "remote"))]


def test_upload_artifact_when_no_release(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(
        tmp_path,
        release_needed=False,
        upload_structure="disk",
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


def test_upload_overrides_destination_and_structure(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _cfg(tmp_path, release_needed=False, upload_structure="disk")
    captured: dict = {}
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.upload_artifact",
        lambda *_a, **kw: captured.update(kw),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload(destination="https://h/up", structure="server")

    assert captured["structure"] == "server"
    assert captured["destination"] == "https://h/up"


def test_upload_raises_when_not_initialized() -> None:
    ez = EzCompiler.__new__(EzCompiler)  # bypass __init__
    ez._config = None
    with pytest.raises(ConfigurationError):
        ez.upload()
