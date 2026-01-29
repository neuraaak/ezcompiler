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
from pathlib import Path
from typing import Any

# Third-party imports
import click
import yaml

# Local imports
from ..services import CompilerService, ConfigService, TemplateService, UploaderService
from ..shared.exceptions import (
    CompilationError,
    ConfigurationError,
    TemplateError,
    UploadError,
    VersionError,
)

# ///////////////////////////////////////////////////////////////
# LAZY ACCESSORS (avoid circular import with interfaces/__init__.py)
# ///////////////////////////////////////////////////////////////


def _get_printer():
    """Get the global EzPrinter instance (lazy import)."""
    from . import get_printer

    return get_printer()


def _get_logger():
    """Get the global EzLogger instance (lazy import)."""
    from . import get_logger

    return get_logger()


# ///////////////////////////////////////////////////////////////
# CLI COMMANDS AND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version="2.0.0", prog_name="EzCompiler")
def main() -> None:
    """
    EzCompiler - CLI for Python project compilation and distribution.

    Generates configuration files, setup.py, and version files from templates
    with support for multiple formats (YAML, JSON) and template types.
    """


@main.group()
def generate() -> None:
    """Generate files from templates."""


@generate.command()
@click.option(
    "--version", "-v", default="1.0.0", help="Project version (default: 1.0.0)"
)
@click.option("--project-name", "-n", required=True, help="Project name")
@click.option("--project-description", "-d", default="", help="Project description")
@click.option("--company-name", "-c", default="", help="Company name")
@click.option("--author", "-a", default="", help="Project author")
@click.option(
    "--main-file", "-m", default="main.py", help="Main file (default: main.py)"
)
@click.option("--icon", "-i", default="", help="Path to icon file")
@click.option(
    "--version-file",
    "-vf",
    default="version_info.txt",
    help="Version file name (default: version_info.txt)",
)
@click.option(
    "--output-folder",
    "-o",
    default="dist",
    help="Output folder for compilation (default: dist)",
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
    default=["debugpy", "test", "unittest"],
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
    default="auto",
    help="Compiler to use (default: auto)",
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
    default="disk",
    help="Upload structure (default: disk)",
)
@click.option(
    "--repo-path",
    "-rp",
    default="releases",
    help="Repository path (default: releases)",
)
@click.option("--server-url", "-su", default="", help="Server URL for upload")
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
    version: str,
    project_name: str,
    project_description: str,
    company_name: str,
    author: str,
    main_file: str,
    icon: str,
    version_filename: str,
    output_folder: str,
    include_files: tuple[str, ...],
    include_folders: tuple[str, ...],
    packages: tuple[str, ...],
    includes: tuple[str, ...],
    excludes: tuple[str, ...],
    console: bool,
    compiler: str,
    zip_needed: bool,
    repo_needed: bool,
    upload_structure: str,
    repo_path: str,
    server_url: str,
    optimize: bool,
    strip: bool,
    debug: bool,
    output: str,
) -> None:
    """
    Generate YAML and JSON configuration files.

    Creates ezcompiler.yaml and ezcompiler.json from provided options
    or defaults. Accepts configuration via multiple CLI options.
    """
    printer = _get_printer()
    logger = _get_logger()

    try:
        # Build configuration dictionary
        config_dict = {
            "version": version,
            "project_name": project_name,
            "project_description": project_description,
            "company_name": company_name,
            "author": author,
            "main_file": main_file,
            "icon": icon,
            "version_filename": version_filename,
            "output_folder": output_folder,
            "include_files": {
                "files": list(include_files),
                "folders": list(include_folders),
            },
            "packages": list(packages),
            "includes": list(includes),
            "excludes": list(excludes),
            "compilation": {
                "console": console,
                "compiler": compiler,
                "zip_needed": zip_needed,
                "repo_needed": repo_needed,
            },
            "upload": {
                "structure": upload_structure,
                "repo_path": repo_path,
                "server_url": server_url,
            },
            "advanced": {"optimize": optimize, "strip": strip, "debug": debug},
        }

        # Ensure output directory exists
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate configuration files using TemplateService
        template_service = TemplateService()

        # Generate YAML configuration
        yaml_content = template_service.process_config_template("yaml", config_dict)
        yaml_path = output_path / "ezcompiler.yaml"
        yaml_path.write_text(yaml_content, encoding="utf-8")
        printer.success(f"YAML configuration file generated: {yaml_path}")
        logger.info(f"YAML configuration file generated: {yaml_path}")

        # Generate JSON configuration
        json_content = template_service.process_config_template("json", config_dict)
        json_path = output_path / "ezcompiler.json"
        json_path.write_text(json_content, encoding="utf-8")
        printer.success(f"JSON configuration file generated: {json_path}")
        logger.info(f"JSON configuration file generated: {json_path}")

    except TemplateError as e:
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
    "--version", "-v", default="1.0.0", help="Project version (default: 1.0.0)"
)
@click.option("--project-name", "-n", help="Project name")
@click.option("--project-description", "-d", default="", help="Project description")
@click.option("--company-name", "-cn", default="", help="Company name")
@click.option("--author", "-a", default="", help="Project author")
@click.option(
    "--main-file", "-m", default="main.py", help="Main file (default: main.py)"
)
@click.option("--icon", "-i", default="", help="Path to icon file")
@click.option(
    "--version-file",
    "-vf",
    default="version_info.txt",
    help="Version file name (default: version_info.txt)",
)
@click.option(
    "--output-folder",
    "-o",
    default="dist",
    help="Output folder for compilation (default: dist)",
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
    default=["debugpy", "test", "unittest"],
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
    version: str,
    project_name: str,
    project_description: str,
    company_name: str,
    author: str,
    main_file: str,
    icon: str,
    version_filename: str,
    output_folder: str,
    include_files: tuple[str, ...],
    include_folders: tuple[str, ...],
    packages: tuple[str, ...],
    includes: tuple[str, ...],
    excludes: tuple[str, ...],
    output: str,
) -> None:
    """
    Generate a setup.py file.

    Creates setup.py from configuration file or CLI options.
    Configuration file takes precedence over CLI options.
    """
    printer = _get_printer()
    logger = _get_logger()

    try:
        # Load configuration from file if provided
        if config:
            config_path = Path(config)
            if config_path.suffix.lower() == ".yaml":
                with open(config_path, encoding="utf-8") as f:
                    config_dict = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, encoding="utf-8") as f:
                    config_dict = json.load(f)
            else:
                raise click.BadParameter("Configuration file must be YAML or JSON")
        else:
            # Ensure project_name is provided when config file is missing
            if not project_name:
                raise click.BadParameter(
                    "--project-name is required when --config is not provided"
                )

            # Build configuration from CLI parameters
            config_dict = {
                "version": version,
                "project_name": project_name,
                "project_description": project_description,
                "company_name": company_name,
                "author": author,
                "main_file": main_file,
                "icon": icon,
                "version_filename": version_filename,
                "output_folder": output_folder,
                "include_files": {
                    "files": list(include_files),
                    "folders": list(include_folders),
                },
                "packages": list(packages),
                "includes": list(includes),
                "excludes": list(excludes),
            }

        # Ensure output directory exists
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate setup.py using TemplateService
        template_service = TemplateService()
        setup_file_path = template_service.generate_setup_file(
            config_dict, output_dir=output_path
        )
        printer.success(f"setup.py file generated: {setup_file_path}")
        logger.info(f"setup.py file generated: {setup_file_path}")

    except TemplateError as e:
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
    "--version", "-v", default="1.0.0", help="Project version (default: 1.0.0)"
)
@click.option("--project-name", "-n", help="Project name")
@click.option("--project-description", "-d", default="", help="Project description")
@click.option("--company-name", "-cn", default="", help="Company name")
@click.option(
    "--version-file",
    "-vf",
    default="version_info.txt",
    help="Version file name (default: version_info.txt)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=".",
    help="Output directory for generated files (default: .)",
)
def version(
    config: str | None,
    version: str,
    project_name: str | None,
    project_description: str,
    company_name: str,
    version_filename: str,
    output: str,
) -> None:
    """
    Generate a version information file.

    Creates version_info.txt from configuration file or CLI options.
    Configuration file takes precedence over CLI options.
    """
    printer = _get_printer()
    logger = _get_logger()

    try:
        # Load configuration from file if provided
        if config:
            config_path = Path(config)
            if config_path.suffix.lower() == ".yaml":
                with open(config_path, encoding="utf-8") as f:
                    config_dict = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, encoding="utf-8") as f:
                    config_dict = json.load(f)
            else:
                raise click.BadParameter("Configuration file must be YAML or JSON")
        else:
            # Ensure project_name is provided when config file is missing
            if not project_name:
                raise click.BadParameter(
                    "--project-name is required when --config is not provided"
                )

            # Build configuration from CLI parameters
            config_dict = {
                "version": version,
                "project_name": project_name,
                "project_description": project_description,
                "company_name": company_name,
                "version_filename": version_filename,
            }

        # Ensure output directory exists
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate version file using TemplateService
        template_service = TemplateService()
        version_file_path = output_path / version_filename
        template_service.generate_version_file(config_dict, version_file_path)
        printer.success(f"Version file generated: {version_file_path}")
        logger.info(f"Version file generated: {version_file_path}")

    except (TemplateError, VersionError) as e:
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
        template_service = TemplateService()

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
def compile_project(
    config: str | None,
    pyproject: str | None,
    compiler: str | None,
    console: bool | None,
    output_folder: str | None,
    debug: bool,
    no_zip: bool,
    no_upload: bool,
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
    """
    printer = _get_printer()
    logger = _get_logger()

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

        printer.info(
            f"Compiling {config_obj.project_name} v{config_obj.version} "
            f"with {config_obj.compiler}..."
        )
        logger.info(
            f"Compiling {config_obj.project_name} v{config_obj.version} "
            f"with {config_obj.compiler}"
        )

        # Compile
        compiler_service = CompilerService(config_obj)
        result = compiler_service.compile(
            console=config_obj.console,
            compiler=config_obj.compiler,  # type: ignore[arg-type]
        )

        printer.success("Compilation completed successfully")
        logger.info("Compilation completed successfully")

        # ZIP if needed
        zip_needed = result.zip_needed and config_obj.zip_needed
        if not no_zip and zip_needed:
            from ..utils.zip_utils import ZipUtils

            zip_path = f"{config_obj.output_folder}.zip"
            ZipUtils.create_zip_archive(
                source_path=str(config_obj.output_folder),
                output_path=zip_path,
            )
            printer.success(f"ZIP archive created: {zip_path}")
            logger.info(f"ZIP archive created: {zip_path}")

        # Upload if needed
        if not no_upload and config_obj.repo_needed:
            source_file = (
                f"{config_obj.output_folder}.zip"
                if zip_needed
                else str(config_obj.output_folder)
            )
            destination = (
                config_obj.server_url
                if config_obj.upload_structure == "server"
                else config_obj.repo_path
            )

            UploaderService.upload(
                source_path=Path(source_file),
                upload_type=config_obj.upload_structure,  # type: ignore[arg-type]
                destination=destination,
            )
            printer.success(f"Upload completed ({config_obj.upload_structure})")
            logger.info(f"Upload completed ({config_obj.upload_structure})")

        printer.success("Build pipeline finished")

    except (ConfigurationError, CompilationError, UploadError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


@main.command()
def init() -> None:
    """
    Initialize a new EzCompiler project.

    Creates base configuration files (ezcompiler.yaml, ezcompiler.json),
    setup.py, and version_info.txt for a new project with user-provided
    project information.
    """
    printer = _get_printer()
    logger = _get_logger()

    try:
        printer.info("Initializing a new EzCompiler project...")

        # Collect basic project information via prompts
        project_name = click.prompt("Project name")
        version = click.prompt("Version", default="1.0.0")
        project_description = click.prompt("Project description", default="")
        company_name = click.prompt("Company name", default="")
        author = click.prompt("Author", default="")
        main_file = click.prompt("Main file", default="main.py")

        # Build configuration dictionary with sensible defaults
        config_dict = {
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

        # Generate all files using TemplateService
        template_service = TemplateService()

        # Generate YAML configuration
        yaml_content = template_service.process_config_template("yaml", config_dict)
        Path("ezcompiler.yaml").write_text(yaml_content, encoding="utf-8")
        printer.success("ezcompiler.yaml generated")
        logger.info("ezcompiler.yaml generated")

        # Generate JSON configuration
        json_content = template_service.process_config_template("json", config_dict)
        Path("ezcompiler.json").write_text(json_content, encoding="utf-8")
        printer.success("ezcompiler.json generated")
        logger.info("ezcompiler.json generated")

        # Generate setup.py
        template_service.generate_setup_file(config_dict)
        printer.success("setup.py generated")
        logger.info("setup.py generated")

        # Generate version file
        template_service.generate_version_file(config_dict)
        printer.success("version_info.txt generated")
        logger.info("version_info.txt generated")

        printer.success("EzCompiler project initialized successfully")
        printer.tip(
            "You can now customize the generated configuration files as needed."
        )

    except (TemplateError, VersionError) as e:
        printer.error(str(e))
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
