from __future__ import annotations

from ezcompiler.shared.exceptions import (
    EzCompilerError,
    PublishAuthError,
    PublishCliError,
    PublishError,
    PublisherTypeError,
)


def test_publish_error_derives_from_ezcompiler_error() -> None:
    assert issubclass(PublishError, EzCompilerError)


def test_publish_subclasses_derive_from_publish_error() -> None:
    for exc in (PublisherTypeError, PublishCliError, PublishAuthError):
        assert issubclass(exc, PublishError)


def test_publish_error_carries_its_message() -> None:
    assert "gh not found" in str(PublishCliError("gh not found"))
