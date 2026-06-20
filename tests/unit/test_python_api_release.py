from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.python_api import EzCompiler


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
    cfg_no_repo = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(tmp_path / "main.py"),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
    )
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")

    captured: dict = {}
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.ReleaseService.release_and_publish",
        staticmethod(lambda **kw: captured.update(kw) or (tmp_path / "r")),
    )

    EzCompiler(cfg_no_repo).release(bundle_dir=tmp_path / "bundle")

    assert captured["repo_dir"] == tmp_path / "dist" / "repo"
