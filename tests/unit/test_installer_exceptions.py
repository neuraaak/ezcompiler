from __future__ import annotations

from ezcompiler.shared.exceptions import (
    EzCompilerError,
    InstallerBuildError,
    InstallerConfigError,
    InstallerError,
    InstallerTypeError,
    IsccNotFoundError,
)


def test_installer_error_is_ezcompiler_error() -> None:
    assert issubclass(InstallerError, EzCompilerError)


def test_installer_subclasses_are_installer_errors() -> None:
    for exc_cls in (
        InstallerTypeError,
        IsccNotFoundError,
        InstallerBuildError,
        InstallerConfigError,
    ):
        assert issubclass(exc_cls, InstallerError)


def test_installer_error_message() -> None:
    with __import__("pytest").raises(InstallerError, match="boom"):
        raise InstallerBuildError("boom")
