# ///////////////////////////////////////////////////////////////
# COMPILER_CONFIG - Configuration dataclass
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Compiler configuration - Configuration dataclass for EzCompiler.

This module provides the CompilerConfig dataclass for centralizing all
configuration parameters needed for project compilation, versioning,
packaging, and distribution.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Local imports
from .exceptions import ConfigurationError

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


@dataclass
class CompilerConfig:
    """
    Configuration class for project compilation.

    Centralizes all configuration parameters needed for project
    compilation, version generation, packaging, and distribution.
    Validates configuration on initialization and provides helper
    properties for file paths.

    Attributes:
        version: Project version (e.g., "1.0.0")
        project_name: Name of the project
        main_file: Path to main Python file
        include_files: Dict with 'files' and 'folders' lists
        output_folder: Path to output directory
        version_filename: Name of version info file (default: "version_info.txt")
        project_description: Project description
        company_name: Company or organization name
        author: Project author
        icon: Path to project icon
        packages: List of Python packages to include
        includes: List of modules to include
        excludes: List of modules to exclude
        console: Show console window in compiled app (default: True)
        compiler: Compiler to use - "auto", "Cx_Freeze", "PyInstaller", "Nuitka"
        zip_needed: Create zip archive (default: True)
        repo_needed: Use repository (default: False)
        upload_structure: Upload target - "disk" or "server"
        repo_path: Repository path (default: "releases")
        server_url: Server upload URL
        optimize: Optimize code (default: True)
        strip: Strip debug info (default: False)
        debug: Enable debug mode (default: False)
        compiler_options: Compiler-specific options dict (default: {})

    Example:
        >>> config = CompilerConfig(
        ...     version="1.0.0",
        ...     project_name="MyApp",
        ...     main_file="main.py",
        ...     include_files={"files": ["config.yaml"], "folders": ["lib"]},
        ...     output_folder=Path("dist")
        ... )
        >>> config_dict = config.to_dict()
    """

    # ////////////////////////////////////////////////
    # REQUIRED FIELDS
    # ////////////////////////////////////////////////

    version: str
    project_name: str
    main_file: str
    include_files: dict[str, list[str]]
    output_folder: Path

    # ////////////////////////////////////////////////
    # OPTIONAL FIELDS WITH DEFAULTS
    # ////////////////////////////////////////////////

    version_filename: str = "version_info.txt"
    project_description: str = ""
    company_name: str = ""
    author: str = ""
    icon: str = ""
    packages: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)

    # ////////////////////////////////////////////////
    # COMPILATION OPTIONS
    # ////////////////////////////////////////////////

    console: bool = True
    compiler: str = "auto"  # "auto", "Cx_Freeze", "PyInstaller", "Nuitka"
    zip_needed: bool = True
    repo_needed: bool = False

    # ////////////////////////////////////////////////
    # UPLOAD OPTIONS
    # ////////////////////////////////////////////////

    upload_structure: str = "disk"  # "disk" or "server"
    repo_path: str = "releases"
    server_url: str = ""

    # ////////////////////////////////////////////////
    # ADVANCED OPTIONS
    # ////////////////////////////////////////////////

    optimize: bool = True
    strip: bool = False
    debug: bool = False

    # ////////////////////////////////////////////////
    # SECURE RELEASE OPTIONS (tufup)
    # ////////////////////////////////////////////////

    release_needed: bool = False
    release_type: str = "tufup"
    tufup_repo_dir: Path | None = None
    tufup_keys_dir: Path | None = None
    update_repo_url: str | None = None
    r2_bucket: str = ""
    r2_remote_prefix: str = ""

    # ////////////////////////////////////////////////
    # COMPILER-SPECIFIC OPTIONS
    # ////////////////////////////////////////////////

    compiler_options: dict[str, Any] = field(default_factory=dict)

    # ////////////////////////////////////////////////
    # INITIALIZATION AND VALIDATION
    # ////////////////////////////////////////////////

    def __post_init__(self) -> None:
        """
        Validate configuration after initialization.

        Called automatically after __init__ to validate all fields
        and ensure configuration is valid before use.

        Raises:
            ConfigurationError: If any validation fails
        """
        self._validate_required_fields()
        self._validate_include_files()
        self._validate_paths()
        self._validate_compiler_option()

    def _validate_required_fields(self) -> None:
        """
        Validate required fields are not empty.

        Raises:
            ConfigurationError: If any required field is empty
        """
        if not self.version:
            raise ConfigurationError("Version cannot be empty")
        if not self.project_name:
            raise ConfigurationError("Project name cannot be empty")
        if not self.main_file:
            raise ConfigurationError("Main file cannot be empty")

    def _validate_include_files(self) -> None:
        """
        Validate and normalize include_files payload.

        Expected format:
            {"files": ["..."], "folders": ["..."]}

        Raises:
            ConfigurationError: If include_files structure is invalid
        """
        if not isinstance(self.include_files, dict):
            raise ConfigurationError("include_files must be a dictionary")

        files = self.include_files.get("files", [])
        folders = self.include_files.get("folders", [])

        if not isinstance(files, list):
            raise ConfigurationError("include_files['files'] must be a list")
        if not isinstance(folders, list):
            raise ConfigurationError("include_files['folders'] must be a list")

        if not all(isinstance(item, str) and item.strip() for item in files):
            raise ConfigurationError(
                "include_files['files'] must contain non-empty strings"
            )
        if not all(isinstance(item, str) and item.strip() for item in folders):
            raise ConfigurationError(
                "include_files['folders'] must contain non-empty strings"
            )

        # Normalize to canonical shape even when keys are missing.
        self.include_files = {
            "files": files,
            "folders": folders,
        }

    def _validate_paths(self) -> None:
        """
        Validate file and folder paths.

        Ensures main file exists and output folder is accessible.
        Converts output_folder and tufup dirs to Path if they are strings.

        Raises:
            ConfigurationError: If main file doesn't exist
        """
        if not Path(self.main_file).exists():
            raise ConfigurationError(f"Main file not found: {self.main_file}")

        if isinstance(self.output_folder, str):
            self.output_folder = Path(self.output_folder)

        if isinstance(self.tufup_repo_dir, str):
            self.tufup_repo_dir = Path(self.tufup_repo_dir)

        if isinstance(self.tufup_keys_dir, str):
            self.tufup_keys_dir = Path(self.tufup_keys_dir)

    def _validate_compiler_option(self) -> None:
        """
        Validate compiler option.

        Ensures compiler is one of the supported options.

        Raises:
            ConfigurationError: If compiler is not valid
        """
        valid_compilers = ["auto", "Cx_Freeze", "PyInstaller", "Nuitka"]
        if self.compiler not in valid_compilers:
            raise ConfigurationError(
                f"Invalid compiler: {self.compiler}. Must be one of {valid_compilers}"
            )

    # ////////////////////////////////////////////////
    # PATH HELPER PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def version_file(self) -> Path:
        """
        Get the full path to the version file.

        Returns:
            Path: Full path to version_info.txt in output folder
        """
        return self.output_folder / self.version_filename

    @property
    def zip_file_path(self) -> Path:
        """
        Get the path to the zip file.

        Uses the project name as the zip filename, placed next to the
        output folder (e.g., dist/MyApp.zip).

        Returns:
            Path: Path to the zip archive file
        """
        return self.output_folder.parent / f"{self.project_name}.zip"

    # ////////////////////////////////////////////////
    # RELEASE HELPER PROPERTIES
    # ////////////////////////////////////////////////

    @property
    def resolved_upload_destination(self) -> str | None:
        """Destination unifiée de l'upload.

        Priorité : update_repo_url, puis fallback rétro-compat selon la
        structure (server_url pour server, repo_path pour disk).

        Returns:
            str | None: Destination résolue, ou None si aucune n'est définie.
        """
        if self.update_repo_url:
            return self.update_repo_url
        if self.upload_structure == "server":
            return self.server_url or None
        return self.repo_path or None

    # ////////////////////////////////////////////////
    # SERIALIZATION METHODS
    # ////////////////////////////////////////////////

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Creates a comprehensive dictionary representation of the
        configuration with nested structures for compilation, upload,
        and advanced settings.

        Returns:
            dict[str, Any]: Configuration as nested dictionary

        Example:
            >>> config = CompilerConfig(...)
            >>> config_dict = config.to_dict()
            >>> print(config_dict["version"])
            '1.0.0'
        """
        return {
            "version": self.version,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "company_name": self.company_name,
            "author": self.author,
            "main_file": self.main_file,
            "icon": self.icon,
            "version_filename": self.version_filename,
            "output_folder": str(self.output_folder),
            "include_files": self.include_files,
            "packages": self.packages,
            "includes": self.includes,
            "excludes": self.excludes,
            "compilation": {
                "console": self.console,
                "compiler": self.compiler,
                "zip_needed": self.zip_needed,
                "repo_needed": self.repo_needed,
            },
            "upload": {
                "structure": self.upload_structure,
                "repo_path": self.repo_path,
                "server_url": self.server_url,
            },
            "advanced": {
                "optimize": self.optimize,
                "strip": self.strip,
                "debug": self.debug,
            },
            "release": {
                "release_needed": self.release_needed,
                "release_type": self.release_type,
                "tufup_repo_dir": str(self.tufup_repo_dir)
                if self.tufup_repo_dir
                else None,
                "tufup_keys_dir": str(self.tufup_keys_dir)
                if self.tufup_keys_dir
                else None,
                "update_repo_url": self.update_repo_url,
                "r2_bucket": self.r2_bucket,
                "r2_remote_prefix": self.r2_remote_prefix,
            },
            "compiler_options": self.compiler_options,
        }

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> CompilerConfig:
        """
        Create configuration from dictionary.

        Flattens nested structures (compilation, upload, advanced)
        and creates a new CompilerConfig instance. Handles backward
        compatibility for 'version_file' key.

        Args:
            config_dict: Configuration dictionary with nested structures

        Returns:
            CompilerConfig: New configuration instance

        Raises:
            ConfigurationError: If required fields are missing or invalid

        Example:
            >>> config_dict = {
            ...     "version": "1.0.0",
            ...     "project_name": "MyApp",
            ...     "main_file": "main.py",
            ...     "include_files": {"files": [], "folders": []},
            ...     "output_folder": "dist"
            ... }
            >>> config = CompilerConfig.from_dict(config_dict)
        """
        config_copy = config_dict.copy()

        # Flatten nested structures
        compilation = config_copy.get("compilation", {})
        upload = config_copy.get("upload", {})
        advanced = config_copy.get("advanced", {})
        release = config_copy.get("release", {})

        config_copy.update(compilation)
        config_copy.update(upload)
        config_copy.update(advanced)
        config_copy.update(release)

        # Remove nested keys
        config_copy.pop("compilation", None)
        config_copy.pop("upload", None)
        config_copy.pop("advanced", None)
        config_copy.pop("release", None)

        # Remap nested key names to dataclass field names
        # "upload.structure" becomes "upload_structure" after flattening
        if "structure" in config_copy:
            if "upload_structure" not in config_copy:
                config_copy["upload_structure"] = config_copy.pop("structure")
            else:
                config_copy.pop("structure")

        # Handle backward compatibility
        if "version_file" in config_copy and "version_filename" not in config_copy:
            config_copy["version_filename"] = config_copy.pop("version_file")

        return cls(**config_copy)
