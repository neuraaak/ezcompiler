# ///////////////////////////////////////////////////////////////
# TEST_INSTALLER_CONFIG - InstallerConfig validation tests
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Tests for InstallerConfig field validation and serialization."""

from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.shared import ConfigurationError, InstallerConfig

# ////////////////////////////////////////////////
# DEFAULTS
# ////////////////////////////////////////////////


def test_defaults_are_inert() -> None:
    """A default InstallerConfig disables the stage and holds no paths."""
    config = InstallerConfig()
    assert config.enabled is False
    assert config.iss_path is None
    assert config.output_dir is None
    assert config.iscc_path is None
    assert config.architecture == "x64"
    assert config.languages == ["english"]
    assert config.compression == "lzma2/max"
    assert config.desktop_icon is True
    assert config.launch_after_install is True
    assert config.close_running_app is True
    assert config.add_to_path is False
    assert config.per_user is False
    assert config.wizard_style == "modern"
    assert config.uninstall_delete == []
    assert config.extra_setup_directives == {}
    assert config.extra_sections == {}


# ////////////////////////////////////////////////
# PATH VALIDATION
# ////////////////////////////////////////////////


def test_iss_path_must_exist(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="iss_path"):
        InstallerConfig(enabled=True, iss_path=tmp_path / "absent.iss")


def test_license_file_must_exist(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="license_file"):
        InstallerConfig(enabled=True, license_file=tmp_path / "absent.txt")


def test_str_paths_are_coerced(tmp_path: Path) -> None:
    script = tmp_path / "custom.iss"
    script.write_text("; empty", encoding="utf-8")
    config = InstallerConfig(
        enabled=True,
        iss_path=str(script),  # pyright: ignore[reportArgumentType]
    )
    assert isinstance(config.iss_path, Path)


# ////////////////////////////////////////////////
# BOUNDED VALUES
# ////////////////////////////////////////////////


def test_architecture_is_bounded() -> None:
    with pytest.raises(ConfigurationError, match="architecture"):
        InstallerConfig(
            enabled=True,
            architecture="itanium",  # pyright: ignore[reportArgumentType]
        )


def test_wizard_style_is_bounded() -> None:
    with pytest.raises(ConfigurationError, match="wizard_style"):
        InstallerConfig(
            enabled=True,
            wizard_style="retro",  # pyright: ignore[reportArgumentType]
        )


def test_unknown_language_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="languages"):
        InstallerConfig(enabled=True, languages=["klingon"])


def test_duplicate_languages_are_rejected() -> None:
    with pytest.raises(ConfigurationError, match="languages"):
        InstallerConfig(enabled=True, languages=["english", "english"])


def test_empty_languages_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="languages"):
        InstallerConfig(enabled=True, languages=[])


def test_app_id_must_be_a_guid() -> None:
    with pytest.raises(ConfigurationError, match="app_id"):
        InstallerConfig(enabled=True, app_id="not-a-guid")


def test_valid_app_id_is_accepted() -> None:
    config = InstallerConfig(
        enabled=True, app_id="{A1B2C3D4-1111-2222-3333-444455556666}"
    )
    assert config.app_id is not None


# ////////////////////////////////////////////////
# SIGNING
# ////////////////////////////////////////////////


def test_sign_tool_requires_both_fields() -> None:
    with pytest.raises(ConfigurationError, match="sign_tool_command"):
        InstallerConfig(enabled=True, sign_tool_name="mytool")


def test_sign_tool_command_alone_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="sign_tool_name"):
        InstallerConfig(enabled=True, sign_tool_command="signtool.exe $f")


# ////////////////////////////////////////////////
# UNINSTALL DELETE — path containment
# ////////////////////////////////////////////////


@pytest.mark.parametrize(
    "entry",
    [
        r"C:\Windows\System32",
        r"..\..\elsewhere",
        "/etc/passwd",
        r"{app}\..\..\other",
    ],
)
def test_uninstall_delete_rejects_escaping_paths(entry: str) -> None:
    """Absolute or traversing entries would delete files outside the app."""
    with pytest.raises(ConfigurationError, match="uninstall_delete"):
        InstallerConfig(enabled=True, uninstall_delete=[entry])


@pytest.mark.parametrize(
    "entry",
    [r"{app}\cache", r"{localappdata}\MyApp\tufup", r"{userappdata}\MyApp"],
)
def test_uninstall_delete_accepts_inno_constant_paths(entry: str) -> None:
    config = InstallerConfig(enabled=True, uninstall_delete=[entry])
    assert config.uninstall_delete == [entry]


# ////////////////////////////////////////////////
# EXTRA ESCAPE HATCHES — collisions
# ////////////////////////////////////////////////


def test_extra_setup_directive_colliding_with_managed_field_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="PrivilegesRequired"):
        InstallerConfig(
            enabled=True, extra_setup_directives={"PrivilegesRequired": "admin"}
        )


def test_extra_setup_directive_collision_is_case_insensitive() -> None:
    with pytest.raises(ConfigurationError, match="(?i)privilegesrequired"):
        InstallerConfig(
            enabled=True, extra_setup_directives={"privilegesrequired": "admin"}
        )


def test_extra_setup_directive_unmanaged_is_accepted() -> None:
    config = InstallerConfig(
        enabled=True, extra_setup_directives={"AppCopyright": "(c) 2026 Me"}
    )
    assert config.extra_setup_directives["AppCopyright"] == "(c) 2026 Me"


@pytest.mark.parametrize("name", ["Setup", "setup", "FILES", "Icons", "Registry"])
def test_extra_sections_collision_is_case_insensitive(name: str) -> None:
    """Inno section names are case-insensitive; the collision check must be too."""
    with pytest.raises(ConfigurationError, match="(?i)" + name):
        InstallerConfig(enabled=True, extra_sections={name: ["; noop"]})


@pytest.mark.parametrize("name", ["Code", "Dirs", "INI", "Components"])
def test_extra_sections_unmanaged_are_accepted(name: str) -> None:
    config = InstallerConfig(enabled=True, extra_sections={name: ["; noop"]})
    assert name in config.extra_sections


# ////////////////////////////////////////////////
# SERIALIZATION
# ////////////////////////////////////////////////


def test_round_trip_through_dict(tmp_path: Path) -> None:
    original = InstallerConfig(
        enabled=True,
        per_user=True,
        languages=["english", "french"],
        uninstall_delete=[r"{app}\cache"],
        extra_sections={"Code": ["procedure Foo; begin end;"]},
        output_dir=tmp_path / "out",
    )
    restored = InstallerConfig.from_dict(original.to_dict())
    assert restored == original


def test_from_dict_ignores_none_values() -> None:
    """A TOML-generated dict carries explicit nulls; they must not override defaults."""
    config = InstallerConfig.from_dict({"enabled": True, "iss_path": None})
    assert config.enabled is True
    assert config.iss_path is None


def test_from_dict_rejects_unknown_key() -> None:
    with pytest.raises(ConfigurationError, match="unknown_option"):
        InstallerConfig.from_dict({"unknown_option": True})
