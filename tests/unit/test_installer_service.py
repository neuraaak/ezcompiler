from __future__ import annotations

import re
from pathlib import Path

import pytest

from ezcompiler.services.installer_service import InstallerService
from ezcompiler.shared import InstallerConfig
from ezcompiler.shared._compiler_config import CompilerConfig
from ezcompiler.shared.exceptions import InstallerConfigError


def _config(tmp_path: Path, icon: str = "") -> CompilerConfig:
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')")
    return CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        icon=icon,
    )


def test_build_installer_delegates_to_factory(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    class _FakeInstaller:
        def build(
            self,
            bundle_dir,
            app_name,
            version,
            output_dir,
            *,
            company_name="",
            icon="",
            main_file="",
        ):
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

    installer_config = InstallerConfig(publisher_url="https://example.com")
    result = InstallerService.build_installer(
        bundle_dir=tmp_path / "bundle",
        app_name="MyApp",
        version="1.0.0",
        output_dir=tmp_path / "installer",
        installer_config=installer_config,
    )

    assert result == tmp_path / "installer" / "MyApp-1.0.0-setup.exe"
    assert calls["create"] == ("innosetup", installer_config)
    assert calls["build"] == (
        tmp_path / "bundle",
        "MyApp",
        "1.0.0",
        tmp_path / "installer",
    )


def test_generate_iss_script_writes_the_file(tmp_path: Path) -> None:
    target = tmp_path / "installer" / "MyApp.iss"
    result = InstallerService.generate_iss_script(
        _config(tmp_path), target, force=False
    )
    assert result == target
    assert target.is_file()
    assert "#ifndef MyAppVersion" in target.read_text(encoding="utf-8-sig")


def test_generate_iss_script_refuses_to_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "MyApp.iss"
    target.write_text("; hand-edited", encoding="utf-8")
    with pytest.raises(InstallerConfigError, match="--force"):
        InstallerService.generate_iss_script(_config(tmp_path), target, force=False)
    assert target.read_text(encoding="utf-8") == "; hand-edited"


def test_generate_iss_script_overwrites_with_force(tmp_path: Path) -> None:
    target = tmp_path / "MyApp.iss"
    target.write_text("; hand-edited", encoding="utf-8")
    InstallerService.generate_iss_script(_config(tmp_path), target, force=True)
    assert "; hand-edited" not in target.read_text(encoding="utf-8-sig")


def test_generate_iss_script_warns_on_relative_icon(tmp_path, caplog) -> None:
    target = tmp_path / "MyApp.iss"
    with caplog.at_level("WARNING"):
        InstallerService.generate_iss_script(
            _config(tmp_path, icon="app.ico"), target, force=False
        )
    assert "app.ico" in caplog.text
    assert "relative" in caplog.text


def test_generate_iss_script_does_not_warn_on_absolute_icon(tmp_path, caplog) -> None:
    icon = tmp_path / "app.ico"
    target = tmp_path / "MyApp.iss"
    with caplog.at_level("WARNING"):
        InstallerService.generate_iss_script(
            _config(tmp_path, icon=str(icon)), target, force=False
        )
    assert "relative" not in caplog.text


def test_generated_script_resolves_the_app_id_inline(tmp_path: Path) -> None:
    """generate iss freezes the GUID: the file becomes the identity source."""
    target = tmp_path / "MyApp.iss"
    InstallerService.generate_iss_script(_config(tmp_path), target, force=False)
    content = target.read_text(encoding="utf-8-sig")
    app_id_line = next(
        line for line in content.splitlines() if line.startswith("AppId=")
    )
    assert re.search(r"\{[0-9A-F-]{36}\}", app_id_line)
