# ///////////////////////////////////////////////////////////////
# PIPELINE_SERVICE - Build pipeline orchestration helpers
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Pipeline service - Compilation, ZIP and upload orchestration.

This service extracts the compile->zip->upload workflow from interfaces
so the orchestration logic remains reusable and testable.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, cast

# Local imports
from ..shared import CompilationResult, CompilerConfig
from .compiler_service import CompilerService
from .installer_service import InstallerService
from .release_service import ReleaseService
from .uploader_service import UploaderService

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class PipelineService:
    """Service that coordinates compile, zip and upload stages."""

    def __init__(
        self,
        compiler_service_factory: (
            Callable[[CompilerConfig], CompilerService] | None
        ) = None,
    ) -> None:
        """Initialise the pipeline service.

        Args:
            compiler_service_factory: Optional factory to create a CompilerService
                from a CompilerConfig. Defaults to ``CompilerService`` constructor.
                Inject a custom factory in tests to avoid triggering real compilation.
        """
        self._compiler_service_factory: Callable[[CompilerConfig], CompilerService] = (
            compiler_service_factory or CompilerService
        )

    def compile_project(
        self,
        config: CompilerConfig,
        console: bool = True,
        compiler: str | None = None,
    ) -> tuple[CompilerService, CompilationResult]:
        """Compile a project and return service + result."""
        compiler_service = self._compiler_service_factory(config)
        compilation_result = compiler_service.compile(
            console=console,
            compiler=cast(
                Literal["Cx_Freeze", "PyInstaller", "Nuitka"] | None,
                compiler,
            ),
        )
        return compiler_service, compilation_result

    def zip_artifact(
        self,
        config: CompilerConfig,
        compiler_service: CompilerService,
        compilation_result: CompilationResult | None,
        progress_callback: Callable[[str, int], None] | None = None,
    ) -> bool:
        """Create ZIP artifact when required and return True when created."""
        zip_needed = compilation_result.zip_needed if compilation_result else True
        if not zip_needed:
            return False

        compiler_service._zip_artifact(
            output_path=str(config.zip_file_path),
            progress_callback=progress_callback,
        )
        return True

    @staticmethod
    def build_stages(
        config: CompilerConfig,
        should_zip: bool = False,
        should_upload: bool = False,
        should_release: bool = False,
        should_installer: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Build the stage list for dynamic_layered_progress.

        Args:
            config: Compiler configuration (used for display labels)
            should_zip: Whether a ZIP stage should be included
            should_upload: Whether an upload stage should be included

        Returns:
            list[dict]: Stage configuration list ready for dynamic_layered_progress
        """
        stages: list[dict[str, Any]] = [
            {
                "name": "main",
                "type": "main",
                "description": f"Building {config.project_name} v{config.version}",
            },
            {
                "name": "version",
                "type": "spinner",
                "description": "Generating version file",
            },
            {
                "name": "compile",
                "type": "spinner",
                "description": f"Compiling with {config.compiler}",
            },
        ]
        if should_zip:
            stages.append(
                {
                    "name": "zip",
                    "type": "progress",
                    "description": "Creating ZIP archive",
                    "total": 100,
                }
            )
        if should_installer:
            stages.append(
                {
                    "name": "installer",
                    "type": "spinner",
                    "description": "Building installer",
                }
            )
        if should_release:
            stages.append(
                {
                    "name": "release",
                    "type": "spinner",
                    "description": "Building TUF release",
                }
            )
        if should_upload:
            stages.append(
                {
                    "name": "upload",
                    "type": "spinner",
                    "description": "Uploading artifacts",
                }
            )
        return stages

    def upload_artifact(
        self,
        config: CompilerConfig,
        structure: str,
        destination: str,
        compilation_result: CompilationResult | None,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Upload project artifact to a destination."""
        zip_needed = compilation_result.zip_needed if compilation_result else True
        source_file = (
            str(config.zip_file_path) if zip_needed else str(config.output_folder)
        )

        UploaderService.upload(
            source_path=Path(source_file),
            upload_type=cast(Literal["disk", "server"], structure),
            destination=destination,
            upload_config=upload_config,
        )

    @staticmethod
    def assemble_release_dir(config: CompilerConfig) -> Path:
        """Assemble le dossier release contenant le zip et l'installeur.

        Layout (nettoyé à chaque run)::

            release/
            ├── <App>.zip                     (si le fichier existe)
            └── <App>-<version>-setup.exe      (si installer_enabled=True)

        L'arbre TUF (metadata/ + targets/) reste dans tufup_repo_dir et est
        poussé directement vers le backend d'update par upload().

        Args:
            config: Configuration (fournit output_folder et zip_file_path).

        Returns:
            Path: Le dossier ``release/`` assemblé.
        """
        release_dir = config.output_folder.parent / "release"
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir(parents=True)

        zip_path = Path(config.zip_file_path)
        if zip_path.is_file():
            shutil.copy2(zip_path, release_dir / zip_path.name)

        if config.installer_enabled:
            installer_dir = config.installer_output_dir or (
                config.output_folder.parent / "installer"
            )
            installer_exe = (
                installer_dir / f"{config.project_name}-{config.version}-setup.exe"
            )
            if installer_exe.is_file():
                shutil.copy2(installer_exe, release_dir / installer_exe.name)

        return release_dir

    @staticmethod
    def release_artifact(
        config: CompilerConfig,
        compilation_result: CompilationResult | None,  # noqa: ARG004
    ) -> Path:
        """Build le repo TUF local depuis output_folder. Ne publie jamais."""
        repo_dir = config.tuf_repo_dir or (config.output_folder / "repo")
        keys_dir = config.tuf_keys_dir or (repo_dir / "keystore")
        return ReleaseService.release_and_publish(
            bundle_dir=config.output_folder,
            app_name=config.project_name,
            version=config.version,
            repo_dir=repo_dir,
            publish=False,
            releaser_config={"keys_dir": keys_dir},
        )

    @staticmethod
    def build_installer(
        config: CompilerConfig,
        compilation_result: CompilationResult | None,  # noqa: ARG004
    ) -> Path | None:
        """Build the Inno Setup installer when installer_enabled=True."""
        if not config.installer_enabled:
            return None

        output_dir = config.installer_output_dir or (
            config.output_folder.parent / "installer"
        )
        installer_config: dict[str, Any] = {
            "icon": config.icon,
            "company_name": config.company_name,
        }
        if config.installer_iss_path is not None:
            installer_config["iss_path"] = config.installer_iss_path

        return InstallerService.build_installer(
            bundle_dir=config.output_folder,
            app_name=config.project_name,
            version=config.version,
            output_dir=output_dir,
            installer_config=installer_config,
        )
