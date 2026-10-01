# ///////////////////////////////////////////////////////////////
# CLI_INTERFACE - Command-line interface for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
CLI interface - Command-line interface for EzCompiler.

This module provides a Click-based CLI for generating configuration files,
build.py scripts, version files, and initializing new EzCompiler projects.

Interfaces layer can use all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import logging

    from ezplog.handlers.wizard.dynamic import StageConfig
    from ezplog.lib_mode import _LazyPrinter

    from .._types import ReleaseDestination, RepoDestination
    from ..shared import CompilerConfig

# Third-party imports
import click
import tomli_w
import yaml
from ezplog.lib_mode import get_logger, get_printer

# Local imports
from .._version import __version__
from ..services import (
    ConfigService,
    InstallerService,
    PipelineService,
    PublishService,
    ReleaseService,
    TemplateService,
    TufService,
    UpdaterService,
)
from ..shared import COMPILER_SECTION_KEYS
from ..shared.exceptions import (
    CompilationError,
    ConfigError,
    ConfigurationError,
    InstallerError,
    PublishError,
    ReleaseError,
    SigningKeyError,
    TemplateError,
    UploadError,
    VersionError,
    ZipError,
)
from ..utils import is_prerelease

# ///////////////////////////////////////////////////////////////
# MODULE-LEVEL LOGGING (lib_mode — passive proxies)
# ///////////////////////////////////////////////////////////////

# Module-level printer and logger obtained once at import time.
# Both are passive proxies: silent until the host application initializes Ezpl.
_printer: _LazyPrinter = get_printer()
_logger: logging.Logger = get_logger(__name__)


def _get_printer() -> _LazyPrinter:
    """Return the module-level lazy printer proxy."""
    return _printer


def _get_logger() -> logging.Logger:
    """Return the module-level stdlib logger."""
    return _logger


_template_service: TemplateService | None = None


def _get_template_service() -> TemplateService:
    """Get the shared TemplateService instance (created once, reused across commands)."""
    global _template_service  # noqa: PLW0603
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service


# ///////////////////////////////////////////////////////////////
# CLI COMMANDS AND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="EzCompiler")
def main() -> None:
    """
    EzCompiler - CLI for Python project compilation and distribution.

    Generates configuration files, build.py, and version files from templates
    with support for multiple formats (YAML, JSON) and template types.
    """
    from ezplog import Ezpl

    Ezpl()


@main.group()
def generate() -> None:
    """Generate files from templates."""


