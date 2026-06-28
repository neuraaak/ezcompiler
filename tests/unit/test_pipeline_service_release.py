from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.services.pipeline_service import PipelineService


@pytest.fixture()
def cfg(tmp_path: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tufup_repo_dir=tmp_path / "repo",
        tufup_keys_dir=tmp_path / "keystore",
    )


def test_build_stages_without_release_has_no_release_stage(
    cfg: CompilerConfig,
) -> None:
    stages = PipelineService.build_stages(cfg, should_zip=False, should_upload=False)
    names = [s["name"] for s in stages]
    assert "release" not in names


def test_build_stages_with_release_adds_release_stage(cfg: CompilerConfig) -> None:
    stages = PipelineService.build_stages(
        cfg, should_zip=False, should_upload=False, should_release=True
    )
    names = [s["name"] for s in stages]
    assert "release" in names


def test_build_stages_release_comes_before_upload(cfg: CompilerConfig) -> None:
    stages = PipelineService.build_stages(
        cfg, should_zip=True, should_upload=True, should_release=True
    )
    names = [s["name"] for s in stages]
    assert names.index("release") < names.index("upload")
    assert names == ["main", "version", "compile", "zip", "release", "upload"]


def test_assemble_release_dir_contains_only_zip(tmp_path: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# m", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
    )
    cfg.output_folder.mkdir(parents=True, exist_ok=True)
    zip_path = Path(cfg.zip_file_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path.write_bytes(b"zip")

    release = PipelineService.assemble_release_dir(cfg)

    assert release.name == "release"
    assert (release / zip_path.name).is_file()
    # aucun fichier TUF dans le dossier release
    assert not any(f.suffix == ".json" for f in release.iterdir())
    assert not any(f.suffix == ".gz" for f in release.iterdir())
    assert not (release / "metadata").exists()
    assert not (release / "targets").exists()


def test_assemble_release_dir_without_zip_file_is_empty(tmp_path: Path) -> None:
    main = tmp_path / "main.py"
    main.write_text("# m", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
    )
    cfg.output_folder.mkdir(parents=True, exist_ok=True)
    # zip file n'existe pas → dossier release vide

    release = PipelineService.assemble_release_dir(cfg)

    assert release.is_dir()
    assert list(release.iterdir()) == []


def test_release_artifact_calls_release_and_publish_with_publish_false(
    monkeypatch, cfg: CompilerConfig
) -> None:
    captured: dict = {}

    def _fake_release(**kwargs) -> Path:
        captured.update(kwargs)
        return cfg.tufup_repo_dir / "repository"

    monkeypatch.setattr(
        "ezcompiler.services.pipeline_service.ReleaseService.release_and_publish",
        staticmethod(_fake_release),
    )

    PipelineService.release_artifact(cfg, compilation_result=None)

    assert captured["publish"] is False


def test_release_artifact_never_publishes_even_if_url_set(
    monkeypatch, tmp_path: Path
) -> None:
    upload_calls: list = []

    monkeypatch.setattr(
        "ezcompiler.services.pipeline_service.ReleaseService.release_and_publish",
        staticmethod(
            lambda **kw: upload_calls.append(kw) or (tmp_path / "repo" / "repository")
        ),
    )
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg_with_url = CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tufup_repo_dir=tmp_path / "repo",
        update_repo_url="https://updates.example.com",
    )
    PipelineService.release_artifact(cfg_with_url, compilation_result=None)

    assert len(upload_calls) == 1
    assert upload_calls[0]["publish"] is False


def test_release_artifact_returns_repository_path(
    monkeypatch, cfg: CompilerConfig
) -> None:
    expected = cfg.tufup_repo_dir / "repository"
    monkeypatch.setattr(
        "ezcompiler.services.pipeline_service.ReleaseService.release_and_publish",
        staticmethod(lambda **_: expected),
    )

    result = PipelineService.release_artifact(cfg, compilation_result=None)

    assert result == expected
