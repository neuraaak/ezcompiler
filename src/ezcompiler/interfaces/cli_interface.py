# ///////////////////////////////////////////////////////////////
# CLI_INTERFACE - Command-line interface for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
CLI interface - Command-line interface for EzCompiler.

This module provides a Click-based CLI for generating configuration files,
setup.py files, version files, and initializing new EzCompiler projects.

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
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import logging

    from ezplog.handlers.wizard.dynamic import StageConfig
    from ezplog.lib_mode import _LazyPrinter

# Third-party imports
import click
import tomli_w
import yaml
from ezplog.lib_mode import get_logger, get_printer

# Local imports
from .._version import __version__
from ..services import ConfigService, PipelineService, TemplateService, UploaderService
from ..shared.exceptions import (
    CompilationError,
    ConfigError,
    ConfigurationError,
    TemplateError,
    UploadError,
    VersionError,
    ZipError,
)

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
_pipeline_service: PipelineService | None = None


def _get_template_service() -> TemplateService:
    """Get the shared TemplateService instance (created once, reused across commands)."""
    global _template_service  # noqa: PLW0603
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service


def _get_pipeline_service() -> PipelineService:
    """Get the shared PipelineService instance (injectable in tests via module attribute)."""
    global _pipeline_service  # noqa: PLW0603
    if _pipeline_service is None:
        _pipeline_service = PipelineService()
    return _pipeline_service


