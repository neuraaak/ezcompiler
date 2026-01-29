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
from pathlib import Path
from typing import Any, Literal

# Third-party imports
from ezpl import EzLogger, EzPrinter

# Local imports
from ..services import (
    CompilationResult,
    CompilerService,
    TemplateService,
    UploaderService,
)
from ..shared.compiler_config import CompilerConfig
from ..shared.exceptions import (
    CompilationError,
    ConfigurationError,
    TemplateError,
    UploadError,
    VersionError,
)
from ..shared.exceptions.utils.zip_exceptions import ZipError
from ..utils.zip_utils import ZipUtils
from . import configure_ezpl, get_logger, get_printer

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
        config: CompilerConfig instance with project settings
        ezpl: Ezpl logging instance
        printer: EzPrinter for console output
        logger: EzLogger for file logging

    Example:
        >>> config = CompilerConfig(...)
        >>> compiler = EzCompiler(config)
        >>> compiler.compile_project()
        >>> compiler.zip_compiled_project()
        >>> compiler.upload_to_repo("disk", "releases")
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(
        self,
        config: CompilerConfig | None = None,
        log_file: Path | None = None,
        log_rotation: str = "1 day",
        log_retention: str = "14 days",
        log_compression: str = "zip",
        log_level: str = "INFO",
    ) -> None:
        """
        Initialize the EzCompiler orchestrator.

        Sets up logging via ezpl (configured in interfaces/__init__.py),
        initializes service instances, and prepares for compilation workflow.

        Args:
            config: Optional CompilerConfig instance (can be set later via init_project)
            log_file: Optional path to log file (default: None)
            log_rotation: Log rotation setting (default: "1 day")
            log_retention: Log retention setting (default: "14 days")
            log_compression: Log compression setting (default: "zip")
            log_level: Log level (default: "INFO")

        Note:
            Ezpl logging is configured via interfaces/__init__.py and can be
            accessed via get_ezpl(), get_printer(), and get_logger().
        """
        # Configuration management
        self.config = config

        # Configure ezpl via interfaces module
        self._ezpl = configure_ezpl(
            log_file=log_file,
            log_rotation=log_rotation,
            log_retention=log_retention,
            log_compression=log_compression,
            log_level=log_level,
        )
        self._printer: EzPrinter = get_printer()
        self._logger: EzLogger = get_logger()

        # Service instances
        self._compiler_service: CompilerService | None = None
        self._template_service = TemplateService()
        self._uploader_service = UploaderService()

        # Compilation state
        self._compilation_result: CompilationResult | None = None

    # ////////////////////////////////////////////////
    # LOGGING ACCESSOR PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def ezpl(self) -> Any:
        """
        Get the Ezpl logging instance.

        Returns:
            Ezpl: Ezpl instance for logging configuration
        """
        return self._ezpl

    @property
    def printer(self) -> EzPrinter:
        """
        Get the console printer instance.

        Returns:
            EzPrinter: Printer for console output
        """
        return self._printer

    @property
    def logger(self) -> EzLogger:
        """
        Get the file logger instance.

        Returns:
            EzLogger: Logger for file output
        """
        return self._logger

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
            self.config = CompilerConfig(**config_dict)

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
            if not self.config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Generate using TemplateService
            config_dict = self.config.to_dict()
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
            if not self.config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Generate using TemplateService
            config_dict = self.config.to_dict()
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
            if not self.config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Create compiler service and compile
            self._compiler_service = CompilerService(self.config)
            self._compilation_result = self._compiler_service.compile(
                console=console,
                compiler=compiler,  # type: ignore[arg-type]
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
            if not self.config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Check if ZIP is needed from compilation result
            zip_needed = (
                self._compilation_result.zip_needed
                if self._compilation_result
                else self.config.zip_needed
            )

            if not zip_needed:
                self._printer.info("ZIP not needed for this compilation type")
                return

            # Create ZIP archive using ZipUtils
            zip_file_path = f"{self.config.output_folder}.zip"

            ZipUtils.create_zip_archive(
                source_path=self.config.output_folder,
                output_path=zip_file_path,
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

    def upload_to_repo(
        self,
        structure: Literal["server", "disk"],
        repo_path: Path | str,
        upload_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Upload compiled project to repository.

        Uploads the compiled artifact (ZIP or directory) to the specified
        repository using the appropriate uploader (disk or server).

        Args:
            structure: Upload type - "server" for HTTP/HTTPS, "disk" for local
            repo_path: Repository path or server URL
            upload_config: Additional uploader configuration options

        Raises:
            ConfigurationError: If project not initialized
            EzCompilerError: If upload structure is invalid

        Example:
            >>> compiler.upload_to_repo("disk", "releases/")
            >>> compiler.upload_to_repo("server", "https://example.com/upload")
        """
        try:
            if not self.config:
                raise ConfigurationError(
                    "Project not initialized. Call init_project() first."
                )

            # Determine source file (ZIP or directory)
            zip_needed = (
                self._compilation_result.zip_needed
                if self._compilation_result
                else self.config.zip_needed
            )

            if zip_needed:
                source_file = f"{self.config.output_folder}.zip"
            else:
                source_file = self.config.output_folder

            # Perform upload using UploaderService
            UploaderService.upload(
                source_path=Path(source_file),
                upload_type=structure,
                destination=str(repo_path),
                upload_config=upload_config,
            )

            self._printer.success(f"Project uploaded successfully to {structure}")
            self._logger.info(f"Project uploaded successfully to {structure}")

        except (ConfigurationError, UploadError):
            raise
        except Exception as e:
            self._printer.error(f"Upload failed: {e}")
            self._logger.error(f"Upload failed: {e}")
            raise UploadError(f"Upload failed: {e}") from e

    # ////////////////////////////////////////////////
    # PRIVATE HELPER METHODS
    # ////////////////////////////////////////////////

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
