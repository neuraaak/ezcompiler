from __future__ import annotations

from pathlib import Path

from ezcompiler.services.pipeline_service import PipelineService
from ezcompiler.shared._compiler_config import CompilerConfig


def _base_kwargs(tmp_path: Path) -> dict:
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")
    return {
        "version": "1.0.0",
        "project_name": "MyApp",
        "main_file": str(main_file),
        "include_files": {"files": [], "folders": []},
        "output_folder": tmp_path / "dist",
    }


def test_build_installer_returns_none_when_disabled(tmp_path: Path) -> None:
    config = CompilerConfig(**_base_kwargs(tmp_path))
    result = PipelineService.build_installer(config, compilation_result=None)
    assert result is None


def test_build_installer_delegates_when_enabled(monkeypatch, tmp_path: Path) -> None:
    kwargs = _base_kwargs(tmp_path)
    kwargs["installer_enabled"] = True
    kwargs["output_folder"].mkdir(parents=True)
    config = CompilerConfig(**kwargs)

    calls: dict[str, object] = {}

    def _fake_build_installer(**kw):
        calls.update(kw)
        return kw["output_dir"] / "MyApp-1.0.0-setup.exe"

    monkeypatch.setattr(
        "ezcompiler.services.pipeline_service.InstallerService.build_installer",
        _fake_build_installer,
    )

    result = PipelineService.build_installer(config, compilation_result=None)

    assert result == config.output_folder.parent / "installer" / "MyApp-1.0.0-setup.exe"
    assert calls["bundle_dir"] == config.output_folder
    assert calls["app_name"] == "MyApp"
    assert calls["version"] == "1.0.0"


def test_build_stages_includes_installer_stage(tmp_path: Path) -> None:
    config = CompilerConfig(**_base_kwargs(tmp_path))
    stages = PipelineService.build_stages(config, should_installer=True)
    names = [s["name"] for s in stages]
    assert names == ["main", "version", "compile", "installer"]
