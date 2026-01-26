# ///////////////////////////////////////////////////////////////
# EZCOMPILER - Project compilation orchestrator
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
EzCompiler - Main orchestration class for project compilation.

This module provides the high-level EzCompiler class that coordinates
compilation, version generation, setup file creation, and artifact
uploading using the modular component system.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path
from typing import Any, Literal

# Third-party imports
from ezpl import EzLogger, Ezpl, EzPrinter
from InquirerPy import prompt

# Local imports
from .compilers import CxFreezeCompiler, PyInstallerCompiler
from .core import (
    CompilationError,
    CompilerConfig,
    ConfigurationError,
    EzCompilerError,
)
from .generators import SetupGenerator, VersionGenerator
from .uploaders import UploaderFactory
from .utils import ValidationUtils, ZipUtils

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

    def __init__(self, config: CompilerConfig | None = None) -> None:
        """
        Initialize the EzCompiler orchestrator.

        Sets up logging via Ezpl, initializes component generators,
        and prepares for compilation workflow.

        Args:
            config: Optional CompilerConfig instance (can be set later via init_project)

        Note:
            Ezpl logging is configured with 1-day rotation, 14-day retention,
            and zip compression.
        """
        # Configuration management
        self.config = config

        # Component generators
        self._cx_freeze_compiler = None
        self._pyinstaller_compiler = None
        self._version_generator = VersionGenerator()
        self._setup_generator = SetupGenerator()

        # Logging via Ezpl
        self._ezpl = Ezpl(log_file=Path("ezcompiler.log"))
        self._ezpl.configure(
            log_rotation="1 day",
            log_retention="14 days",
            log_compression="zip",
        )
        self._ezpl.set_level("INFO")
        self._printer: EzPrinter = self._ezpl.get_printer()
        self._logger: EzLogger = self._ezpl.get_logger()

        # Compilation state
        self._compiler_choice = None
        self._zip_needed = False

    # ////////////////////////////////////////////////
    # LOGGING ACCESSOR PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def ezpl(self) -> Ezpl:
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

        except Exception as e:
            self._printer.error(f"Failed to initialize project: {e}")
            self._logger.error(f"Failed to initialize project: {e}")
            raise

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

            # Generate using VersionGenerator
            version_file_path = Path(name)

            # Prepare config dict for version generation
            version_config = {
                "version": self.config.version,
                "company_name": self.config.company_name,
                "project_description": self.config.project_description,
                "project_name": self.config.project_name,
            }

            self._version_generator.generate(
                config=version_config, output_path=version_file_path, format_type="txt"
            )

            self._printer.success("Version file generated successfully")
            self._logger.info("Version file generated successfully")

        except Exception as e:
            self._printer.error(f"Failed to generate version file: {e}")
            self._logger.error(f"Failed to generate version file: {e}")
            raise

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

            # Generate using SetupGenerator
            config_dict = self.config.to_dict()
            self._setup_generator.generate_from_config(
                config=config_dict, output_dir=Path(file_path).parent
            )

            self._printer.success("Setup file generated successfully")
            self._logger.info("Setup file generated successfully")

        except Exception as e:
            self._printer.error(f"Failed to generate setup file: {e}")
            self._logger.error(f"Failed to generate setup file: {e}")
            raise

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
                - None: Prompt user for choice

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

            # Determine compiler choice
            if compiler:
                self._compiler_choice = compiler
            else:
                self._compiler_choice = self._choose_compiler()

            # Validate compiler choice
            if not ValidationUtils.validate_compiler_name(self._compiler_choice):
                raise CompilationError(f"Invalid compiler: {self._compiler_choice}")

            # Compile using appropriate compiler
            if self._compiler_choice == "Cx_Freeze":
                self._cx_freeze_compiler = CxFreezeCompiler(config=self.config)
                self._cx_freeze_compiler.compile(console=console)
                self._zip_needed = True

            elif self._compiler_choice == "PyInstaller":
                self._pyinstaller_compiler = PyInstallerCompiler(config=self.config)
                self._pyinstaller_compiler.compile(console=console)
                self._zip_needed = "--onefile" not in sys.argv

            else:
                raise CompilationError(f"Unsupported compiler: {self._compiler_choice}")

            self._printer.success("Project compiled successfully")
            self._logger.info("Project compiled successfully")

        except Exception as e:
            self._printer.error(f"Compilation failed: {e}")
            self._logger.error(f"Compilation failed: {e}")
            raise

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

            if not self._zip_needed:
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

        except Exception as e:
            self._printer.error(f"Failed to create ZIP archive: {e}")
            self._logger.error(f"Failed to create ZIP archive: {e}")
            raise

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

            # Validate upload structure
            if not ValidationUtils.validate_upload_structure(structure):
                raise EzCompilerError(f"Invalid upload structure: {structure}")

            # Determine source file (ZIP or directory)
            if self._zip_needed:
                source_file = f"{self.config.output_folder}.zip"
            else:
                source_file = self.config.output_folder

            # Create uploader with appropriate configuration
            uploader_config = upload_config or {}
            if structure == "disk":
                uploader_config["destination_path"] = str(repo_path)
            elif structure == "server":
                uploader_config["server_url"] = str(repo_path)

            uploader = UploaderFactory.create_uploader(structure, uploader_config)

            # Perform upload
            uploader.upload(source_path=Path(source_file), destination=str(repo_path))

            self._printer.success(f"Project uploaded successfully to {structure}")
            self._logger.info(f"Project uploaded successfully to {structure}")

        except Exception as e:
            self._printer.error(f"Upload failed: {e}")
            self._logger.error(f"Upload failed: {e}")
            raise

    # ////////////////////////////////////////////////
    # PRIVATE HELPER METHODS
    # ////////////////////////////////////////////////

    def _choose_compiler(self) -> str:
        """
        Prompt user to choose a compiler.

        Checks command-line arguments for compiler flags (-cxf, -pyi) or
        prompts user interactively.

        Returns:
            str: Chosen compiler name ("Cx_Freeze" or "PyInstaller")

        Note:
            Command-line flags take precedence over interactive prompt.
        """
        try:
            # Check command line arguments first
            if "-cxf" in sys.argv:
                return "Cx_Freeze"
            elif "-pyi" in sys.argv:
                return "PyInstaller"

            # Prompt user for choice
            questions = [
                {
                    "type": "list",
                    "name": "compiler",
                    "message": "Which compiler to use?",
                    "choices": ["Cx_Freeze", "PyInstaller"],
                    "default": "Cx_Freeze",
                }
            ]

            result = prompt(questions)
            return result["compiler"]  # type: ignore[return-value]

        except Exception as e:
            self._printer.error(f"Failed to choose compiler: {e}")
            self._logger.error(f"Failed to choose compiler: {e}")
            raise

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

    # ////////////////////////////////////////////////
    # LEGACY BACKWARD COMPATIBILITY METHODS
    # ////////////////////////////////////////////////

    def _compile_with_pyinstaller(self, console: bool) -> None:
        """
        Legacy method - use compile_project() instead.

        Args:
            console: Whether to show console window
        """
        self.compile_project(console=console, compiler="PyInstaller")

    def _compile_with_cxfreeze(self, console: bool) -> None:
        """
        Legacy method - use compile_project() instead.

        Args:
            console: Whether to show console window
        """
        self.compile_project(console=console, compiler="Cx_Freeze")

    def _show_prompt(
        self,
        name: str,
        message: str,
        choices: list[str],
        default: str,
        vtype: str = "list",
    ) -> str:
        """
        Legacy method - use _choose_compiler() instead.

        Args:
            name: Prompt name
            message: Prompt message
            choices: List of choices
            default: Default choice
            vtype: Question type

        Returns:
            str: User's selected choice
        """
        questions = [
            {
                "type": vtype,
                "name": name,
                "message": message,
                "choices": choices,
                "default": default,
            }
        ]
        result = prompt(questions)
        return result[name]  # type: ignore[return-value]
