from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from ezcompiler.adapters._innosetup_installer import (
    ISCC_TIMEOUT_SECONDS,
    InnoSetupInstaller,
    detect_main_exe,
)
from ezcompiler.shared import InstallerConfig
from ezcompiler.shared.exceptions import InstallerBuildError, InstallerConfigError


def _bundle(tmp_path: Path, *exe_names: str) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    for name in exe_names or ("MyApp.exe",):
        (bundle / name).write_bytes(b"MZ")
    return bundle


def _extract_iss_path(message: str) -> str:
    for token in message.split():
        stripped = token.rstrip(".,;:)")
        if stripped.endswith(".iss"):
            return stripped
    raise AssertionError(f"no .iss path found in {message!r}")


@dataclass
class _IsccCall:
    argv: list[str]
    kwargs: dict[str, Any]


def _patch_subprocess(
    monkeypatch: pytest.MonkeyPatch,
    calls: list[_IsccCall],
    output_dir: Path,
    app_name: str = "MyApp",
    version: str = "1.2.3",
    returncode: int = 0,
) -> None:
    """Replace subprocess.run, record the call, and fake ISCC's output file."""

    def _fake_run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(_IsccCall(argv=list(argv), kwargs=dict(kwargs)))
        if returncode == 0:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{app_name}-{version}-setup.exe").write_bytes(b"MZ")
        return subprocess.CompletedProcess(
            args=argv, returncode=returncode, stdout=b"iscc says hi", stderr=b""
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)
    # ISCC resolution must not depend on the developer's machine.
    monkeypatch.setattr(shutil, "which", lambda _name: r"C:\Inno\ISCC.exe")


def _build(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    config: InstallerConfig | None = None,
    *,
    app_name: str = "MyApp",
    version: str = "1.2.3",
    exe_names: tuple[str, ...] = ("MyApp.exe",),
    returncode: int = 0,
    company_name: str = "",
    icon: str = "",
) -> tuple[Path, _IsccCall]:
    """Run one full build against a faked ISCC and return (setup_exe, call)."""
    bundle = _bundle(tmp_path, *exe_names)
    output_dir = tmp_path / "out"
    calls: list[_IsccCall] = []
    _patch_subprocess(monkeypatch, calls, output_dir, app_name, version, returncode)
    installer = InnoSetupInstaller(config or InstallerConfig(enabled=True))
    setup_exe = installer.build(
        bundle, app_name, version, output_dir, company_name=company_name, icon=icon
    )
    return setup_exe, calls[0]


# ////////////////////////////////////////////////
# MAIN EXE DETECTION
# ////////////////////////////////////////////////


def test_detect_main_exe_single_candidate(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path, "whatever.exe")
    assert detect_main_exe(bundle, "MyApp", "main.py") == "whatever.exe"


def test_detect_main_exe_prefers_project_name(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path, "helper.exe", "MyApp.exe")
    assert detect_main_exe(bundle, "MyApp", "main.py") == "MyApp.exe"


def test_detect_main_exe_falls_back_to_main_file_basename(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path, "helper.exe", "launcher.exe")
    assert detect_main_exe(bundle, "MyApp", "launcher.py") == "launcher.exe"


def test_detect_main_exe_raises_when_ambiguous(tmp_path: Path) -> None:
    """Defect 4 guard: never pick one at random — ISCC cannot detect the error."""
    bundle = _bundle(tmp_path, "one.exe", "two.exe")
    with pytest.raises(InstallerConfigError, match="main executable"):
        detect_main_exe(bundle, "MyApp", "main.py")


def test_detect_main_exe_raises_when_absent(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "data.txt").write_text("x", encoding="utf-8")
    with pytest.raises(InstallerConfigError, match="no executable"):
        detect_main_exe(bundle, "MyApp", "main.py")


# ////////////////////////////////////////////////
# ISCC COMMAND LINE
# ////////////////////////////////////////////////


def test_iscc_command_carries_the_five_volatile_defines(tmp_path, monkeypatch):
    _, call = _build(monkeypatch, tmp_path)
    argv = call.argv
    joined = " ".join(argv)
    assert "/Q" in argv
    assert "/DMyAppVersion=1.2.3" in joined
    assert "/DBundleDir=" in joined
    assert "/DOutputDir=" in joined
    assert "/DMainExe=MyApp.exe" in joined
    assert "/DVersionInfo=1.2.3.0" in joined


def test_iscc_command_quotes_paths_with_spaces(tmp_path, monkeypatch):
    """A /D value containing a space must reach ISCC as one argument."""
    bundle = tmp_path / "Program Files" / "bundle"
    bundle.mkdir(parents=True)
    (bundle / "MyApp.exe").write_bytes(b"MZ")
    output_dir = tmp_path / "out"
    calls: list[_IsccCall] = []
    _patch_subprocess(monkeypatch, calls, output_dir)
    installer = InnoSetupInstaller(InstallerConfig(enabled=True))
    installer.build(bundle, "MyApp", "1.2.3", output_dir)
    argv = calls[0].argv
    assert '/DBundleDir="' in " ".join(argv)


def test_iscc_command_includes_sign_tool_when_configured(tmp_path, monkeypatch):
    config = InstallerConfig(
        enabled=True, sign_tool_name="mytool", sign_tool_command="tool.exe $f"
    )
    _, call = _build(monkeypatch, tmp_path, config)
    argv = call.argv
    assert "/Smytool=tool.exe $f" in " ".join(argv)


