# ///////////////////////////////////////////////////////////////
# TEST_ISS_RENDERER - .iss rendering, escaping and helpers
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Tests for the Jinja2-based .iss renderer, its filter and pure helpers."""

from __future__ import annotations

from pathlib import Path, PureWindowsPath

import pytest

from ezcompiler.adapters._iss_renderer import (
    escape_iss,
    render_iss,
    resolve_app_id,
    sanitize_version_info,
)
from ezcompiler.shared import InstallerConfig
from ezcompiler.shared.exceptions import InstallerRenderError

FIXTURES = Path(__file__).parent.parent / "fixtures" / "iss"

# ////////////////////////////////////////////////
# ESCAPING
# ////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("MyApp", "MyApp"),
        ("My{App}", "My{{App}"),
        ("{autopf}", "{{autopf}"),
        ("a{b{c", "a{{b{{c"),
        ("closes}here", "closes}here"),
    ],
)
def test_escape_iss_doubles_braces(raw: str, expected: str) -> None:
    """Inno treats '{{' as a literal brace; a bare '{' opens a constant.

    '}' has no special meaning in Inno syntax and is left untouched.
    """
    assert escape_iss(raw) == expected


@pytest.mark.parametrize("raw", ['My"App', "line\nbreak", "tab\there", "cr\rhere"])
def test_escape_iss_rejects_breaking_characters(raw: str) -> None:
    """A quote or newline would truncate or split the generated directive."""
    with pytest.raises(ValueError, match="invalid character"):
        escape_iss(raw)


def test_escape_iss_handles_the_audit_regression_case() -> None:
    """Regression guard for defect 3 of the audit."""
    assert escape_iss("My{App}X") == "My{{App}X"


# ////////////////////////////////////////////////
# APP ID
# ////////////////////////////////////////////////


def test_resolve_app_id_is_deterministic() -> None:
    first = resolve_app_id(None, "ACME", "MyApp")
    second = resolve_app_id(None, "ACME", "MyApp")
    assert first == second


def test_resolve_app_id_is_version_independent() -> None:
    """Regression guard for defect 1: the AppId must not vary per build.

    ``resolve_app_id`` takes no version parameter, so the derivation for a
    given (company, project) pair is pinned to a hard-coded expected value:
    any future change that folds a version (or anything else) into the
    derivation changes this UUID5 and fails this test loudly.
    """
    assert (
        resolve_app_id(None, "ACME", "MyApp")
        == "{E7A0F07C-6E64-5CEC-92F0-53BF1DB423A4}"
    )


def test_resolve_app_id_differs_per_project() -> None:
    assert resolve_app_id(None, "ACME", "AppOne") != resolve_app_id(
        None, "ACME", "AppTwo"
    )


def test_resolve_app_id_differs_per_company() -> None:
    assert resolve_app_id(None, "ACME", "MyApp") != resolve_app_id(
        None, "OTHER", "MyApp"
    )


def test_resolve_app_id_is_braced_guid() -> None:
    app_id = resolve_app_id(None, "ACME", "MyApp")
    assert app_id.startswith("{") and app_id.endswith("}")
    assert len(app_id) == 38


def test_resolve_app_id_honours_explicit_value() -> None:
    explicit = "{A1B2C3D4-1111-2222-3333-444455556666}"
    assert resolve_app_id(explicit, "ACME", "MyApp") == explicit


# ////////////////////////////////////////////////
# VERSION INFO
# ////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.2.3", "1.2.3.0"),
        ("1.2.3.4", "1.2.3.4"),
        ("1.2", "1.2.0.0"),
        ("1", "1.0.0.0"),
        ("1.2.0-rc1", "1.2.0.0"),
        ("v1.2.0", "1.2.0.0"),
        ("1.2.0+build5", "1.2.0.0"),
        ("2026.09.27", "2026.9.27.0"),
    ],
)
def test_sanitize_version_info(version: str, expected: str) -> None:
    """Inno's VersionInfoVersion requires a numeric quadruplet."""
    assert sanitize_version_info(version) == expected


def test_sanitize_version_info_rejects_unusable_input() -> None:
    with pytest.raises(ValueError, match="version"):
        sanitize_version_info("nightly")


# ////////////////////////////////////////////////
# RENDERING
# ////////////////////////////////////////////////


def _render(config: InstallerConfig, *, standalone: bool = False) -> str:
    return render_iss(
        config,
        project_name="MyApp",
        company_name="ACME Corp",
        icon="",
        standalone=standalone,
    )


def test_volatile_values_are_never_hardcoded() -> None:
    """Version and build paths must arrive via ISCC /D, never be written in."""
    rendered = _render(InstallerConfig(enabled=True))
    assert "AppVersion={#MyAppVersion}" in rendered
    assert r'Source: "{#BundleDir}\*"' in rendered
    assert "OutputDir={#OutputDir}" in rendered


