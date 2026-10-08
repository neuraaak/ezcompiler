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

    from .._types import ReleaseDestination, RepoDestination

# Third-party imports
from ezplog.lib_mode import get_logger, get_printer

# Local imports
from ..services import (
    CompilerService,
    PipelineService,
    PublishService,
    ReleaseService,
    TemplateService,
    TufService,
    UpdaterService,
    UploaderService,
)
from ..shared import CompilationResult, CompilerConfig, ReleasePreflight
from ..shared.exceptions import (
    CompilationError,
    ConfigurationError,
    InstallerError,
    ReleaseError,
    SigningKeyError,
    TemplateError,
    UploadError,
    VersionError,
    ZipError,
)
from ..utils import is_prerelease

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_MSG_NOT_INITIALIZED = "Project not initialized. Call init_project() first."
_MSG_VERSION_OK = "Version file generated successfully"
_MSG_COMPILED_OK = "Project compiled successfully"
_MSG_ZIP_OK = "ZIP archive created successfully"

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
        self._pipeline_service = pipeline_service or PipelineService(
            compiler_service_factory=self._compiler_service_factory
        )

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
                raise ConfigurationError(_MSG_NOT_INITIALIZED)

            # Generate using TemplateService
            config_dict = self._config.to_dict()
            version_file_path = Path(name)
            self._template_service.generate_version_file(config_dict, version_file_path)

            self._printer.success(_MSG_VERSION_OK)
            self._logger.info(_MSG_VERSION_OK)

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
                raise ConfigurationError(_MSG_NOT_INITIALIZED)

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
                raise ConfigurationError(_MSG_NOT_INITIALIZED)

            # Create compiler service and compile
            self._compiler_service = self._compiler_service_factory(self._config)
            self._compilation_result = self._compiler_service.compile(
                console=console,
                compiler=cast(
                    Literal["Cx_Freeze", "PyInstaller", "Nuitka"] | None,
                    compiler,
                ),
            )

            self._printer.success(_MSG_COMPILED_OK)
            self._logger.info(_MSG_COMPILED_OK)

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
                raise ConfigurationError(_MSG_NOT_INITIALIZED)

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

            self._printer.success(_MSG_ZIP_OK)
            self._logger.info(_MSG_ZIP_OK)

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
        """Upload the TUF repo and/or the installer zip, as the config says.

        Deprecated:
            Deprecated since 4.1.0, removed in v5. Use ``publish_update()``
            then ``publish_release()``, or the CLI (``ezcompiler publish
            update`` then ``ezcompiler publish release``), which asks for
            confirmation before any irreversible publication.

        When ``release_needed`` is True, performs two sequential uploads:
        1. TUF tree -> ``<dest>/update/``
        2. installer zip -> ``<dest>/release/`` (skipped if repo_destination="r2")

        Otherwise, uploads the compiled artifact (unchanged behavior).

        Args:
            destination: Shared override for both destinations.
            repo_destination: Override for ``config.repo_destination``.
            release_destination: Override for ``config.release_destination``.
            upload_config: Extra options passed to the uploaders.

        Raises:
            ConfigurationError: If the project is not initialized.
            UploadError: If an upload fails.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)

        import warnings  # noqa: PLC0415

        warnings.warn(
            "EzCompiler.upload() is deprecated and will be removed in v5. "
            "Use `publish_update()` then `publish_release()` (or the CLI: "
            "`ezcompiler publish update` then `ezcompiler publish release`, "
            "which asks for confirmation before any irreversible publication).",
            DeprecationWarning,
            stacklevel=2,
        )

        repo_dest = repo_destination or self._config.repo_destination

        try:
            if self._config.tuf_enabled:
                repo_dir = TufService.repo_dir(self._config)
                rel_dest = release_destination or self._config.release_destination
                release_root = (
                    None
                    if repo_dest == "r2" and rel_dest == "disk"
                    else self._pipeline_service.assemble_release_dir(self._config)
                )
                UploaderService.upload_release(
                    config=self._config,
                    repo_dir=repo_dir,
                    release_root=release_root,
                    destination=destination,
                    repo_destination=repo_destination,
                    release_destination=release_destination,
                    upload_config=upload_config,
                )

            else:
                dest = destination or self._config.resolved_repo_destination or ""
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

    def publish_update(
        self,
        destination: str | None = None,
        repo_destination: RepoDestination | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """Publish the signed TUF tree to the update backend.

        Python counterpart of ``ezcompiler publish update``. Only the public
        part of the tree is transferred; the interactive confirmation stays
        specific to the CLI, a programmatic call being explicit by nature.

        Args:
            destination: Override for the resolved update destination.
            repo_destination: Override for ``config.repo_destination``.
            upload_config: Extra options passed to the uploader.

        Raises:
            ConfigurationError: If the project is not initialized.
            UploadError: If the transfer fails.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)

        PublishService.publish_update(
            self._config,
            destination=destination,
            repo_destination=repo_destination,
            upload_config=upload_config,
        )
        self._logger.info("TUF update tree published")

    def preflight_release(
        self,
        *,
        tag: str | None = None,
        release_destination: ReleaseDestination | None = None,
    ) -> ReleasePreflight:
        """Run the pre-publication checks and return the recap.

        Args:
            tag: Target tag (default: ``v<version>``).
            release_destination: Override for ``config.release_destination``.

        Returns:
            ReleasePreflight: What the publication would do, once every local
                check has passed.

        Raises:
            ConfigurationError: If the project is not initialized.
            PublishError: If the platform CLI is missing, not authenticated,
                or if the tag already exists.
            ReleaseError: If an enabled installer is missing, or if nothing
                was built.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)

        return PublishService.preflight_release(
            self._config,
            tag=tag or f"v{self._config.version}",
            release_destination=release_destination,
        )

    def publish_release(
        self,
        *,
        tag: str | None = None,
        title: str | None = None,
        notes: str | None = None,
        prerelease: bool | None = None,
        draft: bool = False,
        destination: str | None = None,
        release_destination: ReleaseDestination | None = None,
        upload_config: dict[str, Any] | None = None,
    ) -> str | None:
        """Publish the installer and the zip as a release.

        Python counterpart of ``ezcompiler publish release``. On a platform
        (``github``), creates the release and attaches the artifacts; on a
        file destination (``disk``/``server``/``r2``), copies the artifacts.
        The operation is irreversible on the platform side: call
        ``preflight_release()`` first to present a recap.

        Args:
            tag: Release tag (default: ``v<version>``).
            title: Title (default: ``<project> v<version>``).
            notes: Release body; ``None`` asks for generated notes.
            prerelease: Force the pre-release label (default: inferred from
                the version).
            draft: Create the release unpublished.
            destination: Override for the resolved file destination.
            release_destination: Override for ``config.release_destination``.
            upload_config: Extra options passed to the uploader.

        Returns:
            str | None: The release URL on the platform path, ``None`` on the
                file path.

        Raises:
            ConfigurationError: If the project is not initialized.
            PublishError: If publishing to the platform fails.
            UploadError: If the file transfer fails.
            ReleaseError: If an enabled installer is missing, or if nothing
                was built.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)

        resolved_tag = tag or f"v{self._config.version}"
        preflight = PublishService.preflight_release(
            self._config, tag=resolved_tag, release_destination=release_destination
        )
        assets = list(preflight.assets)
        url = PublishService.publish_release(
            self._config,
            assets,
            tag=resolved_tag,
            title=title or f"{self._config.project_name} v{self._config.version}",
            notes=notes,
            prerelease=(
                is_prerelease(self._config.version)
                if prerelease is None
                else prerelease
            ),
            draft=draft,
            destination=destination,
            release_destination=release_destination,
            upload_config=upload_config,
        )
        self._logger.info("Release %s published: %s", resolved_tag, url)
        return url

    def release(
        self,
        bundle_dir: Path,
        *,
        publish: bool = False,
        required: bool = False,
    ) -> Path:
        """Package a compiled bundle into a signed TUF repository.

        Reads app name, version and tufup directories from the config.
        When ``publish`` is True, the repository tree is transferred via the
        configured uploader (``update_repo_url`` + repo_destination).

        Args:
            bundle_dir: Directory containing the compiled application artifacts.
            publish: When True, upload the repository/ tree to ``update_repo_url``.
                Deprecated since 4.1.0 (removed in v5): run ``run_pipeline()``
                then ``ezcompiler publish update`` / ``ezcompiler publish
                release`` instead.
            required: Mark this version as mandatory for TUF clients.

        Returns:
            Path: The local ``repository/`` tree produced by tufup.

        Raises:
            ConfigurationError: If project not initialized.
            ReleaseError: If release packaging or remote publishing fails.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)
        if publish:
            import warnings  # noqa: PLC0415

            warnings.warn(
                "release(publish=True) is deprecated: run run_pipeline() "
                "then `ezcompiler publish update` / `ezcompiler publish "
                "release`. run_pipeline() performs no remote transfer.",
                DeprecationWarning,
                stacklevel=2,
            )
        repo_dir = TufService.repo_dir(self._config)
        keys_dir = TufService.keys_dir(self._config)
        return ReleaseService.release_and_publish(
            bundle_dir=bundle_dir,
            app_name=self._config.project_name,
            version=self._config.version,
            repo_dir=repo_dir,
            publish=publish,
            upload_type=self._config.repo_destination if publish else None,
            destination=self._config.repo_endpoint if publish else None,
            releaser_config={
                "keys_dir": keys_dir,
                "expiration_days": self._config.tuf_expiration_days,
            },
            required=required,
        )

    def init_release(self) -> bool:
        """Initialize the TUF keys/repo from the current config.

        Explicit action - never called by run_pipeline().

        Returns:
            bool: True if the init ran, False if the keys were already present
                (skip).

        Raises:
            ConfigurationError: If project not initialized.
            ReleaseError: If TUF initialization fails.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)
        repo_dir = TufService.repo_dir(self._config)
        keys_dir = TufService.keys_dir(self._config)
        return ReleaseService.init_release(
            app_name=self._config.project_name,
            repo_dir=repo_dir,
            keys_dir=keys_dir,
            releaser_config={
                "keys_dir": keys_dir,
                "expiration_days": self._config.tuf_expiration_days,
            },
        )

    def refresh_release_expiration(
        self,
        *,
        roles: tuple[str, ...] = ("targets", "snapshot", "timestamp"),
        days: int | None = None,
    ) -> Path:
        """Re-sign TUF metadata to extend expiration without a new release.

        Native tufup keep-alive for projects updated irregularly: bumps the
        expiration date of the short-lived roles and re-publishes, so clients
        keep trusting the repository between releases.

        Args:
            roles: Role names to refresh (default: targets/snapshot/timestamp).
            days: Days from now. None → the config's ``tuf_expiration_days``
                (or tufup defaults) for each role.

        Returns:
            Path: The local TUF repository directory.

        Raises:
            ConfigurationError: If project not initialized.
            ReleaseError: If the refresh fails.
            SigningKeyError: If signing keys are missing.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)
        repo_dir = TufService.repo_dir(self._config)
        keys_dir = TufService.keys_dir(self._config)
        repo = ReleaseService.refresh_expiration(
            app_name=self._config.project_name,
            repo_dir=repo_dir,
            keys_dir=keys_dir,
            roles=roles,
            days=days,
            releaser_config={
                "keys_dir": keys_dir,
                "expiration_days": self._config.tuf_expiration_days,
            },
        )
        self._printer.success("TUF metadata expiration refreshed")
        self._logger.info("TUF metadata expiration refreshed: %s", repo)
        return repo

    def generate_updater(
        self,
        output_dir: Path | str | None = None,
        *,
        patch_config: bool = True,
    ) -> list[Path]:
        """Generate auto-update client files for embedding in the compiled bundle.

        Generates ``update.py``, ``settings.py``, and copies ``root.json``
        from the local TUF repository into ``output_dir``.

        When ``patch_config=True`` (default), the three generated files are
        added to ``config.include_files["files"]`` so they are automatically
        bundled by the next ``run_pipeline()`` call. Call this method BEFORE
        ``run_pipeline()``.

        Args:
            output_dir: Directory where files are written. Defaults to the
                directory containing ``main_file``.
            patch_config: If True, add generated file paths to include_files.

        Returns:
            List of generated file paths [settings.py, update.py, root.json].

        Raises:
            ConfigurationError: If project not initialized.
            UpdaterConfigError: If tuf_enabled=False or root.json absent.
            UpdaterGenerationError: If writing files fails.
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)

        resolved_dir = (
            Path(output_dir)
            if output_dir is not None
            else Path(self._config.main_file).parent
        )

        files = UpdaterService.generate(self._config, resolved_dir)

        if patch_config:
            self._config.include_files["files"].extend(str(f) for f in files)

        self._printer.success(f"Updater files generated in {resolved_dir}")
        self._logger.info("Updater files generated: %s", [str(f) for f in files])

        return files

    def run_pipeline(
        self,
        console: bool = True,
        compiler: str | None = None,
        skip_zip: bool = False,
        skip_release: bool = False,
        skip_installer: bool = False,
        skip_build: bool = False,
        required: bool = False,
    ) -> None:
        """
        Run the build pipeline with visual progress tracking.

        Executes version generation, compilation, optional ZIP creation,
        optional installer build and optional TUF release in sequence with a
        DynamicLayeredProgress display. Publication is not part of the
        pipeline — run ``ezcompiler publish update`` / ``ezcompiler publish
        release`` afterwards.

        Args:
            console: Whether to show console window (default: True)
            compiler: Compiler to use or None for auto-selection
            skip_zip: Skip ZIP archive creation
            skip_release: Skip the TUF release stage
            skip_installer: Skip the installer build stage
            skip_build: Skip version generation and compilation, and resume
                from the existing build in ``output_folder``
            required: Mark the released version as mandatory (needs the TUF
                release stage)

        Raises:
            ConfigurationError: If project not initialized, or required without
                a release stage
            CompilationError: If compilation fails, or no existing build is
                found when ``skip_build`` is set
            VersionError: If version file generation fails
            ZipError: If ZIP creation fails
            ReleaseError: If the release stage fails
            InstallerError: If the installer build fails

        Example:
            >>> compiler = EzCompiler(config)
            >>> compiler.run_pipeline(console=False)
        """
        if not self._config:
            raise ConfigurationError(_MSG_NOT_INITIALIZED)

        # Determine which optional stages to include
        should_zip = not skip_zip
        should_release = not skip_release and self._config.tuf_enabled
        should_installer = not skip_installer and self._config.installer.enabled

        if required and not should_release:
            raise ConfigurationError(
                "required=True only has an effect when the TUF release step "
                "runs (tuf_enabled, without skip_release)."
            )

        # Pre-flight: fail early if release needed but keys absent, or if the
        # version is not above a withdrawn one (before a possibly long compile)
        if should_release:
            self._preflight_release(TufService.keys_dir(self._config))
            TufService.ensure_releasable(
                TufService.repo_dir(self._config), self._config.version
            )

        # Build stages
        stages: list[StageConfig] = cast(
            list["StageConfig"],
            PipelineService.build_stages(
                self._config,
                should_zip=should_zip,
                should_release=should_release,
                should_installer=should_installer,
                should_build=not skip_build,
            ),
        )

        current_phase = "version"
        pipeline_error: Exception | None = None

        with self._printer.wizard.dynamic_layered_progress(stages) as dlp:
            try:
                if skip_build:
                    # Resume from a previous build: no version file, no compile
                    current_phase = "compile"
                    dlp.update_layer("compile", 0, "Checking existing build...")
                    self._compiler_service, self._compilation_result = (
                        self._pipeline_service.reuse_build(
                            config=self._config,
                            compiler=compiler,
                        )
                    )
                    self._logger.info(
                        f"Reusing existing build in {self._config.output_folder}"
                    )
                    dlp.complete_layer("compile")
                else:
                    # Version file
                    current_phase = "version"
                    dlp.update_layer("version", 0, "Processing template...")
                    config_dict = self._config.to_dict()
                    version_file_path = Path(self._config.version_filename)
                    self._template_service.generate_version_file(
                        config_dict, version_file_path
                    )
                    self._logger.info(_MSG_VERSION_OK)
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
                    self._logger.info(_MSG_COMPILED_OK)
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
                        self._logger.info(_MSG_ZIP_OK)
                        dlp.complete_layer("zip")
                    else:
                        # Stage was added but not needed at runtime
                        dlp.update_layer("zip", 0, "Skipped (not needed)")
                        dlp.complete_layer("zip")

                # Installer (Inno Setup setup.exe for first deployment)
                if should_installer:
                    current_phase = "installer"
                    dlp.update_layer("installer", 0, "Building installer...")
                    installer_path = self._pipeline_service.build_installer(
                        config=self._config,
                        compilation_result=self._compilation_result,
                    )
                    self._logger.info(f"Installer built: {installer_path}")
                    dlp.complete_layer("installer")

                # Release (build the local TUF tree; upload is a separate step)
                if should_release:
                    current_phase = "release"
                    dlp.update_layer("release", 0, "Signing bundle...")
                    repository_path = self._pipeline_service.release_artifact(
                        config=self._config,
                        compilation_result=self._compilation_result,
                        required=required,
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
                InstallerError,
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
                "Run `ezcompiler tuf init` first."
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
