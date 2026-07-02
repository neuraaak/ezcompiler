from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.adapters.base_installer import BaseInstaller
from ezcompiler.shared.exceptions import InstallerConfigError


class _ConcreteInstaller(BaseInstaller):
    def build(
        self, bundle_dir: Path, app_name: str, version: str, output_dir: Path
    ) -> Path:
        self._validate_bundle_dir(bundle_dir)
        return output_dir / f"{app_name}-{version}-setup.exe"

    def get_installer_name(self) -> str:
        return "Concrete"


def test_validate_bundle_dir_raises_when_missing(tmp_path: Path) -> None:
    installer = _ConcreteInstaller()
    with pytest.raises(InstallerConfigError, match="does not exist"):
        installer.build(tmp_path / "absent", "App", "1.0.0", tmp_path)


def test_validate_bundle_dir_raises_when_empty(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    installer = _ConcreteInstaller()
    with pytest.raises(InstallerConfigError, match="empty"):
        installer.build(bundle, "App", "1.0.0", tmp_path)


def test_validate_bundle_dir_passes_when_populated(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "app.exe").write_bytes(b"x")
    installer = _ConcreteInstaller()
    result = installer.build(bundle, "App", "1.0.0", tmp_path)
    assert result == tmp_path / "App-1.0.0-setup.exe"