def test_app_id_is_version_independent() -> None:
    """Regression guard for defect 1."""
    rendered = _render(InstallerConfig(enabled=True))
    app_id_line = next(
        line for line in rendered.splitlines() if line.startswith("AppId=")
    )
    assert "{#MyAppVersion}" not in app_id_line
    assert "MyAppVersion" not in app_id_line


def test_app_id_has_the_doubled_leading_brace_inno_requires() -> None:
    """A literal GUID AppId needs a doubled opening brace and a single
    closing one ('{{GUID}'): a bare '{GUID}' is read by ISCC as a
    reference to a constant named GUID, not as a literal value."""
    rendered = _render(InstallerConfig(enabled=True))
    app_id_line = next(
        line for line in rendered.splitlines() if line.startswith("AppId=")
    )
    assert app_id_line.startswith("AppId={{")
    assert not app_id_line.startswith("AppId={{{")
    assert app_id_line.endswith("}")
    assert not app_id_line.endswith("}}")


def test_explicit_app_id_also_gets_the_doubled_leading_brace() -> None:
    rendered = render_iss(
        InstallerConfig(enabled=True, app_id="{A1B2C3D4-1111-2222-3333-444455556666}"),
        project_name="MyApp",
        company_name="ACME Corp",
        icon="",
        standalone=False,
    )
    app_id_line = next(
        line for line in rendered.splitlines() if line.startswith("AppId=")
    )
    assert app_id_line == "AppId={{A1B2C3D4-1111-2222-3333-444455556666}"


def test_user_values_are_escaped() -> None:
    """Regression guard for defect 3: a brace in a name must be doubled."""
    rendered = render_iss(
        InstallerConfig(enabled=True),
        project_name="My{App}X",
        company_name="ACME",
        icon="",
        standalone=False,
    )
    # escape_iss doubles only the opening brace (see its docstring): '}' is
    # left untouched, so "My{App}X" becomes "My{{App}X", not "My{{App}}X".
    assert '#define MyAppName "My{{App}X"' in rendered
    # OutputBaseFilename does not expand runtime constants: applying the
    # same escape there creates a different filename on disk.
    assert "OutputBaseFilename=My{App}X-{#MyAppVersion}-setup" in rendered


def test_per_user_switches_directory_and_privileges() -> None:
    rendered = _render(InstallerConfig(enabled=True, per_user=True))
    assert r"DefaultDirName={localappdata}\Programs" in rendered
    assert "PrivilegesRequired=lowest" in rendered


def test_add_to_path_emits_a_registry_section() -> None:
    rendered = _render(InstallerConfig(enabled=True, add_to_path=True))
    assert "[Registry]" in rendered
    assert "Path" in rendered


def test_add_to_path_guards_against_duplicate_entries() -> None:
    """Without a Check, every reinstall re-appends {app} to the user's Path
    and Windows' Environment\\Path eventually truncates."""
    rendered = _render(InstallerConfig(enabled=True, add_to_path=True))
    registry = next(
        line for line in rendered.splitlines() if line.startswith("Root: HKCU")
    )
    assert "Check: NeedsAddPath(" in registry
    assert "function NeedsAddPath(" in rendered


def test_add_to_path_removes_its_entry_on_uninstall() -> None:
    """The entry must be surgically removed, never via uninsdeletevalue —
    that flag would wipe the user's entire Environment\\Path."""
    rendered = _render(InstallerConfig(enabled=True, add_to_path=True))
    registry = next(
        line for line in rendered.splitlines() if line.startswith("Root: HKCU")
    )
    assert "uninsdeletevalue" not in registry
    assert "procedure CurUninstallStepChanged(" in rendered
    assert "RegWriteExpandStringValue(" in rendered


def test_add_to_path_merges_its_code_helper_with_user_code() -> None:
    """A user [Code] section and the PATH helper must share one header —
    two [Code] headers is not a script ISCC accepts."""
    rendered = _render(
        InstallerConfig(
            enabled=True,
            add_to_path=True,
            extra_sections={"Code": ["procedure Foo; begin end;"]},
        )
    )
    assert rendered.count("[Code]") == 1
    assert "function NeedsAddPath(" in rendered
    assert "procedure Foo; begin end;" in rendered


def test_add_to_path_omits_the_registry_section_when_off() -> None:
    rendered = _render(InstallerConfig(enabled=True, add_to_path=False))
    assert "[Registry]" not in rendered


