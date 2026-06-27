from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared.exceptions import SigningKeyError


@pytest.fixture()
def cfg(tmp_path: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="2.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tufup_repo_dir=tmp_path / "repo",
        tufup_keys_dir=tmp_path / "keystore",
    )


def test_release_delegates_to_service(
    monkeypatch, tmp_path: Path, cfg: CompilerConfig
) -> None:
    captured: dict = {}

    def _fake_release(**kwargs):
        captured.update(kwargs)
        return tmp_path / "repo" / "repository"

    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.ReleaseService.release_and_publish",
        staticmethod(_fake_release),
    )

    EzCompiler(cfg).release(bundle_dir=tmp_path / "bundle")

    assert captured["app_name"] == "MyApp"
    assert captured["version"] == "2.0.0"
    assert captured["repo_dir"] == tmp_path / "repo"


def test_release_uses_output_folder_as_default_repo(
    monkeypatch, tmp_path: Path
) -> None:
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")
    cfg_no_repo = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(tmp_path / "main.py"),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
    )

    captured: dict = {}
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.ReleaseService.release_and_publish",
        staticmethod(lambda **kw: captured.update(kw) or (tmp_path / "r")),
    )

    EzCompiler(cfg_no_repo).release(bundle_dir=tmp_path / "bundle")

    assert captured["repo_dir"] == tmp_path / "dist" / "repo"


def _make_cfg(tmp_path: Path, **kwargs: object) -> CompilerConfig:
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


def test_init_release_delegates_to_service(monkeypatch, tmp_path: Path) -> None:
    cfg = _make_cfg(tmp_path)
    captured: dict = {}

    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.ReleaseService.init_release",
        staticmethod(lambda **kw: captured.update(kw) or True),
    )

    result = EzCompiler(cfg).init_release()

    assert result is True
    assert captured["app_name"] == "MyApp"
    assert captured["repo_dir"] == tmp_path / "repo"
    assert captured["keys_dir"] == tmp_path / "keystore"


def test_run_pipeline_preflight_raises_before_compile_when_keys_missing(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _make_cfg(tmp_path, release_needed=True)
    compile_called: list = []

    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.compile_project",
        lambda *_a, **_kw: compile_called.append(True),
    )

    with pytest.raises(SigningKeyError, match="ezcompiler release init"):
        EzCompiler(cfg).run_pipeline()

    assert compile_called == [], "compile_project must NOT be called before pre-flight"


def test_run_pipeline_uploads_publish_root_after_release(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _make_cfg(
        tmp_path,
        zip_needed=True,
        repo_needed=True,
        release_needed=True,
        upload_structure="disk",
        update_repo_url=str(tmp_path / "remote"),
    )
    # preflight passes: keys present
    (tmp_path / "keystore").mkdir()
    (tmp_path / "keystore" / "root").write_bytes(b"k")

    # local TUF tree produced by the release stage (root with metadata/ + targets/)
    repo_root = tmp_path / "repo"
    (repo_root / "metadata").mkdir(parents=True)
    (repo_root / "metadata" / "root.json").write_text("{}", "utf-8")
    (repo_root / "targets").mkdir()
    (repo_root / "targets" / "App-1.0.0.tar.gz").write_bytes(b"bundle")

    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.release_artifact",
        staticmethod(lambda **_: repo_root),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.UploaderService.upload",
        staticmethod(
            lambda *, source_path, destination, **_kw: calls.append(
                (str(source_path), destination)
            )
        ),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.compile_project",
        lambda *_a, **_kw: (MagicMock(), MagicMock(zip_needed=True)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.zip_artifact",
        lambda *_a, **_kw: True,
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.TemplateService.generate_version_file",
        lambda *_a, **_kw: None,
    )

    # fake produced zip so assemble_release_dir copies it
    zp = Path(cfg.zip_file_path)
    zp.parent.mkdir(parents=True, exist_ok=True)
    zp.write_bytes(b"zip")

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.run_pipeline(console=False)

    assert len(calls) == 1
    source, dest = calls[0]
    assert source.endswith("release")
    assert dest == str(tmp_path / "remote")


def test_release_publish_true_warns(monkeypatch, tmp_path: Path) -> None:
    import warnings

    cfg = _make_cfg(
        tmp_path,
        upload_structure="disk",
        update_repo_url=str(tmp_path / "remote"),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.ReleaseService.release_and_publish",
        staticmethod(lambda **_: tmp_path / "repo" / "repository"),
    )
    compiler = EzCompiler(cfg)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        compiler.release(tmp_path / "bundle", publish=True)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_run_pipeline_skip_release_bypasses_release_stage(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = _make_cfg(tmp_path, release_needed=True)
    release_calls: list = []

    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.release_artifact",
        staticmethod(
            lambda **_: release_calls.append(True) or (tmp_path / "repo" / "repository")
        ),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.PipelineService.compile_project",
        lambda *_a, **_kw: (MagicMock(), MagicMock(zip_needed=False)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.TemplateService.generate_version_file",
        lambda *_a, **_kw: None,
    )

    ez = EzCompiler(cfg)
    ez._printer = MagicMock()
    ez.run_pipeline(skip_release=True, skip_upload=True, skip_zip=True)

    assert release_calls == []
