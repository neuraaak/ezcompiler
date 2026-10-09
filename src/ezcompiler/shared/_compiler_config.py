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

import re

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Local imports
from ._constants import TUF_PUBLIC_DIRS
from ._installer_config import InstallerConfig, raise_on_legacy_installer_keys
from .exceptions import ConfigurationError

if TYPE_CHECKING:
    from .._types import ReleaseDestination, RepoDestination

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

# Keys accepted by each nested config section. The flattening of from_dict()
# validates against this schema: without it, any field is accepted in any
# section and a key present in two sections is resolved by the merge order.
# 'installer' is not listed here — it stays a sub-object (InstallerConfig).
SECTION_SCHEMA: dict[str, frozenset[str]] = {
    "compilation": frozenset({"console", "compiler"}),
    "upload": frozenset(
        {
            "repo_destination",
            "release_destination",
            "repo_endpoint",
            "release_endpoint",
            "repo_public_url",
        }
    ),
    "advanced": frozenset({"debug"}),
    "release": frozenset(
        {"tuf_enabled", "tuf_repo_dir", "tuf_keys_dir", "tuf_expiration_days"}
    ),
}

# Keys removed by past migrations, with the message that names the
# replacement. Checked both inside a section (during the strict flattening)
# and at the top level, so the diagnostic is the same wherever the key sits.
REMOVED_KEYS: dict[str, str] = {
    "repo_path": "'repo_path' was removed. Use 'upload.repo_endpoint'.",
    "server_url": "'server_url' was removed. Use 'upload.repo_endpoint' or 'upload.release_endpoint'.",
    "update_repo_url": "'update_repo_url' was removed. Use 'upload.repo_endpoint'.",
    "r2_bucket": "'r2_bucket' was removed. Use 'upload.repo_endpoint' in \"bucket/prefix\" form.",
    "r2_remote_prefix": "'r2_remote_prefix' was removed. See 'upload.repo_endpoint' (\"bucket/prefix\" form).",
    "release_needed": "'release_needed' was renamed to 'tuf_enabled'.",
    "release_type": "'release_type' was removed. tufup is the only release backend.",
    "repo_needed": "'repo_needed' was removed. Use 'release.tuf_enabled'.",
    "structure": "'upload.structure' / 'upload_structure' was removed. "
    "Use 'upload.repo_destination' and 'upload.release_destination'.",
    "upload_structure": "'upload.structure' / 'upload_structure' was removed. "
    "Use 'upload.repo_destination' and 'upload.release_destination'.",
    "zip_needed": "'zip_needed' was removed. The zip is always produced when "
    "tuf_enabled=True. In the release-less flow, the zip depends on the "
    "compilation result.",
}

