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
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Mapping compiler name -> per-compiler config section key.
# Only the section matching config.compiler is applied; the others may
# coexist in the file as ready-to-use alternative configurations.
COMPILER_SECTION_KEYS: dict[str, str] = {
    "PyInstaller": "pyinstaller",
    "Cx_Freeze": "cx_freeze",
    "Nuitka": "nuitka",
}

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
        compiler: Compiler to use - "" (unset -> prompt), "Cx_Freeze", "PyInstaller", "Nuitka"
        repo_destination: TUF repo upload backend - "disk" | "server" | "r2"
        release_destination: Zip installer upload backend - "disk" | "server"
        repo_endpoint: Endpoint for TUF repo upload (path, URL, or "bucket/prefix")
        release_endpoint: Endpoint for zip installer upload (path or URL)
        optimize: Optimize code (default: True)
        strip: Strip debug info (default: False)
        debug: Enable debug mode (default: False)
        optimize: Optimize code (compiler-specific, set via the compiler section)
        strip: Strip debug info (compiler-specific, set via the compiler section)
        compiler_options: Compiler-specific options dict, populated from the
            per-compiler section ([tool.ezcompiler.<pyinstaller|cx_freeze|nuitka>])
            that matches the selected compiler (default: {})
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
    compiler: str = ""  # "" (unset -> prompt), "Cx_Freeze", "PyInstaller", "Nuitka"

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
    # INSTALLER OPTIONS (Inno Setup)
    # ////////////////////////////////////////////////

    installer_enabled: bool = False
    installer_output_dir: Path | None = None
    installer_iss_path: Path | None = None

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
        self._validate_installer_option()

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

        if isinstance(self.installer_output_dir, str):
            self.installer_output_dir = Path(self.installer_output_dir)

        if isinstance(self.installer_iss_path, str):
            self.installer_iss_path = Path(self.installer_iss_path)

    def _validate_compiler_option(self) -> None:
        """
        Validate compiler option.

        Ensures compiler is one of the supported options. An empty string
        means "unset" (resolved interactively at compile time) and is allowed.

        Raises:
            ConfigurationError: If compiler is not valid
        """
        valid_compilers = ["Cx_Freeze", "PyInstaller", "Nuitka"]
        if self.compiler and self.compiler not in valid_compilers:
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

    def _validate_installer_option(self) -> None:
        """
        Validate installer configuration.

        Ensures installer_iss_path, when provided, points to an existing file.

        Raises:
            ConfigurationError: If installer_iss_path is set but not found
        """
        if (
            self.installer_iss_path is not None
            and not Path(self.installer_iss_path).is_file()
        ):
            raise ConfigurationError(
                f"installer_iss_path not found: {self.installer_iss_path}"
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
        and advanced settings. Compiler-specific options (optimize, strip
        and free-form compiler_options) are emitted under the per-compiler
        section key matching the selected compiler.

        Returns:
            dict[str, Any]: Configuration as nested dictionary

        Example:
            >>> config = CompilerConfig(...)
            >>> config_dict = config.to_dict()
            >>> print(config_dict["version"])
            '1.0.0'
        """
        result: dict[str, Any] = {
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
                "debug": self.debug,
            },
            "release": {
                "tuf_enabled": self.tuf_enabled,
                "tuf_repo_dir": str(self.tuf_repo_dir) if self.tuf_repo_dir else None,
                "tuf_keys_dir": str(self.tuf_keys_dir) if self.tuf_keys_dir else None,
            },
            "installer": {
                "installer_enabled": self.installer_enabled,
                "installer_output_dir": (
                    str(self.installer_output_dir)
                    if self.installer_output_dir
                    else None
                ),
                "installer_iss_path": (
                    str(self.installer_iss_path) if self.installer_iss_path else None
                ),
            },
        }

        # Emit compiler-specific options under the per-compiler section key.
        section_key = COMPILER_SECTION_KEYS.get(self.compiler)
        if section_key:
            result[section_key] = {
                "optimize": self.optimize,
                "strip": self.strip,
                **self.compiler_options,
            }

        return result

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

        # Pop per-compiler sections before flattening; only the one matching
        # the selected compiler is applied (the others may coexist as
        # ready-to-use alternatives and are ignored).
        per_compiler_sections = {
            key: config_copy.pop(key)
            for key in COMPILER_SECTION_KEYS.values()
            if key in config_copy
        }

        # 'compiler_options' (flat dict shared across compilers) has been
        # replaced by per-compiler sections.
        if "compiler_options" in config_copy:
            raise ConfigurationError(
                "'compiler_options' a été supprimé. Utiliser une section par "
                "compilateur : [tool.ezcompiler.pyinstaller], "
                "[tool.ezcompiler.cx_freeze] ou [tool.ezcompiler.nuitka]."
            )

        # 'optimize'/'strip' ont quitté 'advanced' pour les sections par compilateur.
        advanced = config_copy.get("advanced", {})
        if "optimize" in advanced or "strip" in advanced:
            raise ConfigurationError(
                "'advanced.optimize' / 'advanced.strip' déplacés vers la section "
                "du compilateur ([tool.ezcompiler.<pyinstaller|cx_freeze|nuitka>])."
            )

        # Flatten nested structures
        compilation = config_copy.get("compilation", {})
        upload = config_copy.get("upload", {})
        release = config_copy.get("release", {})
        installer = config_copy.get("installer", {})

        config_copy.update(compilation)
        config_copy.update(upload)
        config_copy.update(advanced)
        config_copy.update(release)
        config_copy.update(installer)

        # Remove nested keys
        config_copy.pop("compilation", None)
        config_copy.pop("upload", None)
        config_copy.pop("advanced", None)
        config_copy.pop("release", None)
        config_copy.pop("installer", None)

        # Select the per-compiler section matching the resolved compiler.
        # optimize/strip are promoted to top-level fields; the remaining keys
        # become the free-form compiler_options passed to the adapter.
        section_key = COMPILER_SECTION_KEYS.get(config_copy.get("compiler", ""))
        selected_section = dict(per_compiler_sections.get(section_key, {}))
        if "optimize" in selected_section:
            config_copy["optimize"] = selected_section.pop("optimize")
        if "strip" in selected_section:
            config_copy["strip"] = selected_section.pop("strip")
        config_copy["compiler_options"] = selected_section

        # 'auto' supprimé : plus de compilateur par défaut implicite.
        if config_copy.get("compiler") == "auto":
            raise ConfigurationError(
                "compiler='auto' a été supprimé. Indiquer explicitement "
                "'Cx_Freeze', 'PyInstaller' ou 'Nuitka', ou laisser le champ "
                "vide pour choisir interactivement au moment de la compilation."
            )

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
