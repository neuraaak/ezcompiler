# ///////////////////////////////////////////////////////////////
# CLI - Command-line interface for EzCompiler
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
CLI - Command-line interface for EzCompiler.

This module provides a Click-based CLI for generating configuration files,
setup.py files, version files, and initializing new EzCompiler projects.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path

# Third-party imports
import click
import yaml

# Local imports
from .generators import SetupGenerator, VersionGenerator
from .templates import TemplateManager

# ///////////////////////////////////////////////////////////////
# CLI COMMANDS AND GROUPS
# ///////////////////////////////////////////////////////////////


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version="2.1.4", prog_name="EzCompiler")
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
    type=click.Choice(["auto", "Cx_Freeze", "PyInstaller"]),
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

    # Generate configuration files using TemplateManager
    template_manager = TemplateManager()

    # Generate YAML configuration
    yaml_content = template_manager.process_config_template("yaml", config_dict)
    yaml_path = output_path / "ezcompiler.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")
    click.echo(f"✅ YAML configuration file generated: {yaml_path}")

    # Generate JSON configuration
    json_content = template_manager.process_config_template("json", config_dict)
    json_path = output_path / "ezcompiler.json"
    json_path.write_text(json_content, encoding="utf-8")
    click.echo(f"✅ JSON configuration file generated: {json_path}")


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

    # Generate setup.py using SetupGenerator
    setup_generator = SetupGenerator()
    setup_file_path = setup_generator.generate_from_config(config_dict, output_path)
    click.echo(f"✅ setup.py file generated: {setup_file_path}")


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

    # Generate version file using VersionGenerator
    version_generator = VersionGenerator()
    version_file_path = output_path / version_filename
    version_generator.generate(config_dict, version_file_path)
    click.echo(f"✅ Version file generated: {version_file_path}")


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

    # Initialize template manager
    template_manager = TemplateManager()

    # Write file to disk
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    target = output_path / filename

    if mockup:
        # Generate with mockup values
        template_manager.generate_template_with_mockup(type, format, target)
        click.echo(f"✅ Template with mockup values generated: {target}")
    else:
        # Generate with placeholders
        template_manager.generate_raw_template(type, format, target)
        click.echo(f"✅ Raw template generated: {target}")


@main.command()
def init() -> None:
    """
    Initialize a new EzCompiler project.

    Creates base configuration files (ezcompiler.yaml, ezcompiler.json),
    setup.py, and version_info.txt for a new project with user-provided
    project information.
    """
    click.echo("🚀 Initializing a new EzCompiler project...")

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
        "upload": {"structure": "disk", "repo_path": "releases", "server_url": ""},
        "advanced": {"optimize": True, "strip": False, "debug": False},
    }

    # Generate all files using generators
    template_manager = TemplateManager()
    setup_generator = SetupGenerator()
    version_generator = VersionGenerator()

    # Generate YAML configuration
    yaml_content = template_manager.process_config_template("yaml", config_dict)
    Path("ezcompiler.yaml").write_text(yaml_content, encoding="utf-8")
    click.echo("✅ ezcompiler.yaml generated")

    # Generate JSON configuration
    json_content = template_manager.process_config_template("json", config_dict)
    Path("ezcompiler.json").write_text(json_content, encoding="utf-8")
    click.echo("✅ ezcompiler.json generated")

    # Generate setup.py
    setup_generator.generate_from_config(config_dict)
    click.echo("✅ setup.py generated")

    # Generate version file
    version_generator.generate_from_config(config_dict)
    click.echo("✅ version_info.txt generated")

    click.echo("\n🎉 EzCompiler project initialized successfully!")
    click.echo("📝 You can now customize the generated configuration files as needed.")


if __name__ == "__main__":
    main()