@generate.command()
@click.option(
    "--from-pyproject",
    "-fp",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Extract base values from a pyproject.toml file",
)
@click.option(
    "--interactive",
    "-I",
    is_flag=True,
    default=False,
    help="Prompt interactively for missing values",
)
@click.option(
    "--format",
    "-fmt",
    type=click.Choice(["yaml", "json", "pyproject"]),
    default="yaml",
    help="Output format (default: yaml)",
)
@click.option("--version", "-v", default=None, help="Project version")
@click.option("--project-name", "-n", default=None, help="Project name")
@click.option("--project-description", "-d", default=None, help="Project description")
@click.option("--company-name", "-c", default=None, help="Company name")
@click.option("--author", "-a", default=None, help="Project author")
@click.option("--main-file", "-m", default=None, help="Main file")
@click.option("--icon", "-i", default=None, help="Path to icon file")
@click.option(
    "--version-file",
    "-vf",
    "version_filename",
    default=None,
    help="Version file name",
)
@click.option(
    "--output-folder",
    "-o",
    default=None,
    help="Output folder for compilation",
)
@click.option(
    "--include-files",
    "-f",
    multiple=True,
    help="Files to include (can be specified multiple times)",
)
@click.option(
    "--include-folders",
    "-fd",
    multiple=True,
    help="Folders to include (can be specified multiple times)",
)
@click.option(
    "--packages",
    "-p",
    multiple=True,
    help="Packages to include (can be specified multiple times)",
)
@click.option(
    "--includes",
    "-inc",
    multiple=True,
    help="Modules to include (can be specified multiple times)",
)
@click.option(
    "--excludes",
    "-exc",
    multiple=True,
    help="Modules to exclude (can be specified multiple times)",
)
@click.option(
    "--console",
    "-con",
    is_flag=True,
    default=True,
    help="Show console window (default: True)",
)
@click.option(
    "--compiler",
    "-comp",
    type=click.Choice(["Cx_Freeze", "PyInstaller", "Nuitka"]),
    default=None,
    help="Compiler to use",
)
@click.option(
    "--tuf-enabled",
    "-te",
    is_flag=True,
    default=False,
    help="Enable TUF secure release (default: False)",
)
@click.option(
    "--installer-enabled",
    "-ie",
    is_flag=True,
    default=False,
    help="Enable Inno Setup installer build stage (default: False)",
)
@click.option(
    "--repo-destination",
    "-rd",
    type=click.Choice(["disk", "server", "r2"]),
    default=None,
    help="TUF repo upload backend",
)
@click.option(
    "--release-destination",
    "-rld",
    type=click.Choice(["disk", "server", "r2"]),
    default=None,
    help="Zip installer upload backend",
)
@click.option(
    "--repo-endpoint",
    "-re",
    default=None,
    help="Upload endpoint for TUF repo (path, URL, or bucket/prefix)",
)
@click.option(
    "--release-endpoint",
    "-rle",
    default=None,
    help="Upload endpoint for release zip (path or URL)",
)
@click.option(
    "--repo-public-url",
    "-rpu",
    default=None,
    help="Public base URL for the TUF repo (required for r2/tuf)",
)
@click.option(
    "--optimize",
    "-opt",
    is_flag=True,
    default=True,
    help="Optimize compilation (default: True)",
)
@click.option(
    "--strip",
    "-s",
    is_flag=True,
    default=False,
    help="Strip symbols (default: False)",
)
@click.option(
    "--debug",
    "-dbg",
    is_flag=True,
    default=False,
    help="Debug mode (default: False)",
)
@click.option(
    "--output",
    "-out",
    type=click.Path(),
    default=".",
    help="Output directory for generated files (default: .)",
)
def config(
    from_pyproject: Path | None,
    interactive: bool,
    format: str,
    version: str | None,
    project_name: str | None,
    project_description: str | None,
    company_name: str | None,
    author: str | None,
    main_file: str | None,
    icon: str | None,
    version_filename: str | None,
    output_folder: str | None,
    include_files: tuple[str, ...],
    include_folders: tuple[str, ...],
    packages: tuple[str, ...],
    includes: tuple[str, ...],
    excludes: tuple[str, ...],
    console: bool,
    compiler: str | None,
    tuf_enabled: bool,
    installer_enabled: bool,
    repo_destination: RepoDestination | None,
    release_destination: ReleaseDestination | None,
    repo_endpoint: str | None,
    release_endpoint: str | None,
    repo_public_url: str | None,
    optimize: bool,
    strip: bool,
    debug: bool,
    output: str,
) -> None:
    """
    Generate a configuration file.

    Builds configuration from pyproject.toml, CLI options, and/or interactive
    prompts.  Sources are merged with the following priority (highest first):
    CLI options > pyproject.toml > interactive prompts > defaults.

    \b
    Examples:
        ezcompiler generate config -n myproject
        ezcompiler generate config --from-pyproject pyproject.toml --fmt json
        ezcompiler generate config --from-pyproject pyproject.toml -I
    """

    printer = _get_printer()
    logger = _get_logger()

    try:
        # 1. Load base from pyproject.toml if requested
        config_dict: dict[str, Any] = {}
        if from_pyproject:
            config_dict = ConfigService.load_pyproject_as_dict(from_pyproject)
            printer.info(f"Loaded base configuration from {from_pyproject}")
            logger.info(f"Loaded base configuration from {from_pyproject}")

        # 2. Override with explicitly provided CLI options
        cli_overrides: dict[str, Any] = {}
        if version is not None:
            cli_overrides["version"] = version
        if project_name is not None:
            cli_overrides["project_name"] = project_name
        if project_description is not None:
            cli_overrides["project_description"] = project_description
        if company_name is not None:
            cli_overrides["company_name"] = company_name
        if author is not None:
            cli_overrides["author"] = author
        if main_file is not None:
            cli_overrides["main_file"] = main_file
        if icon is not None:
            cli_overrides["icon"] = icon
        if version_filename is not None:
            cli_overrides["version_filename"] = version_filename
        if output_folder is not None:
            cli_overrides["output_folder"] = output_folder
        if include_files:
            cli_overrides.setdefault("include_files", {})["files"] = list(include_files)
        if include_folders:
            cli_overrides.setdefault("include_files", {})["folders"] = list(
                include_folders
            )
        if packages:
            cli_overrides["packages"] = list(packages)
        if includes:
            cli_overrides["includes"] = list(includes)
        if excludes:
            cli_overrides["excludes"] = list(excludes)
        if compiler is not None:
            cli_overrides.setdefault("compilation", {})["compiler"] = compiler
        if repo_destination is not None:
            cli_overrides.setdefault("upload", {})["repo_destination"] = (
                repo_destination
            )
        if release_destination is not None:
            cli_overrides.setdefault("upload", {})["release_destination"] = (
                release_destination
            )
        if repo_endpoint is not None:
            cli_overrides.setdefault("upload", {})["repo_endpoint"] = repo_endpoint
        if release_endpoint is not None:
            cli_overrides.setdefault("upload", {})["release_endpoint"] = (
                release_endpoint
            )
        if repo_public_url is not None:
            cli_overrides.setdefault("upload", {})["repo_public_url"] = repo_public_url

        # Flags always have a value — include them
        cli_overrides.setdefault("compilation", {}).update({"console": console})
        if tuf_enabled:
            cli_overrides.setdefault("release", {})["tuf_enabled"] = True
        if installer_enabled:
            cli_overrides.setdefault("installer", {})["enabled"] = True
        # optimize/strip are compiler-specific: the template emits them under
        # the compiler section. debug stays generic (advanced).
        cli_overrides["optimize"] = optimize
        cli_overrides["strip"] = strip
        cli_overrides.setdefault("advanced", {})["debug"] = debug

        if cli_overrides:
            config_dict = ConfigService.merge_configs(config_dict, cli_overrides)

        # 3. Interactive prompts for missing required values
        if interactive:
            if not config_dict.get("project_name"):
                config_dict["project_name"] = click.prompt("Project name")
            if not config_dict.get("version"):
                config_dict["version"] = click.prompt("Version", default="1.0.0")
            if not config_dict.get("project_description"):
                config_dict["project_description"] = click.prompt(
                    "Project description", default=""
                )
            if not config_dict.get("company_name"):
                config_dict["company_name"] = click.prompt("Company name", default="")
            if not config_dict.get("author"):
                config_dict["author"] = click.prompt("Author", default="")
            if not config_dict.get("main_file"):
                config_dict["main_file"] = click.prompt("Main file", default="main.py")

        # 4. Apply defaults for anything still missing
        config_dict.setdefault("version", "1.0.0")
        config_dict.setdefault("project_description", "")
        config_dict.setdefault("company_name", "")
        config_dict.setdefault("author", "")
        config_dict.setdefault("main_file", "main.py")
        config_dict.setdefault("icon", "")
        config_dict.setdefault("version_filename", "version_info.txt")
        config_dict.setdefault("output_folder", "dist")
        config_dict.setdefault("include_files", {"files": [], "folders": []})
        config_dict.setdefault("packages", [])
        config_dict.setdefault("includes", [])
        config_dict.setdefault("excludes", ["debugpy", "test", "unittest"])
        config_dict.setdefault(
            "compilation",
            {
                "console": True,
                "compiler": "PyInstaller",
            },
        )
        config_dict.setdefault(
            "upload",
            {
                "repo_destination": "disk",
                "release_destination": "disk",
                "repo_endpoint": "",
                "release_endpoint": "",
                "repo_public_url": "",
            },
        )
        config_dict.setdefault("optimize", True)
        config_dict.setdefault("strip", False)
        config_dict.setdefault("advanced", {"debug": False})
        config_dict.setdefault("installer", {}).setdefault("enabled", False)

        # Validate: project_name is required
        if not config_dict.get("project_name"):
            raise click.UsageError(
                "Project name is required. Provide it via --project-name, "
                "--from-pyproject, or --interactive"
            )

        # Ensure output directory exists
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate configuration file in chosen format
        template_service = _get_template_service()
        if format == "pyproject":
            generated = dict(config_dict)
            generated.pop("installer")
            compiler_name = generated["compilation"].get("compiler") or "PyInstaller"
            generated["compilation"]["compiler"] = compiler_name
            compiler_key = COMPILER_SECTION_KEYS[compiler_name]
            compiler_options = dict(generated.get(compiler_key, {}))
            for option in ("optimize", "strip"):
                compiler_options.setdefault(option, generated.pop(option))
            generated[compiler_key] = compiler_options
            target = output_path / "pyproject.toml"
            _create_or_update_pyproject(target, generated)
            installer_block = tomli_w.dumps(
                {"tool": {"ezcompiler": {"installer": config_dict["installer"]}}}
            )
            content = target.read_text(encoding="utf-8") + "\n" + installer_block
            content += (
                "# per_user = true                    # installs into %LOCALAPPDATA% "
                "(required for tufup auto-update)\n"
                '# iss_path = "installer/MyApp.iss"   # script produced by '
                "`ezcompiler generate iss`\n"
                "# Full option set: `ezcompiler generate iss --help` and "
                "docs/guides/windows-installer.md\n"
            )
        else:
            content = template_service.process_config_template(format, config_dict)
            filename = "ezcompiler.yaml" if format == "yaml" else "ezcompiler.json"
            target = output_path / filename
            if format == "json":
                # Extend the existing template without changing its other fields.
                content = content.rstrip().removesuffix("}").rstrip()
                content += ',\n  "installer": ' + json.dumps(config_dict["installer"])
                content += "\n}\n"
            else:
                content += "\n" + yaml.safe_dump(
                    {"installer": config_dict["installer"]}
                )
        target.write_text(content, encoding="utf-8")
        printer.success(f"Configuration file generated: {target}")
        logger.info(f"Configuration file generated: {target}")

    except (TemplateError, ConfigError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@generate.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Configuration file (YAML or JSON)",
)
@click.option(
    "--from-pyproject",
    "-fp",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Extract base values from a pyproject.toml file",
)
@click.option(
    "--interactive",
    "-I",
    is_flag=True,
    default=False,
    help="Prompt interactively for missing values",
)
@click.option("--version", "-v", default=None, help="Project version")
@click.option("--project-name", "-n", default=None, help="Project name")
@click.option("--project-description", "-d", default=None, help="Project description")
@click.option("--company-name", "-cn", default=None, help="Company name")
@click.option("--author", "-a", default=None, help="Project author")
@click.option("--main-file", "-m", default=None, help="Main file")
@click.option("--icon", "-i", default=None, help="Path to icon file")
@click.option(
    "--version-file",
    "-vf",
    "version_filename",
    default=None,
    help="Version file name",
)
@click.option(
    "--output-folder",
    "-o",
    default=None,
    help="Output folder for compilation",
)
@click.option(
    "--include-files",
    "-f",
    multiple=True,
    help="Files to include (can be specified multiple times)",
)
@click.option(
    "--include-folders",
    "-fd",
    multiple=True,
    help="Folders to include (can be specified multiple times)",
)
@click.option(
    "--packages",
    "-p",
    multiple=True,
    help="Packages to include (can be specified multiple times)",
)
@click.option(
    "--includes",
    "-inc",
    multiple=True,
    help="Modules to include (can be specified multiple times)",
)
@click.option(
    "--excludes",
    "-exc",
    multiple=True,
    help="Modules to exclude (can be specified multiple times)",
)
@click.option(
    "--output",
    "-out",
    type=click.Path(),
    default=".",
    help="Output directory for generated files (default: .)",
)
def build(
    config: str | None,
    from_pyproject: Path | None,
    interactive: bool,
    version: str | None,
    project_name: str | None,
    project_description: str | None,
    company_name: str | None,
    author: str | None,
    main_file: str | None,
    icon: str | None,
    version_filename: str | None,
    output_folder: str | None,
    include_files: tuple[str, ...],
    include_folders: tuple[str, ...],
    packages: tuple[str, ...],
    includes: tuple[str, ...],
    excludes: tuple[str, ...],
    output: str,
) -> None:
    """
    Generate a build.py script.

    Builds configuration from a config file, pyproject.toml, CLI options,
    and/or interactive prompts.  Sources are merged with the following
    priority (highest first):
    CLI options > config file > pyproject.toml > interactive prompts > defaults.

    \b
    Examples:
        ezcompiler generate build -c ezcompiler.yaml
        ezcompiler generate build --from-pyproject pyproject.toml
        ezcompiler generate build --from-pyproject pyproject.toml -I
        ezcompiler generate build -n myproject -v 2.0.0
    """

    printer = _get_printer()
    logger = _get_logger()

    try:
        # 1. Load base from pyproject.toml if requested
        config_dict: dict[str, Any] = {}
        if from_pyproject:
            config_dict = ConfigService.load_pyproject_as_dict(from_pyproject)
            printer.info(f"Loaded base configuration from {from_pyproject}")
            logger.info(f"Loaded base configuration from {from_pyproject}")

        # 2. Load from config file (YAML/JSON) and merge
        if config:
            config_path = Path(config)
            if config_path.suffix.lower() == ".yaml":
                with open(config_path, encoding="utf-8") as f:
                    file_config = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, encoding="utf-8") as f:
                    file_config = json.load(f)
            else:
                raise click.BadParameter("Configuration file must be YAML or JSON")
            config_dict = ConfigService.merge_configs(config_dict, file_config)

        # 3. Override with explicitly provided CLI options
        cli_overrides: dict[str, Any] = {}
        if version is not None:
            cli_overrides["version"] = version
        if project_name is not None:
            cli_overrides["project_name"] = project_name
        if project_description is not None:
            cli_overrides["project_description"] = project_description
        if company_name is not None:
            cli_overrides["company_name"] = company_name
        if author is not None:
            cli_overrides["author"] = author
        if main_file is not None:
            cli_overrides["main_file"] = main_file
        if icon is not None:
            cli_overrides["icon"] = icon
        if version_filename is not None:
            cli_overrides["version_filename"] = version_filename
        if output_folder is not None:
            cli_overrides["output_folder"] = output_folder
        if include_files:
            cli_overrides.setdefault("include_files", {})["files"] = list(include_files)
        if include_folders:
            cli_overrides.setdefault("include_files", {})["folders"] = list(
                include_folders
            )
        if packages:
            cli_overrides["packages"] = list(packages)
        if includes:
            cli_overrides["includes"] = list(includes)
        if excludes:
            cli_overrides["excludes"] = list(excludes)

        if cli_overrides:
            config_dict = ConfigService.merge_configs(config_dict, cli_overrides)

        # 4. Interactive prompts for missing required values
        if interactive:
            if not config_dict.get("project_name"):
                config_dict["project_name"] = click.prompt("Project name")
            if not config_dict.get("version"):
                config_dict["version"] = click.prompt("Version", default="1.0.0")
            if not config_dict.get("project_description"):
                config_dict["project_description"] = click.prompt(
                    "Project description", default=""
                )
            if not config_dict.get("company_name"):
                config_dict["company_name"] = click.prompt("Company name", default="")
            if not config_dict.get("author"):
                config_dict["author"] = click.prompt("Author", default="")
            if not config_dict.get("main_file"):
                config_dict["main_file"] = click.prompt("Main file", default="main.py")

        # 5. Apply defaults for anything still missing
        config_dict.setdefault("version", "1.0.0")
        config_dict.setdefault("project_description", "")
        config_dict.setdefault("company_name", "")
        config_dict.setdefault("author", "")
        config_dict.setdefault("main_file", "main.py")
        config_dict.setdefault("icon", "")
        config_dict.setdefault("version_filename", "version_info.txt")
        config_dict.setdefault("output_folder", "dist")
        config_dict.setdefault("include_files", {"files": [], "folders": []})
        config_dict.setdefault("packages", [])
        config_dict.setdefault("includes", [])
        config_dict.setdefault("excludes", ["debugpy", "test", "unittest"])

        # Validate: project_name is required
        if not config_dict.get("project_name"):
            raise click.UsageError(
                "Project name is required. Provide it via --project-name, "
                "--config, --from-pyproject, or --interactive"
            )

        # Ensure output directory exists
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate build.py using TemplateService
        template_service = _get_template_service()
        build_file_path = template_service.generate_setup_file(
            config_dict, output_dir=output_path
        )
        printer.success(f"build.py file generated: {build_file_path}")
        logger.info(f"build.py file generated: {build_file_path}")

    except (TemplateError, ConfigError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@generate.command(name="iss")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Script path (default: installer/<project_name>.iss).",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Overwrite an existing script.",
)
def generate_iss(output: Path | None, force: bool) -> None:
    """Generate an editable Inno Setup script from the project configuration.

    Auto-discovers pyproject.toml, ezcompiler.yaml, or ezcompiler.json.
    Once installer.iss_path is set, script-generation options are ignored;
    edit the script itself to customize the installer.
    """
    printer = _get_printer()
    logger = _get_logger()
    try:
        config_obj = ConfigService.build_compiler_config()
        output_path = output or Path("installer") / f"{config_obj.project_name}.iss"
        target = InstallerService.generate_iss_script(
            config_obj, output_path, force=force
        )
        printer.success(f"Inno Setup script generated: {target}")
        printer.info("Add to [tool.ezcompiler.installer]:")
        printer.info(tomli_w.dumps({"iss_path": target.as_posix()}).strip())
        printer.warning(
            "With iss_path set, installer script-generation options are ignored; "
            "edit the .iss file to change them."
        )
        logger.info("Inno Setup script generated: %s", target)
    except (InstallerError, ConfigError, ConfigurationError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@generate.command(name="template")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["config", "build", "version"]),
    required=True,
    help="Template type to generate",
)
@click.option(
    "--format",
    "-f",
    type=str,
    help="Template format (yaml/json for config, py for build, txt for version)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=".",
    help="Output directory (default: .)",
)
@click.option(
    "--filename",
    "-N",
    type=str,
    default="",
    help="Filename to write (default derived from type/format)",
)
@click.option(
    "--mockup",
    "-m",
    is_flag=True,
    help="Generate with mockup values instead of placeholders",
)
def template_raw(
    type: str, format: str | None, output: str, filename: str, mockup: bool
) -> None:
    """
    Generate a raw template file.

    Generates templates with either placeholders or mockup values.
    Useful for creating baseline configuration or template files.
    """
    printer = _get_printer()
    logger = _get_logger()

    try:
        # Define allowed formats and default filenames
        allowed_formats = {
            "config": ["yaml", "json"],
            "build": ["py"],
            "version": ["txt"],
        }
        default_filenames = {
            ("config", "yaml"): "ezcompiler.yaml",
            ("config", "json"): "ezcompiler.json",
            ("build", "py"): "build.py",
            ("version", "txt"): "version_info.txt",
        }

        # Determine default format when missing
        if not format:
            format = {
                "config": "yaml",
                "build": "py",
                "version": "txt",
            }[type]

        # Validate format value
        if format not in allowed_formats[type]:
            raise click.BadParameter(
                f"Invalid format '{format}' for type '{type}'. "
                f"Valid formats: {allowed_formats[type]}"
            )

        # Determine default filename when missing
        if not filename:
            filename = default_filenames[(type, format)]

        # Initialize template service
        template_service = _get_template_service()

        # Write file to disk
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        target = output_path / filename

        if mockup:
            template_service.generate_mockup_template(type, format, target)
            printer.success(f"Template with mockup values generated: {target}")
            logger.info(f"Template with mockup values generated: {target}")
        else:
            template_service.generate_raw_template(type, format, target)
            printer.success(f"Raw template generated: {target}")
            logger.info(f"Raw template generated: {target}")

    except TemplateError as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@main.command(name="compile")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Config file path (YAML, JSON)",
)
@click.option(
    "--pyproject",
    "-p",
    type=click.Path(exists=True),
    help="Explicit pyproject.toml path",
)
@click.option(
    "--compiler",
    type=click.Choice(["Cx_Freeze", "PyInstaller", "Nuitka"]),
    default=None,
    help="Compiler to use (overrides config)",
)
@click.option(
    "--console/--no-console",
    default=None,
    help="Show console window (overrides config)",
)
@click.option(
    "--output-folder",
    "-o",
    type=click.Path(),
    default=None,
    help="Output folder (overrides config)",
)
@click.option(
    "--debug",
    "-dbg",
    is_flag=True,
    default=False,
    help="Enable debug mode",
)
@click.option(
    "--no-zip",
    is_flag=True,
    default=False,
    help="Skip ZIP archive creation",
)
@click.option(
    "--skip-installer",
    is_flag=True,
    default=False,
    help="Skip the Inno Setup installer stage even if installer_enabled=True",
)
@click.option(
    "--skip-release",
    is_flag=True,
    default=False,
    help="Skip the TUF release stage even if tuf_enabled=True",
)
@click.option(
    "--skip-build",
    is_flag=True,
    default=False,
    help=(
        "Skip version generation and compilation; resume from the existing "
        "build in output_folder (zip, installer, release)"
    ),
)
@click.option(
    "--required",
    is_flag=True,
    default=False,
    help="Marquer la version produite comme obligatoire pour les clients TUF",
)
def compile_project(
    config: str | None,
    pyproject: str | None,
    compiler: str | None,
    console: bool | None,
    output_folder: str | None,
    debug: bool,
    no_zip: bool,
    skip_installer: bool,
    skip_release: bool,
    skip_build: bool,
    required: bool,
) -> None:
    """
    Compile the project (full build pipeline).

    Auto-discovers configuration from pyproject.toml, ezcompiler.yaml,
    or ezcompiler.json. CLI options override config file values.

    Runs version -> compile -> zip, plus the installer and TUF release
    stages when enabled in the config (installer_enabled / tuf_enabled).
    Publication is a separate step: run `ezcompiler publish` afterwards.
    Use --skip-build to resume after a previous compile (zip, installer and
    release run against the existing output_folder).

    Examples:

        ezcompiler compile

        ezcompiler compile --config ezcompiler.yaml

        ezcompiler compile --pyproject ../myproject/pyproject.toml

        ezcompiler compile --compiler PyInstaller --no-console

        ezcompiler compile --skip-installer --skip-release

        ezcompiler compile --skip-build

        ezcompiler compile --required
    """
    printer = _get_printer()
    logger = _get_logger()

    # Config loading
    try:
        # Build CLI overrides (only explicitly provided values)
        cli_overrides: dict[str, Any] = {}
        if compiler is not None:
            cli_overrides["compiler"] = compiler
        if console is not None:
            cli_overrides["console"] = console
        if output_folder is not None:
            cli_overrides["output_folder"] = output_folder
        if debug:
            cli_overrides["debug"] = True

        # Load config with cascade
        config_obj = ConfigService.build_compiler_config(
            config_path=Path(config) if config else None,
            pyproject_path=Path(pyproject) if pyproject else None,
            cli_overrides=cli_overrides or None,
        )
    except ConfigurationError as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)

    # Validate --required flag
    if required and (skip_release or not config_obj.tuf_enabled):
        raise click.UsageError(
            "--required n'a d'effet que si l'étape release TUF s'exécute "
            "(tuf_enabled, sans --skip-release)."
        )

    # Delegate to the shared pipeline so installer and TUF release stages run
    # when enabled in the config — identical behaviour to EzCompiler.run_pipeline.
    from .python_api import EzCompiler  # noqa: PLC0415

    try:
        EzCompiler(config=config_obj).run_pipeline(
            console=config_obj.console,
            compiler=config_obj.compiler,
            skip_zip=no_zip,
            skip_installer=skip_installer,
            skip_release=skip_release,
            skip_build=skip_build,
            required=required,
        )
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
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@main.command(name="upload")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Config file path (YAML, JSON)",
)
@click.option(
    "--pyproject",
    "-p",
    type=click.Path(exists=True),
    help="Explicit pyproject.toml path",
)
@click.option(
    "--repo-destination",
    "-rd",
    "repo_destination",
    type=click.Choice(["disk", "server", "r2"]),
    default=None,
    help="Backend pour l'arbre TUF (overrides config)",
)
@click.option(
    "--release-destination",
    "-rld",
    "release_destination",
    type=click.Choice(["disk", "server", "r2"]),
    default=None,
    help="Backend pour le zip installeur (overrides config)",
)
@click.option(
    "--destination",
    "-d",
    "destination",
    default=None,
    help="Destination commune (override pour repo et release)",
)
def upload_command(
    config: str | None,
    pyproject: str | None,
    repo_destination: RepoDestination | None,
    release_destination: ReleaseDestination | None,
    destination: str | None,
) -> None:
    """[Déprécié] Utiliser `ezcompiler publish update` / `publish release`.

    Raccourci qui enchaîne `publish update` (si tuf_enabled) puis
    `publish release`, sans confirmation. Les publications sur plateforme
    (github) sont refusées : utiliser `publish release`, qui les confirme.

    Exemples :

        ezcompiler upload --config ezcompiler.yaml

        ezcompiler upload --repo-destination r2 --destination uploads/
    """
    printer = _get_printer()
    logger = _get_logger()
    printer.warning(
        "`ezcompiler upload` est déprécié et sera retiré en v5. "
        "Utiliser `ezcompiler publish update` puis "
        "`ezcompiler publish release`."
    )
    try:
        cfg = ConfigService.build_compiler_config(
            config_path=Path(config) if config else None,
            pyproject_path=Path(pyproject) if pyproject else None,
        )
    except ConfigurationError as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)

    rel_dest = release_destination or cfg.release_destination
    if rel_dest not in ("disk", "server", "r2"):
        printer.error(
            f"`ezcompiler upload` ne publie pas sur {rel_dest} : une release "
            "de plateforme demande confirmation. Utiliser "
            "`ezcompiler publish update` puis `ezcompiler publish release`."
        )
        sys.exit(1)

    # Délègue aux commandes publish avec --yes implicite (spec §8) : upload
    # reste non interactif. Un échec de l'arbre TUF sort avant la release.
    ctx = click.get_current_context()
    common = {"config": config, "pyproject": pyproject, "destination": destination}
    if cfg.tuf_enabled:
        ctx.invoke(
            publish_update_command,
            repo_destination=repo_destination,
            yes=True,
            **common,
        )
    ctx.invoke(
        publish_release_command,
        release_destination=release_destination,
        yes=True,
        **common,
    )


