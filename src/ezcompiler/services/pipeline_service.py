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
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..shared.compilation_result import CompilationResult

# Local imports
from ..shared.compiler_config import CompilerConfig
from .compiler_service import CompilerService
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
            compiler=compiler,  # type: ignore[arg-type]
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
        zip_needed = (
            compilation_result.zip_needed if compilation_result else config.zip_needed
        )
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
        zip_needed = (
            compilation_result.zip_needed if compilation_result else config.zip_needed
        )
        source_file = (
            str(config.zip_file_path) if zip_needed else str(config.output_folder)
        )

        UploaderService.upload(
            source_path=Path(source_file),
            upload_type=structure,  # type: ignore[arg-type]
            destination=destination,
            upload_config=upload_config,
        )