# ///////////////////////////////////////////////////////////////
# CLI COMMANDS AND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="EzCompiler")
def main() -> None:
    """
    EzCompiler - CLI for Python project compilation and distribution.

    Generates configuration files, setup.py, and version files from templates
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
    type=click.Choice(["yaml", "json"]),
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
    type=click.Choice(["auto", "Cx_Freeze", "PyInstaller", "Nuitka"]),
    default=None,
    help="Compiler to use",
)
@click.option(
    "--zip-needed",
    "-z",
    is_flag=True,
    default=True,
    help="Create ZIP archive (default: True)",
)
@click.option(
    "--repo-needed",
    "-r",
    is_flag=True,
    default=False,
    help="Require repository upload (default: False)",
)
@click.option(
    "--upload-structure",
    "-us",
    type=click.Choice(["disk", "server"]),
    default=None,
    help="Upload structure",
)
@click.option(
    "--repo-path",
    "-rp",
    default=None,
    help="Repository path",
)
@click.option("--server-url", "-su", default=None, help="Server URL for upload")
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
    zip_needed: bool,
    repo_needed: bool,
    upload_structure: str | None,
    repo_path: str | None,
    server_url: str | None,
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
        if upload_structure is not None:
            cli_overrides.setdefault("upload", {})["structure"] = upload_structure
        if repo_path is not None:
            cli_overrides.setdefault("upload", {})["repo_path"] = repo_path
        if server_url is not None:
            cli_overrides.setdefault("upload", {})["server_url"] = server_url

        # Flags always have a value — include them
        cli_overrides.setdefault("compilation", {}).update(
            {"console": console, "zip_needed": zip_needed, "repo_needed": repo_needed}
        )
        cli_overrides.setdefault("advanced", {}).update(
            {"optimize": optimize, "strip": strip, "debug": debug}
        )

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
                "compiler": "auto",
                "zip_needed": True,
                "repo_needed": False,
            },
        )
        config_dict.setdefault(
            "upload", {"structure": "disk", "repo_path": "releases", "server_url": ""}
        )
        config_dict.setdefault(
            "advanced", {"optimize": True, "strip": False, "debug": False}
        )

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
        content = template_service.process_config_template(format, config_dict)
        filename = "ezcompiler.yaml" if format == "yaml" else "ezcompiler.json"
        target = output_path / filename
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
def setup(
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
    Generate a setup.py file.

    Builds configuration from a config file, pyproject.toml, CLI options,
    and/or interactive prompts.  Sources are merged with the following
    priority (highest first):
    CLI options > config file > pyproject.toml > interactive prompts > defaults.

    \b
    Examples:
        ezcompiler generate setup -c ezcompiler.yaml
        ezcompiler generate setup --from-pyproject pyproject.toml
        ezcompiler generate setup --from-pyproject pyproject.toml -I
        ezcompiler generate setup -n myproject -v 2.0.0
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

        # Generate setup.py using TemplateService
        template_service = _get_template_service()
        setup_file_path = template_service.generate_setup_file(
            config_dict, output_dir=output_path
        )
        printer.success(f"setup.py file generated: {setup_file_path}")
        logger.info(f"setup.py file generated: {setup_file_path}")

    except (TemplateError, ConfigError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@generate.command(name="template")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["config", "setup", "version"]),
    required=True,
    help="Template type to generate",
)
@click.option(
    "--format",
    "-f",
    type=str,
    help="Template format (yaml/json for config, py for setup, txt for version)",
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
            "setup": ["py"],
            "version": ["txt"],
        }
        default_filenames = {
            ("config", "yaml"): "ezcompiler.yaml",
            ("config", "json"): "ezcompiler.json",
            ("setup", "py"): "setup.py",
            ("version", "txt"): "version_info.txt",
        }

        # Determine default format when missing
        if not format:
            format = {
                "config": "yaml",
                "setup": "py",
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
    type=click.Choice(["auto", "Cx_Freeze", "PyInstaller", "Nuitka"]),
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
    "--no-upload",
    is_flag=True,
    default=False,
    help="Skip upload step",
)
@click.option(
    "--upload-structure",
    "-us",
    type=click.Choice(["disk", "server"]),
    default=None,
    help="Upload structure (overrides config)",
)
@click.option(
    "--upload-destination",
    "-ud",
    default=None,
    help="Upload destination path or URL (overrides config)",
)
def compile_project(
    config: str | None,
    pyproject: str | None,
    compiler: str | None,
    console: bool | None,
    output_folder: str | None,
    debug: bool,
    no_zip: bool,
    no_upload: bool,
    upload_structure: str | None,
    upload_destination: str | None,
) -> None:
    """
    Compile the project.

    Auto-discovers configuration from pyproject.toml, ezcompiler.yaml,
    or ezcompiler.json. CLI options override config file values.

    Examples:

        ezcompiler compile

        ezcompiler compile --config ezcompiler.yaml

        ezcompiler compile --pyproject ../myproject/pyproject.toml

        ezcompiler compile --compiler PyInstaller --no-console

        ezcompiler compile --upload-structure disk --upload-destination releases/
    """
    printer = _get_printer()
    logger = _get_logger()

    # Phase 1: Config loading (outside progress - needed to build stages)
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
        if upload_structure is not None:
            cli_overrides["upload_structure"] = upload_structure
        if upload_destination is not None:
            cli_overrides["repo_path"] = upload_destination

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

    should_zip = not no_zip and config_obj.zip_needed
    should_upload = not no_upload and (
        upload_structure is not None or config_obj.repo_needed
    )

    # Build dynamic stages based on config
    stages: list[StageConfig] = PipelineService.build_stages(  # type: ignore[assignment]
        config_obj, should_zip=should_zip, should_upload=should_upload
    )

    # Phase 2-5: Execute pipeline with progress
    current_phase = "version"
    pipeline_error: Exception | None = None

    with printer.wizard.dynamic_layered_progress(stages) as dlp:
        try:
            # Version file generation
            current_phase = "version"
            dlp.update_layer("version", 0, "Processing template...")
            template_service = _get_template_service()
            version_file_path = Path(config_obj.version_filename)
            template_service.generate_version_file(
                config_obj.to_dict(), version_file_path
            )
            logger.info(f"Version file generated: {version_file_path}")
            dlp.complete_layer("version")

            # Compilation
            current_phase = "compile"
            dlp.update_layer("compile", 0, "Initializing compiler...")
            compiler_service, result = _get_pipeline_service().compile_project(
                config_obj,
                console=config_obj.console,
                compiler=config_obj.compiler,
            )
            logger.info("Compilation completed successfully")
            dlp.complete_layer("compile")

            # ZIP archive (runtime check for zip_needed from compilation result)
            zip_needed = result.zip_needed and config_obj.zip_needed
            if should_zip:
                if zip_needed:
                    current_phase = "zip"
                    zip_path = str(config_obj.zip_file_path)

                    def _zip_progress(filename: str, progress: int) -> None:
                        """Update progress display during ZIP file creation.

                        Args:
                            filename: The name of the file being compressed.
                            progress: The current progress percentage (0-100).
                        """
                        dlp.update_layer("zip", progress, Path(filename).name)

                    compiler_service._zip_artifact(
                        output_path=zip_path,
                        progress_callback=_zip_progress,
                    )
                    logger.info(f"ZIP archive created: {zip_path}")
                    dlp.complete_layer("zip")
                else:
                    # Stage was added but not needed at runtime
                    dlp.update_layer("zip", 0, "Skipped (not needed)")
                    dlp.complete_layer("zip")

            # Upload
            if should_upload:
                current_phase = "upload"
                source_file = (
                    str(config_obj.zip_file_path)
                    if zip_needed
                    else str(config_obj.output_folder)
                )
                structure = upload_structure or config_obj.upload_structure
                destination = upload_destination or (
                    config_obj.server_url
                    if structure == "server"
                    else config_obj.repo_path
                )
                dlp.update_layer("upload", 0, f"Connecting to {destination}...")
                UploaderService.upload(
                    source_path=Path(source_file),
                    upload_type=structure,  # type: ignore[arg-type]
                    destination=destination,
                )
                logger.info(f"Upload completed ({structure})")
                dlp.complete_layer("upload")

        except (
            ConfigurationError,
            CompilationError,
            TemplateError,
            VersionError,
            UploadError,
            ZipError,
        ) as e:
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

    printer.success("Build pipeline finished")


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
                "compiler": "auto",
                "zip_needed": True,
                "repo_needed": False,
            },
            "upload": {
                "structure": "disk",
                "repo_path": "releases",
                "server_url": "",
            },
            "advanced": {"optimize": True, "strip": False, "debug": False},
        }

        # File generation with progress tracking
        stages: list[StageConfig] = [
            {
                "name": "config",
                "type": "spinner",
                "description": f"Generating {format_type} configuration",
            },
            {"name": "setup", "type": "spinner", "description": "Generating setup.py"},
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
                current_phase = "setup"
                dlp.update_layer("setup", 0, "Processing template...")
                template_service.generate_setup_file(config_dict, output_dir=output_dir)
                logger.info(f"setup.py generated: {output_dir / 'setup.py'}")
                dlp.complete_layer("setup")

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
