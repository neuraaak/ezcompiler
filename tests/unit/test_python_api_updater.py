from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared import CompilerConfig
from ezcompiler.shared.exceptions import ConfigurationError


def _cfg(tmp_path: Path, tuf_enabled: bool = True) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    if tuf_enabled:
        (tmp_path / "repo" / "metadata").mkdir(parents=True)
        (tmp_path / "repo" / "metadata" / "root.json").write_text(
            "{}", encoding="utf-8"
        )
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=tuf_enabled,
        tuf_repo_dir=tmp_path / "repo" if tuf_enabled else None,
        repo_destination="disk",
        repo_endpoint=str(tmp_path / "repo") if tuf_enabled else "",
    )


@patch("ezcompiler.interfaces.python_api.UpdaterService.generate")
def test_generate_updater_delegates_to_service(mock_gen, tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    mock_gen.return_value = [tmp_path / "a.py", tmp_path / "b.py", tmp_path / "c.json"]
    compiler = EzCompiler(cfg)
    out = tmp_path / "updater"
    result = compiler.generate_updater(output_dir=out)
    mock_gen.assert_called_once_with(cfg, out)
    assert result == mock_gen.return_value


@patch("ezcompiler.interfaces.python_api.UpdaterService.generate")
def test_generate_updater_patch_config_adds_include_files(
    mock_gen, tmp_path: Path
) -> None:
    cfg = _cfg(tmp_path)
    f1 = tmp_path / "settings.py"
    f2 = tmp_path / "update.py"
    f3 = tmp_path / "root.json"
    mock_gen.return_value = [f1, f2, f3]
    compiler = EzCompiler(cfg)
    compiler.generate_updater(output_dir=tmp_path / "updater", patch_config=True)
    files = cfg.include_files["files"]
    assert str(f1) in files
    assert str(f2) in files
    assert str(f3) in files


@patch("ezcompiler.interfaces.python_api.UpdaterService.generate")
def test_generate_updater_no_patch_config_leaves_include_files_unchanged(
    mock_gen, tmp_path: Path
) -> None:
    cfg = _cfg(tmp_path)
    mock_gen.return_value = [tmp_path / "a", tmp_path / "b", tmp_path / "c"]
    original = list(cfg.include_files["files"])
    compiler = EzCompiler(cfg)
    compiler.generate_updater(output_dir=tmp_path / "out", patch_config=False)
    assert cfg.include_files["files"] == original


def test_generate_updater_not_initialized_raises() -> None:
    compiler = EzCompiler()
    with pytest.raises(ConfigurationError):
        compiler.generate_updater()


@patch("ezcompiler.interfaces.python_api.UpdaterService.generate")
def test_generate_updater_default_output_dir_uses_main_file_parent(
    mock_gen, tmp_path: Path
) -> None:
    cfg = _cfg(tmp_path)
    mock_gen.return_value = []
    compiler = EzCompiler(cfg)
    compiler.generate_updater()
    called_dir = mock_gen.call_args.args[1]
    assert called_dir == Path(cfg.main_file).parent
