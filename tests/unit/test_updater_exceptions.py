from __future__ import annotations

import pytest

from ezcompiler import EzCompilerError, UpdaterError
from ezcompiler.shared.exceptions import UpdaterConfigError, UpdaterGenerationError


def test_updater_error_is_ezcompiler_error() -> None:
    assert issubclass(UpdaterError, EzCompilerError)


def test_updater_config_error_is_updater_error() -> None:
    assert issubclass(UpdaterConfigError, UpdaterError)


def test_updater_generation_error_is_updater_error() -> None:
    assert issubclass(UpdaterGenerationError, UpdaterError)


def test_updater_errors_are_raiseable() -> None:
    with pytest.raises(UpdaterConfigError):
        raise UpdaterConfigError("config invalid")
    with pytest.raises(UpdaterGenerationError):
        raise UpdaterGenerationError("write failed")
