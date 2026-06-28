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
from typing import TYPE_CHECKING, Any

# Local imports
from .exceptions import ConfigurationError

if TYPE_CHECKING:
    from ..types import ReleaseDestination, RepoDestination

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
        repo_needed: Use repository (default: False)
        repo_destination: TUF repo upload backend - "disk" | "server" | "r2"
        release_destination: Zip installer upload backend - "disk" | "server"
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
    repo_needed: bool = False

    # ////////////////////////////////////////////////
    # UPLOAD OPTIONS
    # ////////////////////////////////////////////////

    repo_destination: RepoDestination = "disk"
    release_destination: ReleaseDestination = "disk"
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
        self._validate_destinations()

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

    def _validate_destinations(self) -> None:
        """
        Validate upload destination backends.

        The TUF repository may be uploaded to disk, server or r2; the release
        zip only to disk or server. Any other value is rejected.

        Raises:
            ConfigurationError: If a destination is not supported
        """
        valid_repo = ["disk", "server", "r2"]
        if self.repo_destination not in valid_repo:
            raise ConfigurationError(
                f"Invalid repo_destination: {self.repo_destination}. "
                f"Must be one of {valid_repo}"
            )

        valid_release = ["disk", "server"]
        if self.release_destination not in valid_release:
            raise ConfigurationError(
                f"Invalid release_destination: {self.release_destination}. "
                f"Must be one of {valid_release}"
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
    def resolved_repo_destination(self) -> str | None:
        """Destination résolue pour l'arbre TUF.

        Priorité : update_repo_url, puis server_url / repo_path selon repo_destination.
        """
        if self.update_repo_url:
            return self.update_repo_url
        if self.repo_destination == "server":
            return self.server_url or None
        return self.repo_path or None

    @property
    def resolved_release_destination(self) -> str | None:
        """Destination résolue pour le zip installeur."""
        if self.release_destination == "server":
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
                "repo_needed": self.repo_needed,
            },
            "upload": {
                "repo_destination": self.repo_destination,
                "release_destination": self.release_destination,
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

        # "upload.structure" / "upload_structure" supprimés (breaking).
        if "structure" in config_copy or "upload_structure" in config_copy:
            raise ConfigurationError(
                "'upload.structure' / 'upload_structure' a été supprimé. "
                "Utiliser 'upload.repo_destination' et 'upload.release_destination'."
            )

        if "zip_needed" in config_copy:
            raise ConfigurationError(
                "'zip_needed' a été supprimé. Le zip est toujours produit quand "
                "release_needed=True. Pour le flux sans release, le zip dépend du "
                "résultat de compilation."
            )

        # Handle backward compatibility
        if "version_file" in config_copy and "version_filename" not in config_copy:
            config_copy["version_filename"] = config_copy.pop("version_file")

        # Reject unknown keys with a clear error
        import dataclasses as _dc

        valid_fields = {f.name for f in _dc.fields(cls)}
        unknown = set(config_copy) - valid_fields
        if unknown:
            raise ConfigurationError(
                f"Unknown configuration key(s): {sorted(unknown)}. "
                "Check your config file for typos or removed keys."
            )

        return cls(**config_copy)
