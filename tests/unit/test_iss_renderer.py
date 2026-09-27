# ///////////////////////////////////////////////////////////////
# TEST_ISS_RENDERER - .iss rendering, escaping and helpers
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Tests for the Jinja2-based .iss renderer, its filter and pure helpers."""

from __future__ import annotations

import pytest

from ezcompiler.adapters._iss_renderer import (
    escape_iss,
    resolve_app_id,
    sanitize_version_info,
)

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
    """Regression guard for defect 1: the AppId must not vary per build."""
    assert resolve_app_id(None, "ACME", "MyApp") == resolve_app_id(
        None, "ACME", "MyApp"
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
