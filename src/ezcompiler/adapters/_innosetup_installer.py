# ///////////////////////////////////////////////////////////////
# INNOSETUP_INSTALLER - Inno Setup installer adapter
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Inno Setup installer - Adapter building a Windows setup.exe from a compiled
bundle via the external ``ISCC.exe`` binary (Inno Setup 6).

No PyPI dependency: the ``.iss`` script is rendered from ezcompiler's own
template using the project's ``#PLACEHOLDER#`` string-substitution
convention, then compiled by shelling out to ISCC.exe.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import os
import shutil
import subprocess
from pathlib import Path

from ..shared.exceptions import (
    InstallerBuildError,
    InstallerConfigError,
    IsccNotFoundError,
)
from .base_installer import BaseInstaller

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_TEMPLATE_PATH = (
    Path(__file__).parent.parent
    / "assets"
    / "templates"
    / "installer"
    / "setup.iss.template"
)
_ISDL_URL = "https://jrsoftware.org/isdl.php"

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
        """Render the .iss script and compile it into a setup.exe."""
        self._validate_bundle_dir(bundle_dir)

        iscc_path = self._config.get("iscc_path") or self._find_iscc()
        if not iscc_path:
            raise IsccNotFoundError(
                "ISCC.exe (Inno Setup 6) not found in PATH or default install "
                f"locations. Download it from {_ISDL_URL}."
            )

        iss_content = self._render_iss(bundle_dir, app_name, version, output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        iss_path = output_dir / f"{app_name}.iss"
        iss_path.write_text(iss_content, encoding="utf-8")

        result = subprocess.run(
            [str(iscc_path), str(iss_path)],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            stdout = result.stdout.decode("utf-8", errors="replace")
            raise InstallerBuildError(
                f"ISCC.exe failed (exit {result.returncode}): {stderr or stdout}"
            )

        setup_exe = output_dir / f"{app_name}-{version}-setup.exe"
        if not setup_exe.is_file():
            raise InstallerBuildError(
                f"ISCC.exe succeeded but expected installer not found at {setup_exe}. "
                "If using a custom installer_iss_path, ensure its OutputBaseFilename "
                f"matches '{app_name}-{version}-setup'."
            )
        return setup_exe

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
    # TEMPLATE RENDERING
    # ////////////////////////////////////////////////

    def _render_iss(
        self, bundle_dir: Path, app_name: str, version: str, output_dir: Path
    ) -> str:
        """Render the .iss script content from the template or a user override."""
        iss_path_override = self._config.get("iss_path")
        if iss_path_override is not None:
            iss_path_override = Path(iss_path_override)
            if not iss_path_override.is_file():
                raise InstallerConfigError(
                    f"installer_iss_path not found: {iss_path_override}"
                )
            template = iss_path_override.read_text(encoding="utf-8")
        else:
            template = _TEMPLATE_PATH.read_text(encoding="utf-8")

        # ISCC resolves relative paths against the .iss file's own directory
        # (output_dir), not the process cwd — so a relative icon path would be
        # looked up in the wrong place and fail with exit 2. Absolutize against
        # cwd, matching how compilers consume config.icon.
        icon = self._config.get("icon", "")
        icon_line = f"SetupIconFile={Path(icon).resolve()}" if icon else ""
        company_name = self._config.get("company_name", app_name)
        main_exe = self._config.get("main_exe", f"{app_name}.exe")

        # Per-user install (no admin rights, %LOCALAPPDATA%\Programs) is
        # required for tufup in-place auto-update, which cannot self-elevate
        # to overwrite a Program Files install.
        per_user = self._config.get("per_user", False)
        default_dir = (
            r"{localappdata}\Programs\{#MyAppName}"
            if per_user
            else r"{autopf}\{#MyAppName}"
        )
        privileges_required = "lowest" if per_user else "admin"

        replacements = {
            "#APP_NAME#": app_name,
            "#VERSION#": version,
            "#COMPANY_NAME#": company_name,
            # ISCC resolves relative paths against the .iss file's own
            # directory (output_dir), not the process cwd — must be absolute.
            "#BUNDLE_DIR#": str(bundle_dir.resolve()),
            "#OUTPUT_DIR#": str(output_dir.resolve()),
            "#ICON_LINE#": icon_line,
            "#MAIN_EXE#": main_exe,
            "#DEFAULT_DIR#": default_dir,
            "#PRIVILEGES_REQUIRED#": privileges_required,
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))
        return result

    # ////////////////////////////////////////////////
    # METADATA
    # ////////////////////////////////////////////////

    def get_installer_name(self) -> str:
        return "InnoSetup"
