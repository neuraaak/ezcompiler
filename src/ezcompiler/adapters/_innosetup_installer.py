# ///////////////////////////////////////////////////////////////
# INNOSETUP_INSTALLER - Inno Setup installer adapter
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Inno Setup installer - Adapter building a Windows setup.exe from a compiled
bundle via the external ``ISCC.exe`` binary (Inno Setup 6).

The ``.iss`` script is rendered once from ``InstallerConfig`` via
``_iss_renderer.render_iss`` (committable, version-independent). Volatile
values — version, bundle/output paths, and the detected main executable —
are never baked into the script: they reach ISCC as ``/D`` command-line
defines, computed fresh on every build.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..shared.exceptions import (
    InstallerBuildError,
    InstallerConfigError,
    IsccNotFoundError,
)
from ._iss_renderer import render_iss, sanitize_version_info
from .base_installer import BaseInstaller

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_ISDL_URL = "https://jrsoftware.org/isdl.php"

# A hung ISCC process must not freeze the build pipeline indefinitely.
ISCC_TIMEOUT_SECONDS = 600

_logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def detect_main_exe(bundle_dir: Path, project_name: str, main_file: str) -> str:
    """Detect the main executable at the root of the compiled bundle.

    Never guesses among several candidates: ISCC cannot itself detect that
    the wrong one was picked, so an ambiguous bundle raises instead of
    silently choosing one at random.

    Args:
        bundle_dir: Directory containing the compiled application.
        project_name: Project name; preferred candidate is
            ``f"{project_name}.exe"``.
        main_file: Entry-point script; fallback candidate is its stem
            with a ``.exe`` extension.

    Returns:
        str: The detected executable's file name.

    Raises:
        InstallerConfigError: If the bundle has no executable, or several
            are present and none matches the project name or main file.
    """
    candidates = sorted(p.name for p in bundle_dir.glob("*.exe"))
    if not candidates:
        raise InstallerConfigError(
            f"Bundle directory contains no executable: {bundle_dir}"
        )
    if len(candidates) == 1:
        return candidates[0]

    project_candidate = f"{project_name}.exe"
    if project_candidate in candidates:
        return project_candidate

    main_file_candidate = f"{Path(main_file).stem}.exe"
    if main_file_candidate in candidates:
        return main_file_candidate

    raise InstallerConfigError(
        f"cannot determine the main executable among {candidates}; "
        "place a single .exe at the bundle root"
    )


# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class InnoSetupInstaller(BaseInstaller):
    """Installer backed by the Inno Setup compiler (ISCC.exe)."""

    # ////////////////////////////////////////////////
    # BUILD
    # ////////////////////////////////////////////////

    def build(
        self, bundle_dir: Path, app_name: str, version: str, output_dir: Path
    ) -> Path:
        """Detect the main executable, resolve the .iss, and compile it."""
        self._validate_bundle_dir(bundle_dir)
        main_exe = detect_main_exe(bundle_dir, app_name, app_name)

        iscc_path = self._config.iscc_path or self._find_iscc()
        if not iscc_path:
            raise IsccNotFoundError(
                "ISCC.exe (Inno Setup 6) not found in PATH or default install "
                f"locations. Download it from {_ISDL_URL}."
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        iss_path, tmp_dir = self._resolve_iss_path(app_name)

        argv = self._build_argv(
            iscc_path, iss_path, version, bundle_dir, output_dir, main_exe
        )

        # No try/finally around this call: the temporary .iss must survive
        # any failure (including a timeout) so it can still be inspected —
        # only the success path below removes it.
        result = subprocess.run(
            argv,
            capture_output=True,
            check=False,
            timeout=ISCC_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            stdout = result.stdout.decode("utf-8", errors="replace")
            raise InstallerBuildError(
                f"ISCC.exe failed (exit {result.returncode}): {stderr or stdout} "
                f"(script kept at {iss_path})"
            )

        _logger.debug(
            "ISCC.exe succeeded: %s",
            result.stdout.decode("utf-8", errors="replace"),
        )
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        setup_exe = output_dir / f"{app_name}-{version}-setup.exe"
        if not setup_exe.is_file():
            raise InstallerBuildError(
                f"ISCC.exe succeeded but expected installer not found at {setup_exe}. "
                "If using a custom iss_path, ensure its OutputBaseFilename "
                f"matches '{app_name}-{version}-setup'."
            )
        return setup_exe

    # ////////////////////////////////////////////////
    # ISS RESOLUTION
    # ////////////////////////////////////////////////

    def _resolve_iss_path(self, app_name: str) -> tuple[Path, str | None]:
        """Return the .iss path to compile, and its temp dir if ephemeral.

        In file mode (``config.iss_path`` set), the user's script is the
        source of truth and is never rendered or written. Otherwise the
        script is rendered from ``InstallerConfig`` and written as an
        ephemeral ``utf-8-sig`` file — ISCC only reads UTF-8 with a BOM.
        """
        if self._config.iss_path is not None:
            return self._config.iss_path, None

        iss_text = render_iss(
            self._config,
            project_name=app_name,
            company_name=app_name,
            icon="",
            standalone=False,
        )
        tmp_dir = tempfile.mkdtemp()
        iss_path = Path(tmp_dir) / f"{app_name}.iss"
        iss_path.write_text(iss_text, encoding="utf-8-sig")
        return iss_path, tmp_dir

    # ////////////////////////////////////////////////
    # ISCC COMMAND LINE
    # ////////////////////////////////////////////////

    def _build_argv(
        self,
        iscc_path: Path,
        iss_path: Path,
        version: str,
        bundle_dir: Path,
        output_dir: Path,
        main_exe: str,
    ) -> list[str]:
        """Build the ISCC argv, quoting each ``/D`` value as one argument.

        Passing a list to ``subprocess.run`` (never ``shell=True``) does not
        dispense with quoting: ISCC re-parses the ``/D`` value itself, so a
        value containing a space must still be wrapped in quotes.
        """

        def _define(name: str, value: str) -> str:
            if " " in value:
                return f'/D{name}="{value}"'
            return f"/D{name}={value}"

        argv = [
            str(iscc_path),
            "/Q",
            _define("MyAppVersion", version),
            _define("BundleDir", str(bundle_dir.resolve())),
            _define("OutputDir", str(output_dir.resolve())),
            _define("MainExe", main_exe),
            _define("VersionInfo", sanitize_version_info(version)),
        ]
        if self._config.sign_tool_name:
            argv.append(
                f"/S{self._config.sign_tool_name}={self._config.sign_tool_command}"
            )
        argv.append(str(iss_path))
        return argv

    # ////////////////////////////////////////////////
    # ISCC DETECTION
    # ////////////////////////////////////////////////

    def _find_iscc(self) -> Path | None:
        """Locate ISCC.exe in PATH, then default install locations."""
        found = shutil.which("ISCC.exe") or shutil.which("ISCC")
        if found:
            return Path(found)

        for env_var in ("ProgramFiles(x86)", "ProgramFiles"):
            base = os.environ.get(env_var)
            if not base:
                continue
            candidate = Path(base) / "Inno Setup 6" / "ISCC.exe"
            if candidate.is_file():
                return candidate

        return None

    # ////////////////////////////////////////////////
    # METADATA
    # ////////////////////////////////////////////////

    def get_installer_name(self) -> str:
        return "InnoSetup"
