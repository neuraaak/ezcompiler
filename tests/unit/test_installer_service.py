from __future__ import annotations

from pathlib import Path

from ezcompiler.services.installer_service import InstallerService


def test_build_installer_delegates_to_factory(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    class _FakeInstaller:
        def build(self, bundle_dir, app_name, version, output_dir):
            calls["build"] = (bundle_dir, app_name, version, output_dir)
            return output_dir / f"{app_name}-{version}-setup.exe"

        def get_installer_name(self):
            return "Fake"

    def _fake_create(installer_type, config=None):
        calls["create"] = (installer_type, config)
        return _FakeInstaller()

    monkeypatch.setattr(
        "ezcompiler.services.installer_service.InstallerFactory.create_installer",
        _fake_create,
    )

    result = InstallerService.build_installer(
        bundle_dir=tmp_path / "bundle",
        app_name="MyApp",
        version="1.0.0",
        output_dir=tmp_path / "installer",
        installer_config={"icon": "app.ico"},
    )

    assert result == tmp_path / "installer" / "MyApp-1.0.0-setup.exe"
    assert calls["create"] == ("innosetup", {"icon": "app.ico"})
    assert calls["build"] == (
        tmp_path / "bundle",
        "MyApp",
        "1.0.0",
        tmp_path / "installer",
    )
