from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.services.pipeline_service import PipelineService
from ezcompiler.shared.exceptions import ReleaseError


def _make_config(tmp_path: Path, *, version: str, project_name: str) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# m", encoding="utf-8")
    cfg = CompilerConfig(
        version=version,
        project_name=project_name,
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
    )
    Path(cfg.zip_file_path).parent.mkdir(parents=True, exist_ok=True)
    return cfg


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
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
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
    assert cfg.tuf_repo_dir is not None
    repo_dir = cfg.tuf_repo_dir

    def _fake_release(**kwargs) -> Path:
        captured.update(kwargs)
        return repo_dir / "repository"

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
        tuf_repo_dir=tmp_path / "repo",
        repo_endpoint="https://updates.example.com",
    )
    PipelineService.release_artifact(cfg_with_url, compilation_result=None)

    assert len(upload_calls) == 1
    assert upload_calls[0]["publish"] is False


def test_release_artifact_returns_repository_path(
    monkeypatch, cfg: CompilerConfig
) -> None:
    assert cfg.tuf_repo_dir is not None
    expected = cfg.tuf_repo_dir / "repository"
    monkeypatch.setattr(
        "ezcompiler.services.pipeline_service.ReleaseService.release_and_publish",
        staticmethod(lambda **_: expected),
    )

    result = PipelineService.release_artifact(cfg, compilation_result=None)

    assert result == expected


def test_should_copy_the_zip_under_its_versioned_name(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path, version="1.2.3", project_name="App")
    Path(cfg.zip_file_path).write_bytes(b"zip")

    assets = PipelineService.stage_versioned_assets(cfg)

    names = [a.name for a in assets]
    assert "App-1.2.3.zip" in names
    assert "App.zip" not in names
    assert all(a.is_file() for a in assets)


def test_should_accept_a_project_without_installer(tmp_path: Path) -> None:
    """Review Focus #4 : installer.enabled=false est legitime, pas une erreur."""
    cfg = _make_config(tmp_path, version="1.2.3", project_name="App")
    cfg.installer.enabled = False
    Path(cfg.zip_file_path).write_bytes(b"zip")

    assets = PipelineService.stage_versioned_assets(cfg)

    assert len(assets) == 1
    assert assets[0].name == "App-1.2.3.zip"


def test_should_list_installer_first_then_zip(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path, version="1.2.3", project_name="App")
    cfg.installer.enabled = True
    Path(cfg.zip_file_path).write_bytes(b"zip")
    installer_dir = cfg.output_folder.parent / "installer"
    installer_dir.mkdir(parents=True, exist_ok=True)
    (installer_dir / "App-1.2.3-setup.exe").write_bytes(b"exe")

    assets = PipelineService.stage_versioned_assets(cfg)

    assert [a.name for a in assets] == ["App-1.2.3-setup.exe", "App-1.2.3.zip"]


def test_should_raise_when_no_artifact_exists(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path, version="1.2.3", project_name="App")

    with pytest.raises(ReleaseError, match="compile"):
        PipelineService.stage_versioned_assets(cfg)


def test_should_be_idempotent(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path, version="1.2.3", project_name="App")
    Path(cfg.zip_file_path).write_bytes(b"zip")

    first = PipelineService.stage_versioned_assets(cfg)
    listing = sorted(p.name for p in first[0].parent.iterdir())
    second = PipelineService.stage_versioned_assets(cfg)

    assert first == second
    assert first[0].read_bytes() == b"zip"
    assert sorted(p.name for p in first[0].parent.iterdir()) == listing


def test_should_raise_when_an_enabled_installer_is_missing(tmp_path: Path) -> None:
    """installer.enabled=true sans .exe : refuser plutot que publier sans lui."""
    cfg = _make_config(tmp_path, version="1.2.3", project_name="App")
    cfg.installer.enabled = True
    Path(cfg.zip_file_path).write_bytes(b"zip")

    with pytest.raises(ReleaseError, match="App-1.2.3-setup.exe"):
        PipelineService.stage_versioned_assets(cfg)


def test_release_artifact_should_forward_required(
    monkeypatch, cfg: CompilerConfig
) -> None:
    captured: dict = {}

    def _fake_release(**kwargs) -> Path:
        captured.update(kwargs)
        return Path("repo")

    monkeypatch.setattr(
        "ezcompiler.services.pipeline_service.ReleaseService.release_and_publish",
        staticmethod(_fake_release),
    )

    PipelineService.release_artifact(cfg, compilation_result=None, required=True)

    assert captured["required"] is True