# ///////////////////////////////////////////////////////////////
# PUBLISH COMMANDS
# ///////////////////////////////////////////////////////////////


def _force_utf8_stdout() -> None:
    """Évite les UnicodeEncodeError sur une console Windows cp1252."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _read_notes_file(path: Path) -> str:
    """Read a release-notes file as UTF-8, or fail as a usage error."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise click.BadParameter(
            f"{path} n'est pas encodé en UTF-8 ({e.reason}).",
            param_hint="--notes-file",
        ) from None


def _format_size(num_bytes: int) -> str:
    """Formate une taille en octets de façon lisible."""
    size = float(num_bytes)
    for unit in ("o", "Ko", "Mo", "Go"):
        if size < 1024 or unit == "Go":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} Go"


def _describe_update_target(
    cfg: CompilerConfig, repo_dest: str, destination: str | None
) -> str:
    """Where ``publish update`` will land, mirroring UploaderService."""
    if repo_dest == "r2":
        return f"r2://{cfg.repo_endpoint} (bucket/préfixe)"
    base = destination or cfg.resolved_repo_destination or ""
    if repo_dest == "server":
        return base.rstrip("/") + "/update/"
    return str(Path(base or ".") / "update")


@main.group()
def publish() -> None:
    """Publier l'arbre de mise à jour TUF ou une release.

    Séparée du pipeline de build : la publication est un acte délibéré,
    irréversible, et demande confirmation (sauf --yes).
    """


