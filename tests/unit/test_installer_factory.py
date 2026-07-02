from __future__ import annotations

import pytest

from ezcompiler.adapters.installer_factory import InstallerFactory
from ezcompiler.shared.exceptions import InstallerTypeError
from ezcompiler.types import InstallerPort


def test_create_innosetup_installer() -> None:
    installer = InstallerFactory.create_installer("innosetup")
    assert isinstance(installer, InstallerPort)
    assert installer.get_installer_name() == "InnoSetup"


def test_unknown_type_raises() -> None:
    with pytest.raises(InstallerTypeError):
        InstallerFactory.create_installer("nsis")


def test_supported_types() -> None:
    assert InstallerFactory.get_supported_types() == ["innosetup"]
