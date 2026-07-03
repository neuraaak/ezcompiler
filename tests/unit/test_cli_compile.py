from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ezcompiler.interfaces.cli_interface import main
from ezcompiler.shared import CompilerConfig


def _cfg(tmp_path: Path) -> CompilerConfig:
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(tmp_path / "main.py"),
        include_files={"files": [], "folders": []},
        output_folder=str(tmp_path / "dist"),
    )


def test_compile_delegates_to_run_pipeline(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []

    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
        staticmethod(lambda **_kw: _cfg(tmp_path)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.EzCompiler.run_pipeline",
        lambda _self, **kw: calls.append(kw),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["compile", "--skip-installer", "--skip-release"])

    assert result.exit_code == 0, result.output
    assert len(calls) == 1
    assert calls[0]["skip_installer"] is True
    assert calls[0]["skip_release"] is True
    assert calls[0]["skip_zip"] is False


def test_compile_error_exits_1(monkeypatch, tmp_path: Path) -> None:
    from ezcompiler.shared.exceptions import CompilationError

    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
        staticmethod(lambda **_kw: _cfg(tmp_path)),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.python_api.EzCompiler.run_pipeline",
        lambda _self, **_kw: (_ for _ in ()).throw(CompilationError("boom")),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["compile"])

    assert result.exit_code == 1
