from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared.exceptions import ConfigurationError


def _cfg(tmp_path: Path, **kwargs: Any) -> CompilerConfig:
    main = tmp_path / "main.py"
    if not main.exists():
        main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="2.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
        **kwargs,
    )


def _upload_recorder(calls: list[dict]):
    """Enregistre chaque upload avec les fichiers de la source (copie temporaire)."""

    def _record(**kw: Any) -> None:
        src = Path(kw["source_path"])
        files = (
            {p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()}
            if src.is_dir()
            else set()
        )
        calls.append({**kw, "files": files})

    return staticmethod(_record)


def test_upload_release_pushes_tuf_to_update_and_zip_to_release(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _cfg(
        tmp_path,
        tuf_enabled=True,
        repo_destination="disk",
        repo_endpoint=str(tmp_path / "remote"),
        release_destination="disk",
        release_endpoint=str(tmp_path / "remote"),
    )
    # Créer le zip pour que assemble_release_dir le copie
    (tmp_path / "repo" / "metadata").mkdir(parents=True)
    (tmp_path / "repo" / "metadata" / "root.json").write_text("{}", encoding="utf-8")
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
        _upload_recorder(upload_calls),
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.upload()

    assert len(upload_calls) == 2
    # 1er appel : arbre TUF vers update/
    repo_call = upload_calls[0]
    assert repo_call["upload_type"] == "disk"
    # Copie filtrée de l'arbre TUF, même disposition.
    assert repo_call["files"] == {"metadata/root.json"}
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
        tuf_enabled=True,
        repo_destination="r2",
        repo_endpoint="my-bucket/chan",
        repo_public_url="https://pub.r2.example.com",
    )
    (tmp_path / "repo" / "metadata").mkdir(parents=True)
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


def test_upload_artifact_when_no_release(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(
        tmp_path,
        tuf_enabled=False,
        repo_destination="disk",
        repo_endpoint=str(tmp_path / "releases"),
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
    cfg = _cfg(tmp_path, tuf_enabled=False, repo_destination="disk")
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


def test_upload_should_warn_that_it_is_deprecated(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, tuf_enabled=False, repo_destination="disk")
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.upload_artifact",
        lambda *_a, **_kw: None,
    )
    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    with pytest.warns(DeprecationWarning, match="ezcompiler publish"):
        ez.upload()


def test_upload_should_remain_non_interactive(monkeypatch, tmp_path: Path) -> None:
    """Une methode Python ne doit jamais interroger stdin."""

    def _boom(*_args: Any, **_kwargs: Any) -> str:
        raise AssertionError("upload() ne doit pas lire stdin")

    class _NoStdin:
        """click.confirm lit stdin sans passer par builtins.input."""

        def read(self, *_args: Any) -> str:
            raise AssertionError("upload() ne doit pas lire stdin")

        readline = read

    monkeypatch.setattr("builtins.input", _boom)
    monkeypatch.setattr("sys.stdin", _NoStdin())
    cfg = _cfg(tmp_path, tuf_enabled=False, repo_destination="disk")
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.upload_artifact",
        lambda *_a, **_kw: None,
    )
    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    with pytest.warns(DeprecationWarning):
        ez.upload()