def test_languages_are_emitted_in_order() -> None:
    rendered = _render(InstallerConfig(enabled=True, languages=["french", "english"]))
    lines = [line for line in rendered.splitlines() if line.startswith('Name: "')]
    assert "french" in lines[0]
    assert "english" in lines[1]


def test_sign_tool_is_absent_from_the_script() -> None:
    """Signing is passed to ISCC via /S, never written into the .iss."""
    rendered = _render(
        InstallerConfig(
            enabled=True, sign_tool_name="mytool", sign_tool_command="tool.exe $f"
        )
    )
    assert "tool.exe" not in rendered
    assert "SignTool=mytool" in rendered


def test_extra_sections_are_appended() -> None:
    rendered = _render(
        InstallerConfig(
            enabled=True, extra_sections={"Code": ["procedure Foo; begin end;"]}
        )
    )
    assert "[Code]" in rendered
    assert "procedure Foo; begin end;" in rendered


def test_standalone_mode_emits_ifndef_defaults() -> None:
    rendered = _render(InstallerConfig(enabled=True), standalone=True)
    assert "#ifndef MyAppVersion" in rendered
    assert "#define MyAppVersion" in rendered


def test_ephemeral_mode_omits_ifndef_defaults() -> None:
    rendered = _render(InstallerConfig(enabled=True), standalone=False)
    assert "#ifndef" not in rendered


def test_undefined_template_variable_raises_render_error(monkeypatch) -> None:
    """StrictUndefined must turn a template slip into an explicit failure."""
    from ezcompiler.adapters import _iss_renderer

    monkeypatch.setattr(_iss_renderer, "_TEMPLATE_NAME", "does-not-exist.jinja")
    with pytest.raises(InstallerRenderError):
        _render(InstallerConfig(enabled=True))


def test_escaping_failure_names_the_offending_field() -> None:
    """InstallerRenderError must say which field carried the bad value."""
    with pytest.raises(InstallerRenderError, match="sign_tool_name"):
        _render(
            InstallerConfig(
                enabled=True,
                sign_tool_name='bad"tool',
                sign_tool_command="tool.exe $f",
            )
        )


# ////////////////////////////////////////////////
# GOLDEN FILES
# ////////////////////////////////////////////////


def _golden(name: str) -> str:
    return (FIXTURES / f"{name}.iss").read_text(encoding="utf-8")


def test_golden_defaults() -> None:
    assert _render(InstallerConfig(enabled=True)) == _golden("defaults")


def test_golden_per_user() -> None:
    config = InstallerConfig(enabled=True, per_user=True, add_to_path=True)
    assert _render(config) == _golden("per_user")


def test_golden_full() -> None:
    config = InstallerConfig(
        enabled=True,
        app_id="{A1B2C3D4-1111-2222-3333-444455556666}",
        publisher_url="https://acme.example",
        support_url="https://acme.example/support",
        updates_url="https://acme.example/updates",
        architecture="x64",
        desktop_icon=True,
        start_menu_group="ACME Tools",
        launch_after_install=True,
        add_to_path=True,
        close_running_app=True,
        uninstall_delete=[r"{app}\cache"],
        languages=["english", "french"],
        wizard_style="modern",
        compression="lzma2/max",
        sign_tool_name="mytool",
        sign_tool_command="tool.exe $f",
    )
    assert _render(config) == _golden("full")


def test_golden_extras() -> None:
    config = InstallerConfig(
        enabled=True,
        extra_setup_directives={"AppCopyright": "(c) 2026 ACME"},
        extra_sections={"Code": ["procedure Foo;", "begin", "end;"]},
    )
    assert _render(config) == _golden("extras")


def test_golden_standalone() -> None:
    assert _render(InstallerConfig(enabled=True), standalone=True) == _golden(
        "standalone"
    )


def test_golden_advanced() -> None:
    """Covers the three branches no other golden config exercises:
    icon set, license_file set, architecture="auto" (which omits both
    ArchitecturesAllowed and ArchitecturesInstallIn64BitMode)."""
    license_file = Path("tests/fixtures/iss/LICENSE.txt")
    config = InstallerConfig(
        enabled=True,
        architecture="auto",
        license_file=license_file,
    )
    rendered = render_iss(
        config,
        project_name="MyApp",
        company_name="ACME Corp",
        icon="assets/icon.ico",
        standalone=False,
    )
    # The golden holds a Windows-style LicenseFile; str(Path) uses the host
    # separator, so rebuild that one line for the OS the test runs on.
    # Production never hits this: the installer absolutizes license_file
    # before rendering.
    golden = _golden("advanced")
    windows_line = f"LicenseFile={PureWindowsPath(license_file)}"
    assert windows_line in golden
    expected = golden.replace(windows_line, f"LicenseFile={license_file}")
    assert rendered == expected
