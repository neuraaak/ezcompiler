from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.shared._compiler_config import CompilerConfig
from ezcompiler.shared.exceptions import ConfigurationError


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


def test_installer_defaults(tmp_path: Path) -> None:
    config = CompilerConfig(**_base_kwargs(tmp_path))
    assert config.installer_enabled is False
    assert config.installer_output_dir is None
    assert config.installer_iss_path is None


def test_installer_iss_path_must_exist_when_provided(tmp_path: Path) -> None:
    kwargs = _base_kwargs(tmp_path)
    kwargs["installer_enabled"] = True
    kwargs["installer_iss_path"] = tmp_path / "absent.iss"
    with pytest.raises(ConfigurationError, match="installer_iss_path"):
        CompilerConfig(**kwargs)


def test_installer_iss_path_ok_when_existing(tmp_path: Path) -> None:
    iss_file = tmp_path / "custom.iss"
    iss_file.write_text("[Setup]")
    kwargs = _base_kwargs(tmp_path)
    kwargs["installer_enabled"] = True
    kwargs["installer_iss_path"] = iss_file
    config = CompilerConfig(**kwargs)
    assert config.installer_iss_path == iss_file


def test_to_dict_from_dict_roundtrip_installer_group(tmp_path: Path) -> None:
    kwargs = _base_kwargs(tmp_path)
    kwargs["installer_enabled"] = True
    kwargs["installer_output_dir"] = tmp_path / "installer"
    config = CompilerConfig(**kwargs)

    config_dict = config.to_dict()
    assert config_dict["installer"] == {
        "installer_enabled": True,
        "installer_output_dir": str(tmp_path / "installer"),
        "installer_iss_path": None,
    }

    restored = CompilerConfig.from_dict(config_dict)
    assert restored.installer_enabled is True
    assert restored.installer_output_dir == tmp_path / "installer"
