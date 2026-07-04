from __future__ import annotations

import pytest

from ezcompiler._types import ReleaserPort
from ezcompiler.adapters.releaser_factory import ReleaserFactory
from ezcompiler.shared.exceptions import ReleaserTypeError


def test_create_tufup_releaser() -> None:
    releaser = ReleaserFactory.create_releaser("tufup")
    assert isinstance(releaser, ReleaserPort)
    assert releaser.get_releaser_name() == "Tufup"


def test_unknown_type_raises() -> None:
    with pytest.raises(ReleaserTypeError):
        ReleaserFactory.create_releaser("github")


def test_supported_types() -> None:
    assert ReleaserFactory.get_supported_types() == ["tufup"]