_OWNER_REPO_RE = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")

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
        release_destination: Release asset destination - disk, server, r2,
            github, or gitlab
        repo_endpoint: Endpoint for TUF repo upload (path, URL, or "bucket/prefix")
        release_endpoint: Release endpoint (path, URL, bucket/prefix, or owner/repo)
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
    # Per-role metadata lifetimes (days). Maps TUF role names
    # (root/targets/snapshot/timestamp) to expiration days. None → tufup
    # defaults (root=365, targets=7, snapshot=7, timestamp=1). Raise these for
    # projects updated irregularly so metadata does not expire between releases.
    tuf_expiration_days: dict[str, int] | None = None

    # ////////////////////////////////////////////////
    # INSTALLER OPTIONS (Inno Setup)
    # ////////////////////////////////////////////////

    installer: InstallerConfig = field(default_factory=InstallerConfig)

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
        self._validate_installer_icon()

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

        self._validate_tuf_keys_location()

    def _validate_tuf_keys_location(self) -> None:
        """
        Refuse a private keystore placed inside the published part of the tree.

        Only ``metadata/`` and ``targets/`` of the TUF repository are uploaded,
        so a ``tuf_keys_dir`` sitting under one of them would publish the
        private signing keys.

        Raises:
            ConfigurationError: If ``tuf_keys_dir`` resolves inside
                ``<tuf_repo_dir>/metadata`` or ``<tuf_repo_dir>/targets``.
        """
        if self.tuf_keys_dir is None:
            return

        repo_dir = self.tuf_repo_dir or (Path(self.output_folder) / "repo")
        keys = Path(self.tuf_keys_dir).expanduser().resolve()
        for public in TUF_PUBLIC_DIRS:
            forbidden = (Path(repo_dir).expanduser() / public).resolve()
            if keys == forbidden or forbidden in keys.parents:
                raise ConfigurationError(
                    f"tuf_keys_dir invalide : {self.tuf_keys_dir} se trouve sous "
                    f"{forbidden}, which is published with the TUF tree — the "
                    "private signing keys would leave the machine. Move the "
                    "keystore outside metadata/ and targets/ (default "
                    "<tuf_repo_dir>/keystore)."
                )

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
        Validate upload and publication destinations and their endpoints.

        The TUF repository may be uploaded to disk, server or r2. Release assets
        may also be published to github or gitlab. Server and r2 destinations
        require an endpoint; publication destinations may infer the repository.

        Raises:
            ConfigurationError: If a destination is not supported or endpoint is missing
        """
        valid_repo = ["disk", "server", "r2"]
        if self.repo_destination not in valid_repo:
            raise ConfigurationError(
                f"Invalid repo_destination: {self.repo_destination}. "
                f"Must be one of {valid_repo}"
            )

        valid_release = ["disk", "server", "r2", "github", "gitlab"]
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

        if self.release_destination in ("github", "gitlab"):
            if self.release_endpoint and not _OWNER_REPO_RE.fullmatch(
                self.release_endpoint
            ):
                raise ConfigurationError(
                    f"Invalid release_endpoint for "
                    f"release_destination='{self.release_destination}': "
                    f"'{self.release_endpoint}'. Expected the "
                    f'"owner/repo" form (no URL, no protocol), or empty to '
                    f"let the CLI infer the repository from the git remote."
                )
        elif self.release_destination != "disk" and not self.release_endpoint:
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

    def _validate_installer_icon(self) -> None:
        """
        Validate the icon format when the installer stage is enabled.

        Inno Setup requires a .ico file; other formats fail ISCC with an
        opaque exit 2. Compilers accept other icon formats, so this check
        only applies once the installer stage is enabled.

        Raises:
            ConfigurationError: If installer.enabled and icon is not a .ico file
        """
        if (
            self.installer.enabled
            and self.icon
            and Path(self.icon).suffix.lower() != ".ico"
        ):
            raise ConfigurationError(
                f"icon must be a .ico file when the installer is enabled: {self.icon}"
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
        """Resolved destination for the TUF tree."""
        return self.repo_endpoint or None

    @property
    def resolved_release_destination(self) -> str | None:
        """Resolved destination for the installer zip."""
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
                "tuf_expiration_days": self.tuf_expiration_days,
            },
            "installer": self.installer.to_dict(),
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
    def _flatten_sections(cls, config: dict[str, Any]) -> None:
        """
        Flatten the nested config sections in place, strictly.

        Two silent behaviours are removed here: a key accepted in a section it
        does not belong to, and a key defined in two sections where the order
        of the merges decided the winner (``[advanced] debug=false`` used to
        beat ``[compilation] debug=true`` without a word).

        Args:
            config: Mutable config mapping; sections are popped and their keys
                promoted to the top level.

        Raises:
            ConfigurationError: If a key sits in the wrong section, or is
                defined both at the top level and in a section, or in two
                sections at once.
        """
        owner: dict[str, str] = {
            key: "racine" for key in config if key not in SECTION_SCHEMA
        }
        for section, allowed in SECTION_SCHEMA.items():
            values = config.pop(section, {})
            if not values:
                continue
            if not isinstance(values, dict):
                raise ConfigurationError(
                    f"Section '{section}' must be a table, not a "
                    f"{type(values).__name__}."
                )
            for key, value in values.items():
                expected = next(
                    (s for s, keys in SECTION_SCHEMA.items() if key in keys), None
                )
                if key in REMOVED_KEYS:
                    raise ConfigurationError(REMOVED_KEYS[key])
                if key not in allowed:
                    hint = (
                        f" That key belongs to section '{expected}'."
                        if expected
                        else ""
                    )
                    raise ConfigurationError(
                        f"Invalid key '{key}' in section '{section}'.{hint}"
                    )
                if key in owner:
                    raise ConfigurationError(
                        f"Key '{key}' defined twice: in '{owner[key]}' and "
                        f"in '{section}'. Declare it only once — the merge "
                        "order must not decide which value wins."
                    )
                owner[key] = section
                config[key] = value

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
                "'compiler_options' was removed. Use a per-compiler "
                "section: [tool.ezcompiler.pyinstaller], "
                "[tool.ezcompiler.cx_freeze] ou [tool.ezcompiler.nuitka]."
            )

        # 'optimize'/'strip' left 'advanced' for the per-compiler sections.
        advanced = config_copy.get("advanced", {})
        if "optimize" in advanced or "strip" in advanced:
            raise ConfigurationError(
                "'advanced.optimize' / 'advanced.strip' moved to the compiler "
                "section ([tool.ezcompiler.<pyinstaller|cx_freeze|nuitka>])."
            )

        # Legacy flat installer keys (pre-4.0.0) — same pattern as the
        # compiler_options / advanced.optimize removals.
        raise_on_legacy_installer_keys(config_copy)

        # Flatten the nested sections. Each key is checked against the schema
        # of its own section, and a key defined twice is an error instead of
        # being resolved silently by the order of the merges.
        cls._flatten_sections(config_copy)

        installer_section = config_copy.pop("installer", {})
        if isinstance(installer_section, InstallerConfig):
            config_copy["installer"] = installer_section
        else:
            config_copy["installer"] = InstallerConfig.from_dict(installer_section)

        # Select the per-compiler section matching the resolved compiler.
        # optimize/strip are promoted to top-level fields; the remaining keys
        # become the free-form compiler_options passed to the adapter.
        section_key = COMPILER_SECTION_KEYS.get(config_copy.get("compiler", ""))
        selected_section = (
            dict(per_compiler_sections.get(section_key, {})) if section_key else {}
        )
        if "optimize" in selected_section:
            config_copy["optimize"] = selected_section.pop("optimize")
        if "strip" in selected_section:
            config_copy["strip"] = selected_section.pop("strip")
        config_copy["compiler_options"] = selected_section

        # 'auto' was removed: no implicit default compiler any more.
        if config_copy.get("compiler") == "auto":
            raise ConfigurationError(
                "compiler='auto' was removed. State explicitly "
                "'Cx_Freeze', 'PyInstaller' or 'Nuitka', or leave the field "
                "empty to choose interactively at compile time."
            )

        # Migration errors for removed upload/release fields.
        for key, msg in REMOVED_KEYS.items():
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