@publish.command("release")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Config file path (YAML, JSON)"
)
@click.option(
    "--pyproject",
    "-p",
    type=click.Path(exists=True),
    help="Explicit pyproject.toml path",
)
@click.option(
    "--release-destination",
    "-rld",
    "release_destination",
    type=click.Choice(["disk", "server", "r2", "github", "gitlab"]),
    default=None,
    help="Backend de publication (overrides config)",
)
@click.option("--destination", "-d", default=None, help="Destination (override config)")
@click.option("--tag", default=None, help="Tag de la release (défaut : v<version>)")
@click.option("--title", default=None, help="Titre (défaut : <projet> v<version>)")
@click.option("--notes", default=None, help="Corps de la release (littéral)")
@click.option(
    "--notes-file",
    "notes_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Fichier contenant le corps de la release",
)
@click.option(
    "--prerelease/--no-prerelease",
    "prerelease",
    default=None,
    help="Force l'étiquette pré-release (défaut : déduite de la version)",
)
@click.option("--draft", is_flag=True, help="Créer la release non publiée")
@click.option("--yes", "-y", is_flag=True, help="Ne pas demander de confirmation")
def publish_release_command(
    config: str | None,
    pyproject: str | None,
    release_destination: str | None,
    destination: str | None,
    tag: str | None,
    title: str | None,
    notes: str | None,
    notes_file: Path | None,
    prerelease: bool | None,
    draft: bool,
    yes: bool,
) -> None:
    """Publier l'installeur et le zip comme release.

    Sur github, crée une Release attachant les artefacts. Sur disk, server
    ou r2, copie les fichiers vers la destination configurée.

    Exemples :

        ezcompiler publish release

        ezcompiler publish release --yes --notes-file CHANGELOG.md
    """
    _force_utf8_stdout()
    printer = _get_printer()
    logger = _get_logger()

    if notes and notes_file:
        raise click.UsageError("--notes et --notes-file sont mutuellement exclusives.")

    try:
        cfg = ConfigService.build_compiler_config(
            config_path=Path(config) if config else None,
            pyproject_path=Path(pyproject) if pyproject else None,
        )

        resolved_tag = tag or f"v{cfg.version}"
        resolved_title = title or f"{cfg.project_name} v{cfg.version}"
        is_pre = is_prerelease(cfg.version) if prerelease is None else prerelease

        publisher = PublishService.resolve_publisher(cfg, release_destination)

        # Chemin fichiers (disk/server/r2) : comportement historique, sans
        # confirmation — rien n'est irréversible côté clients. Les assets sont
        # réassemblés dans release/ par le service, comme avant.
        if publisher is None:
            ignored = [
                flag
                for flag, given in (
                    ("--tag", tag),
                    ("--title", title),
                    ("--notes", notes),
                    ("--notes-file", notes_file),
                    ("--draft", draft),
                    ("--prerelease/--no-prerelease", prerelease is not None),
                )
                if given
            ]
            if ignored:
                printer.warning(
                    f"Ignoré(s) hors plateforme de release : {', '.join(ignored)}."
                )
            PublishService.publish_release(
                cfg,
                [],
                tag=resolved_tag,
                title=resolved_title,
                destination=destination,
                release_destination=release_destination,
            )
            printer.success("Assets de release transférés")
            logger.info("Release assets uploaded")
            return

        if destination:
            raise click.UsageError(
                "--destination ne s'applique pas à une publication sur "
                "plateforme : le dépôt vient de release_endpoint (owner/repo)."
            )

        # Toutes les vérifications passent AVANT le récapitulatif : quand
        # l'opérateur confirme, il ne reste qu'un risque réseau.
        body = _read_notes_file(notes_file) if notes_file else notes
        publisher.preflight()
        if publisher.exists(resolved_tag):
            printer.error(
                f"La release {resolved_tag} existe déjà. "
                "Supprime-la ou change de version."
            )
            sys.exit(1)

        assets = PipelineService.stage_versioned_assets(cfg)

        printer.info("─" * 60)
        printer.info(f"Release à publier via {publisher.get_publisher_name()}")
        printer.info(
            f"   Dépôt      : {cfg.release_endpoint or '(déduit du remote git courant)'}"
        )
        printer.info(f"   Tag        : {resolved_tag}")
        printer.info(f"   Titre      : {resolved_title}")
        printer.info(f"   Pré-release: {'oui' if is_pre else 'non'}")
        printer.info(f"   Brouillon  : {'oui' if draft else 'non'}")
        printer.info(
            f"   Notes      : {'fournies' if body else 'générées automatiquement'}"
        )
        printer.info("   Artefacts  :")
        for asset in assets:
            printer.info(
                f"     - {asset.name}   ({_format_size(asset.stat().st_size)})"
            )
        printer.info("─" * 60)

        if not yes and not click.confirm("Publier cette release ?", default=False):
            printer.info("Annulé.")
            sys.exit(1)

        url = PublishService.publish_release(
            cfg,
            assets,
            tag=resolved_tag,
            title=resolved_title,
            notes=body,
            prerelease=is_pre,
            draft=draft,
            release_destination=release_destination,
            publisher=publisher,
        )
        printer.success(f"Release {resolved_tag} publiée : {url}")
        logger.info("Release %s published: %s", resolved_tag, url)

    except (ConfigurationError, PublishError, UploadError, ReleaseError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@publish.command("update")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Config file path (YAML, JSON)"
)
@click.option(
    "--pyproject",
    "-p",
    type=click.Path(exists=True),
    help="Explicit pyproject.toml path",
)
@click.option(
    "--repo-destination",
    "-rd",
    "repo_destination",
    type=click.Choice(["disk", "server", "r2"]),
    default=None,
    help="Backend pour l'arbre TUF (overrides config)",
)
@click.option("--destination", "-d", default=None, help="Destination (override config)")
@click.option("--yes", "-y", is_flag=True, help="Ne pas demander de confirmation")
def publish_update_command(
    config: str | None,
    pyproject: str | None,
    repo_destination: str | None,
    destination: str | None,
    yes: bool,
) -> None:
    """Publier l'arbre de mise à jour TUF.

    C'est la plus irréversible des deux publications : les versions de
    métadonnées TUF sont monotones et les clients auto-updatent sans
    action humaine. On ne dépublie pas, on republie plus haut.

    Exemples :

        ezcompiler publish update

        ezcompiler publish update --repo-destination r2 --yes
    """
    _force_utf8_stdout()
    printer = _get_printer()
    logger = _get_logger()

    try:
        cfg = ConfigService.build_compiler_config(
            config_path=Path(config) if config else None,
            pyproject_path=Path(pyproject) if pyproject else None,
        )

        repo_dir = cfg.tuf_repo_dir or (cfg.output_folder / "repo")
        # Lit la version dans l'arbre signé lui-même : c'est elle que les
        # clients recevront, pas forcément celle de la config.
        tree_version = TufService.read_tree_version(cfg)

        repo_dest = repo_destination or cfg.repo_destination
        if repo_dest == "r2" and destination:
            printer.warning(
                "--destination est ignoré avec r2 : la cible vient de "
                "repo_endpoint (bucket/préfixe)."
            )
        target = _describe_update_target(cfg, repo_dest, destination)
        file_count = sum(1 for f in repo_dir.rglob("*") if f.is_file())

        printer.info("─" * 60)
        printer.info("Arbre de mise à jour TUF à publier")
        printer.info(f"   Backend    : {repo_dest}")
        printer.info(f"   Destination: {target}")
        printer.info(f"   Version    : {tree_version}")
        printer.info(f"   Fichiers   : {file_count}")
        printer.info("─" * 60)
        if not TufService.same_version(tree_version, cfg.version):
            printer.warning(
                f"La configuration annonce {cfg.version}, mais l'arbre signé "
                f"porte {tree_version} : c'est {tree_version} qui sera publiée. "
                "Relancer le pipeline si ce n'est pas voulu."
            )
        printer.warning(
            f"Les clients installés passeront en {tree_version} automatiquement. "
            "Cette publication ne peut pas être annulée, seulement remplacée "
            "par une version supérieure."
        )

        if not yes and not click.confirm("Publier cet arbre ?", default=False):
            printer.info("Annulé.")
            sys.exit(1)

        PublishService.publish_update(
            cfg, destination=destination, repo_destination=repo_destination
        )
        printer.success(f"Arbre TUF publié ({repo_dest})")
        logger.info("TUF update tree published (%s)", repo_dest)

    except (ConfigurationError, UploadError, ReleaseError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@main.command()
@click.argument(
    "format_type",
    type=click.Choice(["yaml", "json", "pyproject"], case_sensitive=False),
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Output directory (defaults to current working directory)",
)
def init(
    format_type: str,
    output_dir: Path | None,
) -> None:
    """
    Initialize a new EzCompiler project with FORMAT_TYPE configuration.

    FORMAT_TYPE must be one of: yaml, json, pyproject.

    \b
    Examples:
        ezcompiler init yaml
        ezcompiler init json -o ./configs
        ezcompiler init pyproject -o ../my-project
    """
    printer = _get_printer()
    logger = _get_logger()

    try:
        # Resolve output directory (default: CWD)
        output_dir = output_dir or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)

        printer.info(f"Initializing EzCompiler project in {output_dir}...")

        # Collect basic project information via prompts (outside progress bar)
        project_name = click.prompt("Project name")
        version = click.prompt("Version", default="1.0.0")
        project_description = click.prompt("Project description", default="")
        company_name = click.prompt("Company name", default="")
        author = click.prompt("Author", default="")
        main_file = click.prompt("Main file", default="main.py")

        # Build configuration dictionary with sensible defaults
        config_dict: dict[str, Any] = {
            "version": version,
            "project_name": project_name,
            "project_description": project_description,
            "company_name": company_name,
            "author": author,
            "main_file": main_file,
            "icon": "",
            "version_filename": "version_info.txt",
            "output_folder": "dist",
            "include_files": {"files": [], "folders": []},
            "packages": [],
            "includes": [],
            "excludes": ["debugpy", "test", "unittest"],
            "compilation": {
                "console": True,
                "compiler": "PyInstaller",
            },
            "upload": {
                "repo_destination": "disk",
                "release_destination": "disk",
                "repo_endpoint": "",
                "release_endpoint": "",
            },
            "optimize": True,
            "strip": False,
            "advanced": {"debug": False},
        }

        # File generation with progress tracking
        stages: list[StageConfig] = [
            {
                "name": "config",
                "type": "spinner",
                "description": f"Generating {format_type} configuration",
            },
            {"name": "build", "type": "spinner", "description": "Generating build.py"},
        ]

        template_service = _get_template_service()
        current_phase = "config"
        pipeline_error: Exception | None = None

        with printer.wizard.dynamic_layered_progress(stages) as dlp:
            try:
                # Config file generation
                current_phase = "config"
                dlp.update_layer("config", 0, f"Writing {format_type} file...")

                if format_type == "yaml":
                    yaml_content = template_service.process_config_template(
                        "yaml", config_dict
                    )
                    target = output_dir / "ezcompiler.yaml"
                    target.write_text(yaml_content, encoding="utf-8")
                    logger.info(f"ezcompiler.yaml generated: {target}")

                elif format_type == "json":
                    json_content = template_service.process_config_template(
                        "json", config_dict
                    )
                    target = output_dir / "ezcompiler.json"
                    target.write_text(json_content, encoding="utf-8")
                    logger.info(f"ezcompiler.json generated: {target}")

                else:  # pyproject
                    _create_or_update_pyproject(
                        output_dir / "pyproject.toml", config_dict
                    )

                dlp.complete_layer("config")

                # Setup file generation
                current_phase = "build"
                dlp.update_layer("build", 0, "Processing template...")
                template_service.generate_setup_file(config_dict, output_dir=output_dir)
                logger.info(f"build.py generated: {output_dir / 'build.py'}")
                dlp.complete_layer("build")

            except (TemplateError, ConfigError) as e:
                dlp.handle_error(current_phase, str(e))
                dlp.emergency_stop(str(e))
                pipeline_error = e
            except Exception as e:
                dlp.handle_error(current_phase, str(e))
                dlp.emergency_stop(str(e))
                pipeline_error = e

        if pipeline_error:
            printer.error(str(pipeline_error))
            logger.error(str(pipeline_error))
            sys.exit(1)

        printer.success("EzCompiler project initialized successfully")
        printer.tip("Run 'ezcompiler compile' to build your project.")

    except (TemplateError, ConfigError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@main.group()
def tuf() -> None:
    """Arbre de mise à jour TUF local : clés, état, retrait de version.

    Ces commandes ne modifient que l'arbre local ; `ezcompiler publish
    update` le publie.
    """


@tuf.command("init")
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to ezcompiler config file (auto-detected if omitted).",
)
def tuf_init(config_path: Path | None) -> None:
    """Initialise TUF signing keys and repository skeleton.

    Run once per project, before the first `ezcompiler compile` with
    tuf_enabled = true. Keys are written to tuf_keys_dir (config).
    Safe to re-run: skips silently when keys already exist.
    """
    printer = _get_printer()
    logger = _get_logger()
    try:
        config_service = ConfigService()
        cfg = config_service.load_config(config_path)
        from ..shared import CompilerConfig  # noqa: PLC0415

        compiler_config = CompilerConfig.from_dict(cfg)
        repo_dir = compiler_config.tuf_repo_dir or (
            compiler_config.output_folder / "repo"
        )
        keys_dir = compiler_config.tuf_keys_dir or (repo_dir / "keystore")
        initialized = ReleaseService.init_release(
            app_name=compiler_config.project_name,
            repo_dir=repo_dir,
            keys_dir=keys_dir,
            releaser_config={
                "keys_dir": keys_dir,
                "expiration_days": compiler_config.tuf_expiration_days,
            },
        )
        if initialized:
            printer.success(f"TUF keys initialized in {keys_dir}")
            logger.info("TUF keys initialized: %s", keys_dir)
        else:
            printer.info(f"Keys already present in {keys_dir} — skipped.")
            logger.info("TUF keys already present, skipped.")
    except (ReleaseError, SigningKeyError, ConfigError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@tuf.command("refresh")
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to ezcompiler config file (auto-detected if omitted).",
)
@click.option(
    "--role",
    "roles",
    multiple=True,
    default=("targets", "snapshot", "timestamp"),
    help="TUF role(s) to refresh (repeatable). Default: targets/snapshot/timestamp.",
)
@click.option(
    "--days",
    "days",
    type=int,
    default=None,
    help="Expiration in days from now (default: config tuf_expiration_days).",
)
def tuf_refresh(
    config_path: Path | None,
    roles: tuple[str, ...],
    days: int | None,
) -> None:
    """Re-sign TUF metadata to extend expiration without a new release.

    Native tufup keep-alive for projects updated irregularly: repushes the
    expiration date of the short-lived roles so clients keep trusting the
    repository between releases. Requires signing keys (`tuf init`).
    """
    printer = _get_printer()
    logger = _get_logger()
    try:
        config_service = ConfigService()
        cfg = config_service.load_config(config_path)
        from ..shared import CompilerConfig  # noqa: PLC0415

        compiler_config = CompilerConfig.from_dict(cfg)
        from .python_api import EzCompiler  # noqa: PLC0415

        repo = EzCompiler(config=compiler_config).refresh_release_expiration(
            roles=roles,
            days=days,
        )
        printer.success(f"TUF metadata expiration refreshed in {repo}")
        logger.info("TUF metadata expiration refreshed: %s", repo)
    except (ReleaseError, SigningKeyError, ConfigError, ConfigurationError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


_EXPIRY_WARN_DAYS = 7


@tuf.command("status")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Config file path (YAML, JSON)"
)
@click.option(
    "--pyproject",
    "-p",
    type=click.Path(exists=True),
    help="Explicit pyproject.toml path",
)
def tuf_status(config: str | None, pyproject: str | None) -> None:
    """Afficher l'état de l'arbre TUF local (lecture seule).

    Versions signées, drapeaux, expirations des rôles et versions retirées.

    Exemple :

        ezcompiler tuf status
    """
    _force_utf8_stdout()
    printer = _get_printer()
    logger = _get_logger()
    try:
        cfg = ConfigService.build_compiler_config(
            config_path=Path(config) if config else None,
            pyproject_path=Path(pyproject) if pyproject else None,
        )
        status = TufService.status(cfg)
    except (ConfigurationError, ReleaseError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)

    printer.info(f"Arbre TUF : {status.repo_dir}")
    printer.info("Versions (de la plus récente à la plus ancienne)")
    if not status.versions:
        printer.info("   (aucune)")
    for v in status.versions:
        flags = [
            f for f, on in (("obligatoire", v.required), ("patch", v.has_patch)) if on
        ]
        printer.info(f"   {v.version:<12} {'  '.join(flags)}".rstrip())

    printer.info("Expirations")
    now = datetime.now(UTC)
    for role, expires in status.expirations.items():
        refresh = "ezcompiler tuf refresh" + (" --role root" if role == "root" else "")
        days = (expires - now).days
        line = f"   {role:<10} {expires:%Y-%m-%d}   ({days} j)"
        if expires <= now:
            printer.error(f"{line}   expiré : lancer `{refresh}`")
        elif days < _EXPIRY_WARN_DAYS:
            printer.warning(f"{line}   expire bientôt : lancer `{refresh}`")
        else:
            printer.info(line)

    printer.info("Versions retirées : " + (", ".join(status.withdrawn) or "aucune"))


