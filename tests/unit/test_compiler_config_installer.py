from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ezcompiler.shared._compiler_config import CompilerConfig
from ezcompiler.shared._installer_config import InstallerConfig
from ezcompiler.shared.exceptions import ConfigurationError


def _base_kwargs(tmp_path: Path) -> dict[str, Any]:
    main = tmp_path / "main.py"
    main.write_text("print('hi')", encoding="utf-8")
    return {
        "version": "1.0.0",
        "project_name": "MyApp",
        "main_file": str(main),
        "include_files": {"files": [], "folders": []},
        "output_folder": tmp_path / "dist",
    }


def test_installer_defaults_to_a_disabled_sub_config(tmp_path: Path) -> None:
    config = CompilerConfig(**_base_kwargs(tmp_path))
    assert isinstance(config.installer, InstallerConfig)
    assert config.installer.enabled is False


def test_installer_sub_config_is_never_none(tmp_path: Path) -> None:
    """Consumers test config.installer.enabled without a None guard."""
    config = CompilerConfig(**_base_kwargs(tmp_path))
    assert config.installer is not None


def test_from_dict_builds_the_sub_config(tmp_path: Path) -> None:
    data = {**_base_kwargs(tmp_path), "installer": {"enabled": True, "per_user": True}}
    config = CompilerConfig.from_dict(data)
    assert config.installer.enabled is True
    assert config.installer.per_user is True


def test_from_dict_without_installer_section(tmp_path: Path) -> None:
    config = CompilerConfig.from_dict(_base_kwargs(tmp_path))
    assert config.installer.enabled is False


@pytest.mark.parametrize(
    "legacy_key",
    [
        "installer_enabled",
        "installer_output_dir",
        "installer_iss_path",
        "installer_per_user",
    ],
)
def test_flat_installer_keys_are_rejected(tmp_path: Path, legacy_key: str) -> None:
    """v4.0.0 migration: the message must carry the replacement."""
    data = {**_base_kwargs(tmp_path), legacy_key: True}
    with pytest.raises(ConfigurationError, match="tool.ezcompiler.installer"):
        CompilerConfig.from_dict(data)


@pytest.mark.parametrize(
    ("legacy_key", "replacement"),
    [
        ("installer_enabled", "enabled"),
        ("installer_output_dir", "output_dir"),
        ("installer_iss_path", "iss_path"),
        ("installer_per_user", "per_user"),
    ],
)
def test_nested_flat_installer_keys_name_their_replacement(
    tmp_path: Path, legacy_key: str, replacement: str
) -> None:
    """v3.4.0's own to_dict() emitted {"installer": {"installer_enabled": ...}},
    so this — not the top-level shape — is the config users actually have."""
    data = {**_base_kwargs(tmp_path), "installer": {legacy_key: True}}
    with pytest.raises(ConfigurationError, match=f"{legacy_key} -> {replacement}"):
        CompilerConfig.from_dict(data)


def test_ico_icon_is_accepted_when_installer_enabled(tmp_path: Path) -> None:
    icon = tmp_path / "app.ico"
    icon.write_bytes(b"\x00\x00\x01\x00")
    config = CompilerConfig(
        **_base_kwargs(tmp_path),
        icon=str(icon),
        installer=InstallerConfig(enabled=True),
    )
    assert config.icon == str(icon)


def test_non_ico_icon_is_rejected_when_installer_enabled(tmp_path: Path) -> None:
    """Defect 5: Inno requires .ico; a .png fails ISCC with an opaque exit 2."""
    icon = tmp_path / "app.png"
    icon.write_bytes(b"\x89PNG")
    with pytest.raises(ConfigurationError, match="icon"):
        CompilerConfig(
            **_base_kwargs(tmp_path),
            icon=str(icon),
            installer=InstallerConfig(enabled=True),
        )


def test_non_ico_icon_is_tolerated_when_installer_disabled(tmp_path: Path) -> None:
    """Compilers accept other formats; only the installer stage is strict."""
    icon = tmp_path / "app.png"
    icon.write_bytes(b"\x89PNG")
    config = CompilerConfig(**_base_kwargs(tmp_path), icon=str(icon))
    assert config.icon == str(icon)


def test_to_dict_emits_the_installer_section(tmp_path: Path) -> None:
    config = CompilerConfig(**_base_kwargs(tmp_path))
    serialized = config.to_dict()
    assert "installer" in serialized
    assert serialized["installer"]["enabled"] is False


def test_to_dict_round_trip_preserves_installer(tmp_path: Path) -> None:
    config = CompilerConfig(
        **_base_kwargs(tmp_path),
        installer=InstallerConfig(enabled=True, add_to_path=True),
    )
    restored = CompilerConfig.from_dict(config.to_dict())
    assert restored.installer == config.installer
