from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.cli_interface import main


def _real_cfg(tmp_path: Path) -> CompilerConfig:
    main_file = tmp_path / "main.py"
    main_file.write_text("# m", encoding="utf-8")
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
    )


def _write_cfg_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "ezcompiler.json"
    cfg.write_text("{}", encoding="utf-8")
    return cfg


def test_upload_invokes_api_upload_and_exits_0(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
        staticmethod(lambda **_kw: _real_cfg(tmp_path)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.EzCompiler.upload",
        lambda *_a, **kw: calls.append(kw),
    )
    cfg_file = _write_cfg_file(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["upload", "--config", str(cfg_file)])

    assert result.exit_code == 0, result.output
    assert len(calls) == 1


def test_upload_passes_repo_and_release_destination_overrides(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
        staticmethod(lambda **_kw: _real_cfg(tmp_path)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.EzCompiler.upload",
        lambda *_a, **kw: calls.append(kw),
    )
    cfg_file = _write_cfg_file(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "upload",
            "--config",
            str(cfg_file),
            "--repo-destination",
            "server",
            "--release-destination",
            "disk",
            "--destination",
            "https://h/up",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls[0]["repo_destination"] == "server"
    assert calls[0]["release_destination"] == "disk"
    assert calls[0]["destination"] == "https://h/up"


def test_upload_error_exits_1(monkeypatch, tmp_path: Path) -> None:
    from ezcompiler.shared.exceptions import UploadError

    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
        staticmethod(lambda **_kw: _real_cfg(tmp_path)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.EzCompiler.upload",
        lambda *_a, **_kw: (_ for _ in ()).throw(UploadError("boom")),
    )
    cfg_file = _write_cfg_file(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["upload", "--config", str(cfg_file)])

    assert result.exit_code == 1
