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
        repo_destination: TUF repo upload backend - "disk" | "server" | "r2"
        release_destination: Zip installer upload backend - "disk" | "server"
        repo_endpoint: Endpoint for TUF repo upload (path, URL, or "bucket/prefix")
        release_endpoint: Endpoint for zip installer upload (path or URL)
        optimize: Optimize code (default: True)
        strip: Strip debug info (default: False)
        debug: Enable debug mode (default: False)
        compiler_options: Compiler-specific options dict (default: {})
        tuf_enabled: Enable TUF secure release pipeline (default: False)
        tuf_repo_dir: Path to TUF repository directory
        tuf_keys_dir: Path to TUF keys directory

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

    # ////////////////////////////////////////////////
    # UPLOAD OPTIONS
    # ////////////////////////////////////////////////

    repo_destination: RepoDestination = "disk"
    release_destination: ReleaseDestination = "disk"
    repo_endpoint: str = ""
    release_endpoint: str = ""
    repo_public_url: str = ""

    # ////////////////////////////////////////////////
    # ADVANCED OPTIONS
    # ////////////////////////////////////////////////

    optimize: bool = True
    strip: bool = False
    debug: bool = False

    # ////////////////////////////////////////////////
    # SECURE RELEASE OPTIONS (tufup)
    # ////////////////////////////////////////////////

    tuf_enabled: bool = False
    tuf_repo_dir: Path | None = None
    tuf_keys_dir: Path | None = None

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
        Converts output_folder and tuf dirs to Path if they are strings.

        Raises:
            ConfigurationError: If main file doesn't exist
        """
        if not Path(self.main_file).exists():
            raise ConfigurationError(f"Main file not found: {self.main_file}")

        if isinstance(self.output_folder, str):
            self.output_folder = Path(self.output_folder)

        if isinstance(self.tuf_repo_dir, str):
            self.tuf_repo_dir = Path(self.tuf_repo_dir)

        if isinstance(self.tuf_keys_dir, str):
            self.tuf_keys_dir = Path(self.tuf_keys_dir)

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
        Validate upload destination backends and require endpoints for non-disk targets.

        The TUF repository may be uploaded to disk, server or r2; the release
        zip only to disk or server. Any other value is rejected.
        Non-disk destinations require the matching endpoint to be non-empty.

        Raises:
            ConfigurationError: If a destination is not supported or endpoint is missing
        """
        valid_repo = ["disk", "server", "r2"]
        if self.repo_destination not in valid_repo:
            raise ConfigurationError(
                f"Invalid repo_destination: {self.repo_destination}. "
                f"Must be one of {valid_repo}"
            )

        valid_release = ["disk", "server", "r2"]
        if self.release_destination not in valid_release:
            raise ConfigurationError(
                f"Invalid release_destination: {self.release_destination}. "
                f"Must be one of {valid_release}"
            )

        if self.repo_destination != "disk" and not self.repo_endpoint:
            raise ConfigurationError(
                f"repo_endpoint is required when repo_destination='{self.repo_destination}'. "
                "For 'server': provide a URL. For 'r2': provide 'bucket/prefix'."
            )

        if self.release_destination != "disk" and not self.release_endpoint:
            raise ConfigurationError(
                f"release_endpoint is required when release_destination='{self.release_destination}'. "
                "For 'server': provide a URL. For 'r2': provide 'bucket/prefix'."
            )

        if (
            self.tuf_enabled
            and self.repo_destination != "disk"
            and not self.repo_public_url
        ):
            raise ConfigurationError(
                f"repo_public_url is required when tuf_enabled=True and "
                f"repo_destination='{self.repo_destination}'. "
                "Provide the public URL where the TUF repository is served "
                "(e.g. 'https://updates.myapp.com')."
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
        """Destination résolue pour l'arbre TUF."""
        return self.repo_endpoint or None

    @property
    def resolved_release_destination(self) -> str | None:
        """Destination résolue pour le zip installeur."""
        return self.release_endpoint or None

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
            },
            "upload": {
                "repo_destination": self.repo_destination,
                "release_destination": self.release_destination,
                "repo_endpoint": self.repo_endpoint,
                "release_endpoint": self.release_endpoint,
                "repo_public_url": self.repo_public_url,
            },
            "advanced": {
                "optimize": self.optimize,
                "strip": self.strip,
                "debug": self.debug,
            },
            "release": {
                "tuf_enabled": self.tuf_enabled,
                "tuf_repo_dir": str(self.tuf_repo_dir) if self.tuf_repo_dir else None,
                "tuf_keys_dir": str(self.tuf_keys_dir) if self.tuf_keys_dir else None,
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
                "tuf_enabled=True. Pour le flux sans release, le zip dépend du "
                "résultat de compilation."
            )

        # Migration errors for removed upload fields.
        _removed_upload = {
            "repo_path": "'repo_path' supprimé. Utiliser 'upload.repo_endpoint'.",
            "server_url": "'server_url' supprimé. Utiliser 'upload.repo_endpoint' ou 'upload.release_endpoint'.",
            "update_repo_url": "'update_repo_url' supprimé. Utiliser 'upload.repo_endpoint'.",
            "r2_bucket": "'r2_bucket' supprimé. Utiliser 'upload.repo_endpoint' au format \"bucket/prefix\".",
            "r2_remote_prefix": "'r2_remote_prefix' supprimé. Voir 'upload.repo_endpoint' (format \"bucket/prefix\").",
        }
        for key, msg in _removed_upload.items():
            if key in config_copy:
                raise ConfigurationError(msg)

        # Migration errors for removed release fields.
        _removed_release = {
            "release_needed": "'release_needed' renommé en 'tuf_enabled'.",
            "release_type": "'release_type' supprimé. tufup est l'unique backend de release.",
            "repo_needed": "'repo_needed' supprimé. Utiliser 'release.tuf_enabled'.",
        }
        for key, msg in _removed_release.items():
            if key in config_copy:
                raise ConfigurationError(msg)

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
