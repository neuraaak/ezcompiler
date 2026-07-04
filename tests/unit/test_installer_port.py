from __future__ import annotations

from pathlib import Path

from ezcompiler._types import InstallerPort


class _FakeInstaller:
    def build(
        self, bundle_dir: Path, app_name: str, version: str, output_dir: Path
    ) -> Path:
        return output_dir / f"{app_name}-{version}-setup.exe"

    def get_installer_name(self) -> str:
        return "Fake"


class _NotAnInstaller:
    def get_installer_name(self) -> str:
        return "Nope"


def test_conforming_class_satisfies_port() -> None:
    assert isinstance(_FakeInstaller(), InstallerPort)


def test_non_conforming_class_does_not_satisfy_port() -> None:
    assert not isinstance(_NotAnInstaller(), InstallerPort)
