# ///////////////////////////////////////////////////////////////
# UPDATER_SERVICE - Update client generation service
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Updater service - Generates auto-update client files for compiled apps.

Produces update.py, settings.py, and copies root.json from the local
TUF repository. Files are meant to be embedded in the compiled bundle
via include_files.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..shared import CompilerConfig
from ..shared._constants import UPDATE_SUBDIR
from ..shared.exceptions import UpdaterConfigError, UpdaterGenerationError

_TEMPLATES_DIR = Path(__file__).parent.parent / "assets" / "templates" / "updater"
_ROOT_JSON = "root.json"


class UpdaterService:
    """Service that generates the tufup client update files."""

    @staticmethod
    def generate(config: CompilerConfig, output_dir: Path) -> list[Path]:
        """Generate update.py, settings.py, and copy root.json.

        Args:
            config: Compiler configuration (must have tuf_enabled=True).
            output_dir: Directory where files are written (created if absent).

        Returns:
            List of generated file paths [settings.py, update.py, root.json].

        Raises:
            UpdaterConfigError: If config is invalid (tuf_enabled=False,
                root.json absent, repo_public_url missing for non-disk).
            UpdaterGenerationError: If writing files fails.
        """
        UpdaterService._validate(config)
        update_url = UpdaterService._resolve_update_url(config)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            generated: list[Path] = []
            generated.append(
                UpdaterService._render_template(
                    "settings", config, update_url, output_dir
                )
            )
            generated.append(
                UpdaterService._render_template(
                    "update", config, update_url, output_dir
                )
            )
            generated.append(UpdaterService._copy_root_json(config, output_dir))
            return generated
        except (UpdaterConfigError, UpdaterGenerationError):
            raise
        except Exception as exc:
            raise UpdaterGenerationError(
                f"Failed to generate updater files in {output_dir}: {exc}"
            ) from exc

    @staticmethod
    def _validate(config: CompilerConfig) -> None:
        if not config.tuf_enabled:
            raise UpdaterConfigError(
                "tuf_enabled must be True to generate updater files. "
                "Set tuf_enabled=True in your config."
            )
        if config.tuf_repo_dir is None:
            raise UpdaterConfigError("tuf_repo_dir is required to locate root.json.")
        root_json = config.tuf_repo_dir / "metadata" / _ROOT_JSON
        if not root_json.exists():
            raise UpdaterConfigError(
                f"root.json not found at {root_json}. "
                "Run 'ezcompiler release init' first to initialise the TUF repository."
            )

    @staticmethod
    def _resolve_update_url(config: CompilerConfig) -> str:
        # The client URL must mirror where UploaderService writes the TUF
        # tree: disk/server place it under the UPDATE_SUBDIR subdir, while r2
        # uploads straight to the bucket prefix. Sharing the constant keeps
        # both sides in sync.
        if config.repo_destination == "disk":
            endpoint = config.repo_endpoint.rstrip("/").replace("\\", "/")
            if not endpoint.startswith("/"):
                endpoint = f"/{endpoint}"
            return f"file://{endpoint}/{UPDATE_SUBDIR}"
        if config.repo_destination == "r2":
            return config.repo_public_url.rstrip("/")
        # server
        return config.repo_public_url.rstrip("/") + f"/{UPDATE_SUBDIR}"

    @staticmethod
    def _render_template(
        name: str,
        config: CompilerConfig,
        update_url: str,
        output_dir: Path,
    ) -> Path:
        tmpl_path = _TEMPLATES_DIR / f"{name}.py.template"
        try:
            content = tmpl_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise UpdaterGenerationError(
                f"Cannot read template {tmpl_path}: {exc}"
            ) from exc

        content = content.replace("#APP_NAME#", config.project_name)
        content = content.replace("#VERSION#", config.version)
        content = content.replace("#UPDATE_URL#", update_url)

        dest = output_dir / f"{name}.py"
        try:
            dest.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise UpdaterGenerationError(f"Cannot write {dest}: {exc}") from exc
        return dest

    @staticmethod
    def _copy_root_json(config: CompilerConfig, output_dir: Path) -> Path:
        assert config.tuf_repo_dir is not None  # guaranteed by _validate
        src = config.tuf_repo_dir / "metadata" / _ROOT_JSON
        dst = output_dir / _ROOT_JSON
        try:
            shutil.copy2(src, dst)
        except OSError as exc:
            raise UpdaterGenerationError(
                f"Cannot copy root.json from {src} to {dst}: {exc}"
            ) from exc
        return dst
