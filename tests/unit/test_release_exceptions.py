from __future__ import annotations

import pytest

from ezcompiler.shared.exceptions import (
    BundleBuildError,
    EzCompilerError,
    ReleaseConfigError,
    ReleaseError,
    ReleaserTypeError,
    SigningKeyError,
)


@pytest.mark.parametrize(
    "exc",
    [ReleaserTypeError, BundleBuildError, SigningKeyError, ReleaseConfigError],
)
def test_release_subclasses_are_caught_by_release_error(
    exc: type[ReleaseError],
) -> None:
    with pytest.raises(ReleaseError):
        raise exc("boom")


def test_release_error_is_ezcompiler_error() -> None:
    assert issubclass(ReleaseError, EzCompilerError)
