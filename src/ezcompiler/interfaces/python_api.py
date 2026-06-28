# ///////////////////////////////////////////////////////////////
# PYTHON_API - Python API interface for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Python API interface - High-level Python API for EzCompiler.

This module provides the EzCompiler class that orchestrates project compilation,
version generation, setup file creation, artifact zipping, and repository upload
using the service layer.

Interfaces layer can use all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    import logging

    from ezplog.handlers.wizard.dynamic import StageConfig
    from ezplog.lib_mode import _LazyPrinter

    from ..types import ReleaseDestination, RepoDestination

# Third-party imports
from ezplog.lib_mode import get_logger, get_printer

# Local imports
from ..services import (
    CompilerService,
    PipelineService,
    ReleaseService,
    TemplateService,
    UploaderService,
)
from ..shared import CompilationResult, CompilerConfig
from ..shared.exceptions import (
    CompilationError,
    ConfigurationError,
    ReleaseError,
    SigningKeyError,
    TemplateError,
    UploadError,
    VersionError,
    ZipError,
)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class EzCompiler:
    """
    Main orchestration class for project compilation and distribution.

    Coordinates project compilation using modular compilers, version file
    generation, setup file creation, artifact zipping, and repository upload.
    Provides high-level API for managing the full build pipeline.

    Attributes:
        _config: CompilerConfig instance with project settings (read via .config property)
        printer: Lazy printer proxy — silent until host app initializes Ezpl
        logger: Stdlib logger — silent until host app configures logging

    Example:
        >>> config = CompilerConfig(...)
        >>> compiler = EzCompiler(config)
        >>> compiler.compile_project()
        >>> compiler.zip_compiled_project()
        >>> compiler.upload()
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(
        self,
        config: CompilerConfig | None = None,
        compiler_service_factory: (
            Callable[[CompilerConfig], CompilerService] | None
        ) = None,
        template_service: TemplateService | None = None,
        uploader_service: UploaderService | None = None,
        pipeline_service: PipelineService | None = None,
    ) -> None:
        """
        Initialize the EzCompiler orchestrator.

        Logging follows the lib_mode pattern: both the printer and logger are
        passive proxies that produce no output until the host application
        initializes Ezpl. No logging configuration happens here — that is an
        application-level concern.

        Args:
            config: Optional CompilerConfig instance (can be set later via init_project)
            compiler_service_factory: Optional factory for CompilerService (for testing)
            template_service: Optional TemplateService instance (for testing)
            uploader_service: Optional UploaderService instance (for testing)
            pipeline_service: Optional PipelineService instance (for testing)
        """
        # Configuration management
        self._config = config

        # Passive lib-mode logging — silent until host app initializes Ezpl
        self._printer: _LazyPrinter = get_printer()
        self._logger: logging.Logger = get_logger(__name__)

        # Service instances
        self._compiler_service_factory = compiler_service_factory or CompilerService
        self._compiler_service: CompilerService | None = None
        self._template_service = template_service or TemplateService()
        self._uploader_service = uploader_service or UploaderService()
        self._pipeline_service = pipeline_service or PipelineService()

        # Compilation state
        self._compilation_result: CompilationResult | None = None

    # ////////////////////////////////////////////////
    # LOGGING ACCESSOR PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def printer(self) -> _LazyPrinter:
        """
        Get the console printer proxy.

        Returns:
            _LazyPrinter: Lazy printer — silent until host app initializes Ezpl
        """
        return self._printer

    @property
    def logger(self) -> logging.Logger:
        """
        Get the stdlib logger.

        Returns:
            logging.Logger: Stdlib logger — silent until host app configures logging
        """
        return self._logger

    @property
    def config(self) -> CompilerConfig | None:
        """
        Get the current compiler configuration.

        Returns:
            CompilerConfig | None: Current configuration or None if not initialized
        """
        return self._config

    # ////////////////////////////////////////////////
    # PROJECT INITIALIZATION
    # ////////////////////////////////////////////////

    def init_project(
        self,
        version: str,
        project_name: str,
        main_file: str,
        include_files: dict[str, list[str]],
        output_folder: Path | str,
        **kwargs: Any,
    ) -> None:
        """
        Initialize project configuration.

        Creates a CompilerConfig from provided parameters. This is a
        convenience method for backward compatibility; can also set
        config directly.

        Args:
            version: Project version (e.g., "1.0.0")
            project_name: Project name
            main_file: Path to main Python file
            include_files: Dict with 'files' and 'folders' lists
            output_folder: Output directory path
            **kwargs: Additional config options

        Raises:
            ConfigurationError: If configuration is invalid

        Example:
            >>> compiler = EzCompiler()
            >>> compiler.init_project(
            ...     version="1.0.0",
            ...     project_name="MyApp",
            ...     main_file="main.py",
            ...     include_files={"files": [], "folders": []},
            ...     output_folder="dist"
            ... )
        """
        try:
            # Create configuration from parameters
            config_dict: dict[str, Any] = {
                "version": version,
                "project_name": project_name,
                "main_file": main_file,
                "include_files": include_files,
                "output_folder": str(output_folder),
                **kwargs,
            }

            # Update configuration
            self._config = CompilerConfig(**config_dict)

            self._printer.success("Project configuration initialized successfully")
            self._logger.info("Project configuration initialized successfully")

        except ConfigurationError:
            raise
        except Exception as e:
            self._printer.error(f"Failed to initialize project: {e}")
            self._logger.error(f"Failed to initialize project: {e}")
            raise ConfigurationError(f"Failed to initialize project: {e}") from e

    # ////////////////////////////////////////////////
    # VERSION AND SETUP GENERATION
    # ////////////////////////////////////////////////

    def generate_version_file(self, name: str = "version_info.txt") -> None:
        """
        Generate version information file.

        Uses the configured version information to generate a version file
        at the specified path. Legacy method for backward compatibility.

        Args:
            name: Version file name (default: "version_info.txt")

        Raises:
            ConfigurationError: If project not initialized

        Note:
            Requires project to be initialized first via init_project().
        """
        try:
            if not self._config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Generate using TemplateService
            config_dict = self._config.to_dict()
            version_file_path = Path(name)
            self._template_service.generate_version_file(config_dict, version_file_path)

            self._printer.success("Version file generated successfully")
            self._logger.info("Version file generated successfully")

        except (ConfigurationError, VersionError, TemplateError):
            raise
        except Exception as e:
            self._printer.error(f"Failed to generate version file: {e}")
            self._logger.error(f"Failed to generate version file: {e}")
            raise VersionError(f"Failed to generate version file: {e}") from e

    def generate_setup_file(self, file_path: Path | str) -> None:
        """
        Generate setup.py file from template.

        Creates a setup.py file using the template system. Legacy method
        for backward compatibility.

        Args:
            file_path: Path where to create the setup.py file

        Raises:
            ConfigurationError: If project not initialized

        Note:
            Requires project to be initialized first via init_project().
        """
        try:
            if not self._config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Generate using TemplateService
            config_dict = self._config.to_dict()
            output_path = Path(file_path)
            self._template_service.generate_setup_file(
                config_dict, output_path=output_path
            )

            self._printer.success("Setup file generated successfully")
            self._logger.info("Setup file generated successfully")

        except (ConfigurationError, TemplateError):
            raise
        except Exception as e:
            self._printer.error(f"Failed to generate setup file: {e}")
            self._logger.error(f"Failed to generate setup file: {e}")
            raise TemplateError(f"Failed to generate setup file: {e}") from e

    # ////////////////////////////////////////////////
    # COMPILATION METHODS
    # ////////////////////////////////////////////////

    def compile_project(
        self, console: bool = True, compiler: str | None = None
    ) -> None:
        """
        Compile the project using specified or auto-selected compiler.

        Validates configuration, selects compiler if not specified, and
        executes compilation. Sets _zip_needed based on compiler output type.

        Args:
            console: Whether to show console window (default: True)
            compiler: Compiler to use or None for auto-selection
                - "Cx_Freeze": Creates directory with dependencies
                - "PyInstaller": Creates single executable
                - "Nuitka": Creates standalone folder or single executable
                - None: Prompt user for choice or use config default

        Raises:
            ConfigurationError: If project not initialized
            CompilationError: If compilation fails

        Example:
            >>> compiler.compile_project(console=False, compiler="PyInstaller")
        """
        try:
            if not self._config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Create compiler service and compile
            self._compiler_service = self._compiler_service_factory(self._config)
            self._compilation_result = self._compiler_service.compile(
                console=console,
                compiler=cast(
                    Literal["Cx_Freeze", "PyInstaller", "Nuitka", "auto"] | None,
                    compiler,
                ),
            )

            self._printer.success("Project compiled successfully")
            self._logger.info("Project compiled successfully")

        except (ConfigurationError, CompilationError):
            raise
        except Exception as e:
            self._printer.error(f"Compilation failed: {e}")
            self._logger.error(f"Compilation failed: {e}")
            raise CompilationError(f"Compilation failed: {e}") from e

    def zip_compiled_project(self) -> None:
        """
        Create ZIP archive of compiled project.

        Archives the compiled output if needed. Cx_Freeze output is
        zipped; PyInstaller single-file output is not.

        Raises:
            ConfigurationError: If project not initialized

        Note:
            ZIP creation is optional based on compiler type and settings.
        """
        try:
            if not self._config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Check if ZIP is needed from compilation result
            zip_needed = (
                self._compilation_result.zip_needed
                if self._compilation_result
                else True
            )

            if not zip_needed:
                self._printer.info("ZIP not needed for this compilation type")
                return

            # Create ZIP archive via CompilerService
            if self._compiler_service is None:
                self._compiler_service = self._compiler_service_factory(self._config)

            self._pipeline_service.zip_artifact(
                config=self._config,
                compiler_service=self._compiler_service,
                compilation_result=self._compilation_result,
                progress_callback=self._zip_progress_callback,
            )

            self._printer.success("ZIP archive created successfully")
            self._logger.info("ZIP archive created successfully")

        except (ConfigurationError, ZipError):
            raise
        except Exception as e:
            self._printer.error(f"Failed to create ZIP archive: {e}")
            self._logger.error(f"Failed to create ZIP archive: {e}")
            raise ZipError(f"Failed to create ZIP archive: {e}") from e

    # ////////////////////////////////////////////////
    # UPLOAD METHODS
    # ////////////////////////////////////////////////

    def upload(
        self,
        destination: str | None = None,
        repo_destination: RepoDestination | None = None,
        release_destination: ReleaseDestination | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Upload le repo TUF et/ou le zip installeur selon la config.

        Quand ``release_needed`` est True, effectue deux uploads séquentiels :
        1. arbre TUF → ``<dest>/update/``
        2. zip installeur → ``<dest>/release/`` (ignoré si repo_destination="r2")

        Sinon, uploade l'artefact compilé (comportement inchangé).

        Args:
            destination: Override commun pour les deux destinations.
            repo_destination: Override de ``config.repo_destination``.
            release_destination: Override de ``config.release_destination``.
            upload_config: Options supplémentaires passées aux uploaders.

        Raises:
            ConfigurationError: Si le projet n'est pas initialisé.
            UploadError: Si un upload échoue.
        """
        if not self._config:
            raise ConfigurationError(
                "Project not initialized. Call init_project() first."
            )

        repo_dest = repo_destination or self._config.repo_destination
        rel_dest = release_destination or self._config.release_destination

        try:
            if self._config.release_needed:
                repo_dir = self._config.tufup_repo_dir or (
                    self._config.output_folder / "repo"
                )

                # Étape 1 — upload arbre TUF
                try:
                    if repo_dest == "r2":
                        UploaderService.upload(
                            source_path=repo_dir,
                            upload_type="r2",
                            destination=self._config.r2_remote_prefix,
                            upload_config={"bucket": self._config.r2_bucket},
                        )
                    elif repo_dest == "server":
                        base = (
                            destination or self._config.resolved_repo_destination or ""
                        )
                        UploaderService.upload(
                            source_path=repo_dir,
                            upload_type="server",
                            destination=base.rstrip("/") + "/update",
                            upload_config=upload_config,
                        )
                    else:  # disk (default)
                        base = (
                            destination or self._config.resolved_repo_destination or ""
                        )
                        UploaderService.upload(
                            source_path=repo_dir,
                            upload_type="disk",
                            destination=str(Path(base) / "update"),
                            upload_config=upload_config,
                        )
                except UploadError as e:
                    raise UploadError(f"TUF repo upload failed: {e}") from e

                # Étape 2 — upload zip (ignoré si R2)
                if repo_dest != "r2":
                    release_root = self._pipeline_service.assemble_release_dir(
                        self._config
                    )
                    try:
                        if rel_dest == "server":
                            base = (
                                destination
                                or self._config.resolved_release_destination
                                or ""
                            )
                            UploaderService.upload(
                                source_path=release_root,
                                upload_type="server",
                                destination=base.rstrip("/") + "/release",
                                upload_config=upload_config,
                            )
                        else:  # disk (default)
                            base = (
                                destination
                                or self._config.resolved_release_destination
                                or ""
                            )
                            UploaderService.upload(
                                source_path=release_root,
                                upload_type="disk",
                                destination=str(Path(base) / "release"),
                                upload_config=upload_config,
                            )
                    except UploadError as e:
                        raise UploadError(f"Release zip upload failed: {e}") from e

            else:
                dest = destination or (
                    self._config.server_url
                    if repo_dest == "server"
                    else self._config.repo_path
                )
                self._pipeline_service.upload_artifact(
                    config=self._config,
                    structure=repo_dest,
                    destination=str(dest),
                    compilation_result=self._compilation_result,
                    upload_config=upload_config,
                )

            self._printer.success(f"Upload completed ({repo_dest})")
            self._logger.info(f"Upload completed ({repo_dest})")

        except (ConfigurationError, UploadError, ReleaseError):
            raise
        except Exception as e:
            self._printer.error(f"Upload failed: {e}")
            self._logger.error(f"Upload failed: {e}")
            raise UploadError(f"Upload failed: {e}") from e

    def release(
        self,
        bundle_dir: Path,
        *,
        publish: bool = False,
    ) -> Path:
        """Package a compiled bundle into a signed TUF repository.

        Reads app name, version and tufup directories from the config.
        When ``publish`` is True, the repository tree is transferred via the
        configured uploader (``update_repo_url`` + repo_destination).

        Args:
            bundle_dir: Directory containing the compiled application artifacts.
            publish: When True, upload the repository/ tree to ``update_repo_url``.

        Returns:
            Path: The local ``repository/`` tree produced by tufup.

        Raises:
            ConfigurationError: If project not initialized.
            ReleaseError: If release packaging or remote publishing fails.
        """
        if not self._config:
            raise ConfigurationError(
                "Project not initialized. Call init_project() first."
            )
        if publish:
            import warnings  # noqa: PLC0415

            warnings.warn(
                "release(publish=True) est déprécié : le transfert distant est "
                "désormais assuré par le stage upload de run_pipeline.",
                DeprecationWarning,
                stacklevel=2,
            )
        repo_dir = self._config.tufup_repo_dir or (self._config.output_folder / "repo")
        keys_dir = self._config.tufup_keys_dir or (repo_dir / "keystore")
        return ReleaseService.release_and_publish(
            bundle_dir=bundle_dir,
            app_name=self._config.project_name,
            version=self._config.version,
            repo_dir=repo_dir,
            release_type=self._config.release_type,
            publish=publish,
            upload_type=self._config.repo_destination if publish else None,
            destination=self._config.update_repo_url if publish else None,
            releaser_config={"keys_dir": keys_dir},
        )

    def init_release(self) -> bool:
        """Initialise les clés/repo TUF depuis la config courante.

        Action explicite — jamais appelée par run_pipeline().

        Returns:
            bool: True si init effectuée, False si clés déjà présentes (skip).

        Raises:
            ConfigurationError: If project not initialized.
            ReleaseError: If TUF initialization fails.
        """
        if not self._config:
            raise ConfigurationError(
                "Project not initialized. Call init_project() first."
            )
        repo_dir = self._config.tufup_repo_dir or (self._config.output_folder / "repo")
        keys_dir = self._config.tufup_keys_dir or (repo_dir / "keystore")
        return ReleaseService.init_release(
            app_name=self._config.project_name,
            repo_dir=repo_dir,
            keys_dir=keys_dir,
            release_type=self._config.release_type,
        )

    def run_pipeline(
        self,
        console: bool = True,
        compiler: str | None = None,
        skip_zip: bool = False,
        skip_release: bool = False,
    ) -> None:
        """
        Run the build pipeline with visual progress tracking.

        Executes version generation, compilation, optional ZIP creation and
        optional TUF release in sequence with a DynamicLayeredProgress display.
        Upload is no longer part of the pipeline — call ``upload()`` explicitly
        afterwards.

        Args:
            console: Whether to show console window (default: True)
            compiler: Compiler to use or None for auto-selection
            skip_zip: Skip ZIP archive creation
            skip_release: Skip the TUF release stage

        Raises:
            ConfigurationError: If project not initialized
            CompilationError: If compilation fails
            VersionError: If version file generation fails
            ZipError: If ZIP creation fails
            ReleaseError: If the release stage fails

        Example:
            >>> compiler = EzCompiler(config)
            >>> compiler.run_pipeline(console=False)
            >>> compiler.upload()
        """
        if not self._config:
            raise ConfigurationError(
                "Project not initialized. Call init_project() first."
            )

        # Determine which optional stages to include
        should_zip = not skip_zip
        should_release = not skip_release and getattr(
            self._config, "release_needed", False
        )

        # Pre-flight: fail early if release needed but keys absent
        if should_release:
            repo_dir = self._config.tufup_repo_dir or (
                self._config.output_folder / "repo"
            )
            keys_dir = self._config.tufup_keys_dir or (repo_dir / "keystore")
            self._preflight_release(keys_dir)

        # Build stages
        stages: list[StageConfig] = cast(
            list["StageConfig"],
            PipelineService.build_stages(
                self._config,
                should_zip=should_zip,
                should_release=should_release,
            ),
        )

        current_phase = "version"
        pipeline_error: Exception | None = None

        with self._printer.wizard.dynamic_layered_progress(stages) as dlp:
            try:
                # Version file
                current_phase = "version"
                dlp.update_layer("version", 0, "Processing template...")
                config_dict = self._config.to_dict()
                version_file_path = Path(self._config.version_filename)
                self._template_service.generate_version_file(
                    config_dict, version_file_path
                )
                self._logger.info("Version file generated successfully")
                dlp.complete_layer("version")

                # Compilation
                current_phase = "compile"
                dlp.update_layer("compile", 0, "Initializing compiler...")
                self._compiler_service, self._compilation_result = (
                    self._pipeline_service.compile_project(
                        config=self._config,
                        console=console,
                        compiler=compiler,
                    )
                )
                self._logger.info("Project compiled successfully")
                dlp.complete_layer("compile")

                # ZIP
                zip_needed = (
                    self._compilation_result.zip_needed
                    if self._compilation_result
                    else True
                )
                if should_zip:
                    if zip_needed:
                        current_phase = "zip"

                        def _zip_cb(filename: str, progress: int) -> None:
                            """Update progress display during ZIP file creation.

                            Args:
                                filename: The name of the file being compressed.
                                progress: The current progress percentage (0-100).
                            """
                            dlp.update_layer("zip", progress, Path(filename).name)

                        self._pipeline_service.zip_artifact(
                            config=self._config,
                            compiler_service=self._compiler_service,
                            compilation_result=self._compilation_result,
                            progress_callback=_zip_cb,
                        )
                        self._logger.info("ZIP archive created successfully")
                        dlp.complete_layer("zip")
                    else:
                        # Stage was added but not needed at runtime
                        dlp.update_layer("zip", 0, "Skipped (not needed)")
                        dlp.complete_layer("zip")

                # Release (build the local TUF tree; upload is a separate step)
                if should_release:
                    current_phase = "release"
                    dlp.update_layer("release", 0, "Signing bundle...")
                    repository_path = self._pipeline_service.release_artifact(
                        config=self._config,
                        compilation_result=self._compilation_result,
                    )
                    self._logger.info(f"TUF release built: {repository_path}")
                    dlp.complete_layer("release")

            except (
                ConfigurationError,
                CompilationError,
                TemplateError,
                VersionError,
                UploadError,
                ZipError,
                ReleaseError,
                SigningKeyError,
            ) as e:
                dlp.handle_error(current_phase, str(e))
                dlp.emergency_stop(str(e))
                pipeline_error = e
            except Exception as e:
                dlp.handle_error(current_phase, str(e))
                dlp.emergency_stop(str(e))
                pipeline_error = e

        if pipeline_error:
            self._printer.error(str(pipeline_error))
            self._logger.error(str(pipeline_error))
            raise pipeline_error

        self._printer.success("Build pipeline finished")
        self._logger.info("Build pipeline finished")

    # ////////////////////////////////////////////////
    # PRIVATE HELPER METHODS
    # ////////////////////////////////////////////////

    def _preflight_release(self, keys_dir: Path) -> None:
        """Raise SigningKeyError before compilation if signing keys are absent."""
        if not keys_dir.is_dir() or not any(keys_dir.iterdir()):
            raise SigningKeyError(
                f"Signing keys not found in {keys_dir}. "
                "Run `ezcompiler release init` first."
            )

    def _zip_progress_callback(self, filename: str, progress: int) -> None:
        """
        Progress callback for ZIP archive creation.

        Logs progress at 10% intervals to reduce log verbosity.

        Args:
            filename: Current file being zipped
            progress: Progress percentage (0-100)
        """
        if progress % 10 == 0:  # Log every 10%
            self._printer.debug(f"ZIP progress: {progress}% - {filename}")
            self._logger.debug(f"ZIP progress: {progress}% - {filename}")
