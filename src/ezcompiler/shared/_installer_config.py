# ///////////////////////////////////////////////////////////////
# INSTALLER_CONFIG - Inno Setup installer configuration
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Installer config - Configuration for the Inno Setup installer stage.

Holds the curated option set driving .iss generation, plus two raw escape
hatches (``extra_setup_directives`` / ``extra_sections``) covering every
Inno directive not worth a typed field. Validates shape only: it knows
nothing about .iss syntax or ISCC.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import dataclasses as _dc
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .exceptions import ConfigurationError

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Languages shipped as .isl files with Inno Setup 6.
INNO_LANGUAGES = frozenset(
    {
        "armenian",
        "brazilianportuguese",
        "bulgarian",
        "catalan",
        "corsican",
        "czech",
        "danish",
        "dutch",
        "english",
        "finnish",
        "french",
        "german",
        "hebrew",
        "hungarian",
        "icelandic",
        "italian",
        "japanese",
        "norwegian",
        "polish",
        "portuguese",
        "russian",
        "slovak",
        "slovenian",
        "spanish",
        "turkish",
        "ukrainian",
    }
)

# [Setup] directives driven by typed fields — an extra colliding with one of
# these would produce two contradictory lines whose winner depends on order.
MANAGED_SETUP_DIRECTIVES = frozenset(
    {
        "appid",
        "appname",
        "appversion",
        "apppublisher",
        "apppublisherurl",
        "appsupporturl",
        "appupdatesurl",
        "architecturesallowed",
        "architecturesinstallin64bitmode",
        "closeapplications",
        "compression",
        "defaultdirname",
        "defaultgroupname",
        "licensefile",
        "outputdir",
        "outputbasefilename",
        "privilegesrequired",
        "restartapplications",
        "setupiconfile",
        "solidcompression",
        "versioninfoversion",
        "wizardstyle",
    }
)

# Sections generated from typed fields.
MANAGED_SECTIONS = frozenset(
    {
        "setup",
        "files",
        "icons",
        "run",
        "tasks",
        "languages",
        "registry",
        "uninstalldelete",
    }
)

_GUID_RE = re.compile(
    r"^\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}"
    r"-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}$"
)

_ARCHITECTURES = ("x64", "x86", "arm64", "auto")
_WIZARD_STYLES = ("modern", "classic")

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