def test_iscc_command_omits_sign_tool_when_absent(tmp_path, monkeypatch):
    _, call = _build(monkeypatch, tmp_path)
    argv = call.argv
    assert not any(arg.startswith("/S") for arg in argv)


def test_iscc_is_called_with_a_timeout(tmp_path, monkeypatch):
    _, call = _build(monkeypatch, tmp_path)
    assert call.kwargs["timeout"] == ISCC_TIMEOUT_SECONDS


# ////////////////////////////////////////////////
# ISS FILE LIFECYCLE
# ////////////////////////////////////////////////


def test_iss_is_written_with_a_bom(tmp_path, monkeypatch):
    """Defect 2 guard: ISCC only reads UTF-8 when a BOM is present.

    The ephemeral .iss is removed on success, so the build must fail to
    inspect the file that was actually written to disk.
    """
    calls: list[_IsccCall] = []
    output_dir = tmp_path / "out"
    bundle = _bundle(tmp_path, "MyApp.exe")
    _patch_subprocess(monkeypatch, calls, output_dir, returncode=2)
    installer = InnoSetupInstaller(InstallerConfig(enabled=True))
    with pytest.raises(InstallerBuildError):
        installer.build(bundle, "MyApp", "1.2.3", output_dir)
    kept_iss = Path(calls[0].argv[-1])
    written_bytes = kept_iss.read_bytes()
    assert written_bytes.startswith(b"\xef\xbb\xbf")


def test_ephemeral_iss_is_removed_on_success(tmp_path, monkeypatch):
    setup_exe, call = _build(monkeypatch, tmp_path)
    iss_path = Path(call.argv[-1])
    assert not iss_path.exists()


def test_company_name_changes_the_app_id(tmp_path, monkeypatch):
    """Defect 1 guard: the AppId GUID is derived from company_name.

    A build with a different company_name must render a different AppId,
    or two builds of the same product mint two AppIds — every install is
    then treated as a new, unrelated product.
    """
    empty_dir = tmp_path / "empty"
    acme_dir = tmp_path / "acme"
    empty_dir.mkdir()
    acme_dir.mkdir()
    with pytest.raises(InstallerBuildError) as excinfo_empty:
        _build(monkeypatch, empty_dir, returncode=2)
    with pytest.raises(InstallerBuildError) as excinfo_acme:
        _build(monkeypatch, acme_dir, returncode=2, company_name="ACME")
    iss_empty = Path(_extract_iss_path(str(excinfo_empty.value)))
    iss_acme = Path(_extract_iss_path(str(excinfo_acme.value)))
    app_id_empty = iss_empty.read_text(encoding="utf-8-sig")
    app_id_acme = iss_acme.read_text(encoding="utf-8-sig")
    assert app_id_empty != app_id_acme


def test_icon_reaches_the_script(tmp_path, monkeypatch):
    """A configured icon must not be silently dropped from the .iss."""
    with pytest.raises(InstallerBuildError) as excinfo:
        _build(monkeypatch, tmp_path, returncode=2, icon="myicon.ico")
    iss_text = Path(_extract_iss_path(str(excinfo.value))).read_text(
        encoding="utf-8-sig"
    )
    assert "SetupIconFile=myicon.ico" in iss_text


def test_ephemeral_iss_is_kept_on_failure(tmp_path, monkeypatch):
    """Without the script, 'ISCC failed (exit 2)' is undiagnosable."""
    bundle = _bundle(tmp_path)
    output_dir = tmp_path / "out"
    calls: list[_IsccCall] = []
    _patch_subprocess(monkeypatch, calls, output_dir, returncode=2)
    installer = InnoSetupInstaller(InstallerConfig(enabled=True))
    with pytest.raises(InstallerBuildError) as excinfo:
        installer.build(bundle, "MyApp", "1.2.3", output_dir)
    assert ".iss" in str(excinfo.value)
    assert Path(_extract_iss_path(str(excinfo.value))).exists()


def test_file_mode_does_not_render(tmp_path, monkeypatch):
    """With iss_path set, the user's script is the source of truth."""
    script = tmp_path / "custom.iss"
    script.write_text("; user script", encoding="utf-8")
    config = InstallerConfig(enabled=True, iss_path=script)
    _, call = _build(monkeypatch, tmp_path, config)
    assert script.read_text(encoding="utf-8") == "; user script"
    assert str(script) in call.argv


def test_file_mode_still_passes_volatile_defines(tmp_path, monkeypatch):
    script = tmp_path / "custom.iss"
    script.write_text("; user script", encoding="utf-8")
    config = InstallerConfig(enabled=True, iss_path=script)
    _, call = _build(monkeypatch, tmp_path, config)
    assert "/DMyAppVersion=1.2.3" in " ".join(call.argv)


# ////////////////////////////////////////////////
# ISCC RESOLUTION
# ////////////////////////////////////////////////


def test_explicit_iscc_path_is_used(tmp_path, monkeypatch):
    """Defect 4 guard: iscc_path was unreachable before v4.0.0."""
    fake = tmp_path / "ISCC.exe"
    fake.write_bytes(b"MZ")
    config = InstallerConfig(enabled=True, iscc_path=fake)
    _, call = _build(monkeypatch, tmp_path, config)
    assert call.argv[0] == str(fake)
