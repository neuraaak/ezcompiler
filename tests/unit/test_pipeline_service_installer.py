from __future__ import annotations

from pathlib import Path
from typing import Any

from ezcompiler.services.installer_service import InstallerService
from ezcompiler.services.pipeline_service import PipelineService
from ezcompiler.shared._compiler_config import CompilerConfig
from ezcompiler.shared._installer_config import InstallerConfig


def _config(tmp_path: Path, **overrides: Any) -> CompilerConfig:
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")
    kwargs: dict[str, Any] = {
        "version": "1.0.0",
        "project_name": "MyApp",
        "main_file": str(main_file),
        "include_files": {"files": [], "folders": []},
        "output_folder": tmp_path / "dist",
    }
    kwargs.update(overrides)
    return CompilerConfig(**kwargs)


def _capture(calls: dict[str, Any]):
    def _fake_build_installer(**kwargs: Any):
        calls.update(kwargs)
        return kwargs["output_dir"] / "MyApp-1.0.0-setup.exe"

    return _fake_build_installer


def test_build_installer_returns_none_when_disabled(tmp_path: Path) -> None:
    config = _config(tmp_path, installer=InstallerConfig(enabled=False))
    assert PipelineService.build_installer(config, None) is None


def test_build_installer_passes_the_sub_config_unchanged(tmp_path, monkeypatch):
    """No intermediate dict: that indirection caused defect 4."""
    installer = InstallerConfig(enabled=True, per_user=True, add_to_path=True)
    captured: dict[str, Any] = {}
    monkeypatch.setattr(InstallerService, "build_installer", _capture(captured))
    PipelineService.build_installer(_config(tmp_path, installer=installer), None)
    assert captured["installer_config"] is installer


def test_build_installer_delegates_when_enabled(monkeypatch, tmp_path: Path) -> None:
    kwargs = {
        "installer": InstallerConfig(enabled=True),
    }
    tmp_path.joinpath("dist").mkdir(parents=True, exist_ok=True)
    config = _config(tmp_path, **kwargs)

    calls: dict[str, object] = {}
    monkeypatch.setattr(InstallerService, "build_installer", _capture(calls))

    result = PipelineService.build_installer(config, compilation_result=None)

    assert result == config.output_folder.parent / "installer" / "MyApp-1.0.0-setup.exe"
    assert calls["bundle_dir"] == config.output_folder
    assert calls["app_name"] == "MyApp"
    assert calls["version"] == "1.0.0"


def test_build_installer_forwards_company_name_and_icon(tmp_path, monkeypatch):
    """The AppId GUID derivation must see the same company name as `generate iss`."""
    icon = tmp_path / "app.ico"
    icon.write_bytes(b"")
    config = _config(
        tmp_path,
        installer=InstallerConfig(enabled=True),
        company_name="Acme Corp",
        icon=str(icon),
    )
    captured: dict[str, Any] = {}
    monkeypatch.setattr(InstallerService, "build_installer", _capture(captured))

    PipelineService.build_installer(config, None)

    assert captured["company_name"] == "Acme Corp"
    assert captured["icon"] == str(icon)


def test_file_mode_warns_about_ignored_options(tmp_path, monkeypatch, caplog):
    """Silently dead config is the trap the spec closes."""
    script = tmp_path / "custom.iss"
    script.write_text("; user", encoding="utf-8")
    installer = InstallerConfig(
        enabled=True, iss_path=script, add_to_path=True, per_user=True
    )
    monkeypatch.setattr(InstallerService, "build_installer", _capture({}))

    with caplog.at_level("WARNING"):
        PipelineService.build_installer(_config(tmp_path, installer=installer), None)

    assert "add_to_path" in caplog.text
    assert "per_user" in caplog.text
    assert "generate iss --force" in caplog.text


def test_file_mode_does_not_warn_about_frame_options(tmp_path, monkeypatch, caplog):
    """enabled / iss_path / output_dir / iscc_path stay meaningful in file mode."""
    script = tmp_path / "custom.iss"
    script.write_text("; user", encoding="utf-8")
    installer = InstallerConfig(enabled=True, iss_path=script)
    monkeypatch.setattr(InstallerService, "build_installer", _capture({}))

    with caplog.at_level("WARNING"):
        PipelineService.build_installer(_config(tmp_path, installer=installer), None)

    assert "iss_path" not in caplog.text


def test_build_stages_includes_installer_stage(tmp_path: Path) -> None:
    config = _config(tmp_path)
    stages = PipelineService.build_stages(config, should_installer=True)
    names = [s["name"] for s in stages]
    assert names == ["main", "version", "compile", "installer"]