@dataclass
class InstallerConfig:
    """Configuration of the Inno Setup installer stage."""

    # ////////////////////////////////////////////////
    # FRAME
    # ////////////////////////////////////////////////

    enabled: bool = False
    iss_path: Path | None = None
    output_dir: Path | None = None
    iscc_path: Path | None = None

    # ////////////////////////////////////////////////
    # IDENTITY
    # ////////////////////////////////////////////////

    # None -> deterministic UUIDv5 derived from company_name + project_name.
    app_id: str | None = None
    publisher_url: str = ""
    support_url: str = ""
    updates_url: str = ""
    architecture: Literal["x64", "x86", "arm64", "auto"] = "x64"

    # ////////////////////////////////////////////////
    # LOCATION AND PRIVILEGES
    # ////////////////////////////////////////////////

    per_user: bool = False

    # ////////////////////////////////////////////////
    # SHORTCUTS AND POST-INSTALL
    # ////////////////////////////////////////////////

    desktop_icon: bool = True
    start_menu_group: str | None = None
    launch_after_install: bool = True
    add_to_path: bool = False

    # ////////////////////////////////////////////////
    # UPGRADE AND UNINSTALL
    # ////////////////////////////////////////////////

    close_running_app: bool = True
    uninstall_delete: list[str] = field(default_factory=list)

    # ////////////////////////////////////////////////
    # WIZARD UX
    # ////////////////////////////////////////////////

    license_file: Path | None = None
    languages: list[str] = field(default_factory=lambda: ["english"])
    wizard_style: Literal["modern", "classic"] = "modern"

    # ////////////////////////////////////////////////
    # OUTPUT AND SIGNING
    # ////////////////////////////////////////////////

    # Free-form: the algorithm list belongs to Inno, duplicating it here would
    # diverge at every Inno release. ISCC rejects an invalid value itself.
    compression: str = "lzma2/max"
    sign_tool_name: str | None = None
    sign_tool_command: str | None = None

    # ////////////////////////////////////////////////
    # ESCAPE HATCHES
    # ////////////////////////////////////////////////

    extra_setup_directives: dict[str, str] = field(default_factory=dict)
    extra_sections: dict[str, list[str]] = field(default_factory=dict)

    # ////////////////////////////////////////////////
    # INITIALIZATION AND VALIDATION
    # ////////////////////////////////////////////////

    def __post_init__(self) -> None:
        """
        Coerce path-like fields and validate configuration.

        Shape checks (bounds, GUID format, collisions) run unconditionally,
        even when ``enabled`` is False, so a disabled but malformed config is
        still caught early. Costly checks (file existence) run only when
        ``enabled`` is True.

        Raises:
            ConfigurationError: If any validation fails.
        """
        self._coerce_paths()
        self._validate_architecture()
        self._validate_wizard_style()
        self._validate_languages()
        self._validate_app_id()
        self._validate_sign_tool()
        self._validate_uninstall_delete()
        self._validate_extra_setup_directives()
        self._validate_extra_sections()
        if self.enabled:
            self._validate_paths_exist()

    def _coerce_paths(self) -> None:
        """Coerce str path fields to Path, before existence checks run."""
        if isinstance(self.iss_path, str):
            self.iss_path = Path(self.iss_path)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.iscc_path, str):
            self.iscc_path = Path(self.iscc_path)
        if isinstance(self.license_file, str):
            self.license_file = Path(self.license_file)

    def _validate_paths_exist(self) -> None:
        """
        Validate that provided paths point to existing files.

        Raises:
            ConfigurationError: If iss_path or license_file is set but absent.
        """
        if self.iss_path is not None and not self.iss_path.is_file():
            raise ConfigurationError(f"iss_path not found: {self.iss_path}")
        if self.license_file is not None and not self.license_file.is_file():
            raise ConfigurationError(f"license_file not found: {self.license_file}")

    def _validate_architecture(self) -> None:
        """Raises ConfigurationError if architecture is not a supported value."""
        if self.architecture not in _ARCHITECTURES:
            raise ConfigurationError(
                f"Invalid architecture: {self.architecture!r}. "
                f"Must be one of {_ARCHITECTURES}"
            )

    def _validate_wizard_style(self) -> None:
        """Raises ConfigurationError if wizard_style is not a supported value."""
        if self.wizard_style not in _WIZARD_STYLES:
            raise ConfigurationError(
                f"Invalid wizard_style: {self.wizard_style!r}. "
                f"Must be one of {_WIZARD_STYLES}"
            )

    def _validate_languages(self) -> None:
        """
        Validate languages: non-empty, known, without duplicates.

        Raises:
            ConfigurationError: If languages is empty, contains an unknown
                Inno language, or a duplicate entry.
        """
        if not self.languages:
            raise ConfigurationError("languages cannot be empty")

        unknown = [lang for lang in self.languages if lang not in INNO_LANGUAGES]
        if unknown:
            raise ConfigurationError(
                f"Unknown languages: {unknown}. Must be one of {sorted(INNO_LANGUAGES)}"
            )

        if len(self.languages) != len(set(self.languages)):
            raise ConfigurationError(f"Duplicate languages in {self.languages}")

    def _validate_app_id(self) -> None:
        """Raises ConfigurationError if app_id is set but not a valid GUID."""
        if self.app_id is not None and not _GUID_RE.match(self.app_id):
            raise ConfigurationError(
                f"app_id must be a GUID of the form "
                f"'{{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}}', got: {self.app_id!r}"
            )

    def _validate_sign_tool(self) -> None:
        """
        Validate that sign_tool_name and sign_tool_command are set together.

        Raises:
            ConfigurationError: If only one of the pair is provided.
        """
        if self.sign_tool_name is not None and self.sign_tool_command is None:
            raise ConfigurationError(
                "sign_tool_command is required when sign_tool_name is set"
            )
        if self.sign_tool_command is not None and self.sign_tool_name is None:
            raise ConfigurationError(
                "sign_tool_name is required when sign_tool_command is set"
            )

    def _validate_uninstall_delete(self) -> None:
        """
        Validate uninstall_delete entries stay within the app directory.

        Rejects an absolute entry (POSIX-style leading slash or a drive
        letter, e.g. ``C:\\Windows``) and any entry containing a ``..``
        segment, including after an Inno constant like ``{app}``.

        Raises:
            ConfigurationError: If an entry escapes the app directory.
        """
        for entry in self.uninstall_delete:
            if entry.startswith(("/", "\\")) or (len(entry) > 1 and entry[1] == ":"):
                raise ConfigurationError(
                    f"uninstall_delete entry must be relative to the app "
                    f"directory, got absolute path: {entry!r}"
                )
            segments = re.split(r"[\\/]", entry)
            if ".." in segments:
                raise ConfigurationError(
                    f"uninstall_delete entry must not escape the app "
                    f"directory with '..': {entry!r}"
                )

    def _validate_extra_setup_directives(self) -> None:
        """
        Validate extra_setup_directives does not shadow a managed directive.

        Raises:
            ConfigurationError: If a key collides with a managed directive,
                case-insensitively.
        """
        for key in self.extra_setup_directives:
            if key.lower() in MANAGED_SETUP_DIRECTIVES:
                raise ConfigurationError(
                    f"extra_setup_directives key {key!r} collides with a "
                    f"managed directive ({key!r} is set via a typed field)"
                )

    def _validate_extra_sections(self) -> None:
        """
        Validate extra_sections does not shadow a managed section.

        Inno Setup section names are case-insensitive, so the comparison
        happens in lowercase.

        Raises:
            ConfigurationError: If a key collides with a managed section,
                case-insensitively.
        """
        for key in self.extra_sections:
            if key.lower() in MANAGED_SECTIONS:
                raise ConfigurationError(
                    f"extra_sections key {key!r} collides with a managed "
                    f"section (section names are case-insensitive in Inno Setup)"
                )

    # ////////////////////////////////////////////////
    # SERIALIZATION METHODS
    # ////////////////////////////////////////////////

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to a flat dictionary.

        Every field is emitted, including defaults, so a round-trip through
        ``from_dict`` reconstructs an equal instance. Path fields are
        serialized to str (or None).

        Returns:
            dict[str, Any]: Configuration as a flat dictionary.
        """
        return {
            "enabled": self.enabled,
            "iss_path": str(self.iss_path) if self.iss_path is not None else None,
            "output_dir": (
                str(self.output_dir) if self.output_dir is not None else None
            ),
            "iscc_path": (str(self.iscc_path) if self.iscc_path is not None else None),
            "app_id": self.app_id,
            "publisher_url": self.publisher_url,
            "support_url": self.support_url,
            "updates_url": self.updates_url,
            "architecture": self.architecture,
            "per_user": self.per_user,
            "desktop_icon": self.desktop_icon,
            "start_menu_group": self.start_menu_group,
            "launch_after_install": self.launch_after_install,
            "add_to_path": self.add_to_path,
            "close_running_app": self.close_running_app,
            "uninstall_delete": self.uninstall_delete,
            "license_file": (
                str(self.license_file) if self.license_file is not None else None
            ),
            "languages": self.languages,
            "wizard_style": self.wizard_style,
            "compression": self.compression,
            "sign_tool_name": self.sign_tool_name,
            "sign_tool_command": self.sign_tool_command,
            "extra_setup_directives": self.extra_setup_directives,
            "extra_sections": self.extra_sections,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstallerConfig:
        """
        Create an InstallerConfig from a dictionary.

        None values are filtered out (a TOML-generated dict carries explicit
        nulls for unset fields; they must not override dataclass defaults).
        An unknown key is rejected, naming it.

        Args:
            data: Configuration dictionary, e.g. as loaded from TOML.

        Returns:
            InstallerConfig: New configuration instance.

        Raises:
            ConfigurationError: If data contains an unknown key.
        """
        valid_fields = {f.name for f in _dc.fields(cls)}
        unknown = set(data) - valid_fields
        if unknown:
            raise ConfigurationError(
                f"Unknown installer configuration key(s): {sorted(unknown)}"
            )

        kwargs = {key: value for key, value in data.items() if value is not None}
        return cls(**kwargs)
