from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ezcompiler.interfaces.cli_interface import main


def _fake_cfg(tmp_path: Path) -> dict:
    return {
        "version": "1.0.0",
        "project_name": "MyApp",
        "main_file": str(tmp_path / "main.py"),
        "include_files": {"files": [], "folders": []},
        "output_folder": str(tmp_path / "dist"),
        "tufup_repo_dir": str(tmp_path / "repo"),
        "tufup_keys_dir": str(tmp_path / "keystore"),
    }


def test_release_init_calls_init_release_and_exits_0(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[dict] = []

    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.load_config",
        lambda *_a, **_kw: _fake_cfg(tmp_path),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ReleaseService.init_release",
        staticmethod(lambda **kw: calls.append(kw) or True),
    )
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["release", "init"])

    assert result.exit_code == 0, result.output
    assert len(calls) == 1
    assert calls[0]["app_name"] == "MyApp"


def test_release_init_already_present_exits_0(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.load_config",
        lambda *_a, **_kw: _fake_cfg(tmp_path),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ReleaseService.init_release",
        staticmethod(lambda **_kw: False),
    )
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["release", "init"])

    assert result.exit_code == 0, result.output


def test_release_init_error_exits_1(monkeypatch, tmp_path: Path) -> None:
    from ezcompiler.shared.exceptions import ReleaseError

    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ConfigService.load_config",
        lambda *_a, **_kw: _fake_cfg(tmp_path),
    )
    monkeypatch.setattr(
        "ezcompiler.interfaces.cli_interface.ReleaseService.init_release",
        staticmethod(
            lambda **_kw: (_ for _ in ()).throw(ReleaseError("tufup not installed"))
        ),
    )
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["release", "init"])

    assert result.exit_code == 1