def _deprecated_alias(target: click.Command, old: str, new: str) -> click.Command:
    """Build a hidden-group alias of ``target`` that warns before delegating.

    The alias copies the target's parameters, so every option given to the
    old spelling reaches the new command unchanged.
    """

    def callback(**kwargs: Any) -> None:
        _get_printer().warning(
            f"`ezcompiler {old}` est déprécié et sera retiré en v5. "
            f"Utiliser `ezcompiler {new}`."
        )
        click.get_current_context().invoke(target, **kwargs)

    return click.Command(
        name=target.name,
        params=list(target.params),
        callback=callback,
        help=f"[Déprécié] Alias de `ezcompiler {new}`.",
    )


@main.group(hidden=True)
def release() -> None:
    """[Déprécié] Utiliser `ezcompiler tuf` à la place."""


release.add_command(_deprecated_alias(tuf_init, "release init", "tuf init"))
release.add_command(_deprecated_alias(tuf_refresh, "release refresh", "tuf refresh"))


@main.group()
def updater() -> None:
    """Updater client generation (tufup)."""


@updater.command("generate")
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to ezcompiler config file (auto-detected if omitted).",
)
@click.option(
    "--output-dir",
    "output_dir",
    default=None,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory where updater files are written (default: main_file directory).",
)
@click.option(
    "--no-patch",
    "no_patch",
    is_flag=True,
    default=False,
    help="Do not add generated files to include_files.",
)
def updater_generate(
    config_path: Path | None,
    output_dir: Path | None,
    no_patch: bool,
) -> None:
    """Generate update.py, settings.py, and copy root.json for the compiled app.

    Run before compiling. The generated files must be included in the
    bundle (done automatically unless --no-patch is specified).
    """
    printer = _get_printer()
    logger = _get_logger()
    try:
        config_service = ConfigService()
        cfg_dict = config_service.load_config(config_path)
        from ..shared import CompilerConfig  # noqa: PLC0415

        compiler_config = CompilerConfig.from_dict(cfg_dict)
        resolved_dir = output_dir or Path(compiler_config.main_file).parent
        files = UpdaterService.generate(compiler_config, resolved_dir)

        if not no_patch:
            compiler_config.include_files["files"].extend(str(f) for f in files)

        printer.success(f"Updater files generated in {resolved_dir}")
        for f in files:
            printer.info(f"  {f.name}")
        logger.info("Updater generated: %s", [str(f) for f in files])

    except Exception as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


def _create_or_update_pyproject(path: Path, config_dict: dict[str, Any]) -> None:
    """Create or update a pyproject.toml with the [tool.ezcompiler] section."""
    printer = _get_printer()
    logger = _get_logger()

    # Read existing file or start empty
    data: dict[str, Any] = {}
    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        printer.info(f"Updating existing pyproject.toml: {path}")
    else:
        printer.info(f"Creating new pyproject.toml: {path}")

    # Add/update [tool.ezcompiler] section
    if "tool" not in data:
        data["tool"] = {}
    data["tool"]["ezcompiler"] = config_dict

    # Write back
    with open(path, "wb") as f:
        tomli_w.dump(data, f)

    printer.success(f"pyproject.toml updated: {path}")
    logger.info(f"pyproject.toml updated: {path}")


if __name__ == "__main__":
    main()
