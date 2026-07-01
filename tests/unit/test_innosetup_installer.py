from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ezcompiler.adapters._innosetup_installer import InnoSetupInstaller
from ezcompiler.shared.exceptions import (
    InstallerBuildError,
    InstallerConfigError,
    IsccNotFoundError,
)


def _make_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "MyApp"
    bundle.mkdir()
    (bundle / "MyApp.exe").write_bytes(b"binary")
    return bundle


def test_build_raises_when_bundle_missing(tmp_path: Path) -> None:
    installer = InnoSetupInstaller({"iscc_path": tmp_path / "ISCC.exe"})
    with pytest.raises(InstallerConfigError, match="does not exist"):
        installer.build(tmp_path / "absent", "MyApp", "1.0.0", tmp_path / "out")


def test_build_raises_when_iscc_not_found(monkeypatch, tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path)
    monkeypatch.setattr(InnoSetupInstaller, "_find_iscc", lambda _self: None)
    installer = InnoSetupInstaller()
    with pytest.raises(IsccNotFoundError, match="jrsoftware.org"):
        installer.build(bundle, "MyApp", "1.0.0", tmp_path / "out")


def test_build_raises_when_override_iss_path_missing(tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path)
    installer = InnoSetupInstaller(
        {"iscc_path": tmp_path / "ISCC.exe", "iss_path": tmp_path / "custom.iss"}
    )
    with pytest.raises(InstallerConfigError, match="custom.iss"):
        installer.build(bundle, "MyApp", "1.0.0", tmp_path / "out")


def test_build_runs_iscc_and_returns_setup_path(monkeypatch, tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path)
    output_dir = tmp_path / "out"
    fake_iscc = tmp_path / "ISCC.exe"
    fake_iscc.write_bytes(b"fake")

    calls: dict[str, object] = {}

    def _fake_run(cmd, **_kwargs):
        calls["cmd"] = cmd
        # Simulate ISCC producing the setup.exe in OutputDir
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "MyApp-1.0.0-setup.exe").write_bytes(b"setup")
        return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    installer = InnoSetupInstaller({"iscc_path": fake_iscc})
    result = installer.build(bundle, "MyApp", "1.0.0", output_dir)

    assert result == output_dir / "MyApp-1.0.0-setup.exe"
    assert str(fake_iscc) in calls["cmd"][0]


def test_build_raises_installer_build_error_on_nonzero_exit(
    monkeypatch, tmp_path: Path
) -> None:
    bundle = _make_bundle(tmp_path)
    fake_iscc = tmp_path / "ISCC.exe"
    fake_iscc.write_bytes(b"fake")

    def _fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(
            cmd, returncode=1, stdout=b"", stderr=b"syntax error"
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)

    installer = InnoSetupInstaller({"iscc_path": fake_iscc})
    with pytest.raises(InstallerBuildError, match="syntax error"):
        installer.build(bundle, "MyApp", "1.0.0", tmp_path / "out")


def test_build_raises_installer_build_error_when_output_missing(
    monkeypatch, tmp_path: Path
) -> None:
    bundle = _make_bundle(tmp_path)
    output_dir = tmp_path / "out"
    fake_iscc = tmp_path / "ISCC.exe"
    fake_iscc.write_bytes(b"fake")

    def _fake_run(cmd, **_kwargs):
        # ISCC "succeeds" but does not produce the expected setup.exe
        # (e.g. a custom iss_path with a different OutputBaseFilename).
        return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    installer = InnoSetupInstaller({"iscc_path": fake_iscc})
    with pytest.raises(InstallerBuildError, match="not found"):
        installer.build(bundle, "MyApp", "1.0.0", output_dir)


def test_get_installer_name() -> None:
    assert InnoSetupInstaller().get_installer_name() == "InnoSetup"
