# CLI Reference

Command-line interface documentation for **EzCompiler**.

## Overview

EzCompiler provides a comprehensive command-line interface for interactive project initialization, configuration file generation, and automation tasks.

## Installation

The CLI is automatically available after installing EzCompiler:

```bash
pip install ezcompiler
```

Verify installation:

```bash
ezcompiler --version
```

---

## Commands

### Initialize Project

Initialize a new EzCompiler project with interactive prompts:

```bash
ezcompiler init
```

This command will guide you through:

- Project name
- Main script file
- Output directory
- Compiler selection
- Package dependencies
- Files and folders to include

---

### Generate Files

EzCompiler can generate various configuration and setup files.

#### Generate Configuration

Create a configuration file with basic settings:

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py"
```

**Options:**

- `--project-name TEXT` – Project name (required)
- `--main-file TEXT` – Main Python file (required)
- `--version TEXT` – Project version (default: "1.0.0")
- `--output PATH` – Output file path (default: "ezcompiler.yaml")
- `--format [yaml|json]` – Output format (default: yaml)

**Example:**

```bash
ezcompiler generate config \
    --project-name "MyApp" \
    --main-file "main.py" \
    --version "2.0.0" \
    --output "config/ezcompiler.yaml"
```

#### Generate Setup File

Generate a `setup.py` file from a configuration:

```bash
ezcompiler generate setup --config ezcompiler.yaml
```

**Options:**

- `--config PATH` – Path to configuration file (required)
- `--output PATH` – Output file path (default: "setup.py")

**Example:**

```bash
ezcompiler generate setup --config ezcompiler.yaml --output dist/setup.py
```

#### Generate Version File

Generate a version information file for Windows executables:

```bash
ezcompiler generate version --config ezcompiler.yaml
```

**Options:**

- `--config PATH` – Path to configuration file (required)
- `--output PATH` – Output file path (default: "version.txt")

**Example:**

```bash
ezcompiler generate version --config ezcompiler.yaml --output version_info.txt
```

#### Generate Template

Generate template files with optional mockup data:

```bash
ezcompiler generate template --type config --mockup
```

**Options:**

- `--type [config|setup|version]` – Template type (required)
- `--mockup` – Include mockup/sample data
- `--output PATH` – Output file path

**Examples:**

```bash
# Generate config template with sample data
ezcompiler generate template --type config --mockup

# Generate setup template
ezcompiler generate template --type setup --output templates/setup_template.py

# Generate version template
ezcompiler generate template --type version
```

---

## Configuration File Format

### YAML Format (Recommended)

```yaml
version: "1.0.0"
project_name: "MyProject"
main_file: "main.py"
output_folder: "dist"
compiler: "PyInstaller"

# Dependencies
packages:
  - "requests"
  - "pandas"
  - "numpy"

# Exclude development packages
excludes:
  - "debugpy"
  - "pytest"
  - "mypy"

# Include files and folders
include_files:
  files:
    - "config.yaml"
    - "data.json"
  folders:
    - "assets"
    - "templates"

# Compiler-specific options
compiler_options:
  log-level: "DEBUG"
  onefile: true
```

### JSON Format

```json
{
  "version": "1.0.0",
  "project_name": "MyProject",
  "main_file": "main.py",
  "output_folder": "dist",
  "compiler": "PyInstaller",
  "packages": ["requests", "pandas"],
  "excludes": ["debugpy", "pytest"],
  "include_files": {
    "files": ["config.yaml"],
    "folders": ["assets"]
  }
}
```

---

## Global Options

These options are available for all commands:

- `--help` – Show help message and exit
- `--version` – Show version and exit
- `--verbose` – Enable verbose output
- `--quiet` – Suppress non-error output

**Example:**

```bash
ezcompiler --verbose generate config --project-name "MyApp" --main-file "main.py"
```

---

## Environment Variables

EzCompiler supports the following environment variables:

- `EZCOMPILER_CONFIG` – Default configuration file path
- `EZCOMPILER_LOG_LEVEL` – Logging level (DEBUG, INFO, WARNING, ERROR)
- `EZCOMPILER_OUTPUT_DIR` – Default output directory

**Example:**

```bash
export EZCOMPILER_CONFIG="config/ezcompiler.yaml"
export EZCOMPILER_LOG_LEVEL="DEBUG"
ezcompiler generate setup
```

---

## Usage Examples

### Basic Workflow

```bash
# 1. Initialize project
ezcompiler init

# 2. Generate setup file
ezcompiler generate setup --config ezcompiler.yaml

# 3. Generate version file
ezcompiler generate version --config ezcompiler.yaml
```

### Custom Configuration

```bash
# Generate config with specific settings
ezcompiler generate config \
    --project-name "AdvancedApp" \
    --main-file "src/main.py" \
    --version "2.1.0" \
    --format json \
    --output "configs/app.json"
```

### Template Generation

```bash
# Generate all template types
ezcompiler generate template --type config --mockup --output templates/config.yaml
ezcompiler generate template --type setup --mockup --output templates/setup.py
ezcompiler generate template --type version --mockup --output templates/version.txt
```

---

## Configuration Reference

### Required Fields

- `version` – Project version (semantic versioning recommended)
- `project_name` – Project name
- `main_file` – Main Python script file
- `output_folder` – Output directory for compiled project

### Optional Fields

- `compiler` – Compiler to use ("Cx_Freeze", "PyInstaller", "Nuitka")
- `packages` – List of packages to include
- `excludes` – List of packages to exclude
- `include_files` – Dictionary with `files` and `folders` lists
- `compiler_options` – Dictionary of compiler-specific options

### Compiler Options

#### Cx_Freeze

```yaml
compiler: "Cx_Freeze"
compiler_options:
  zip_include_packages: ["*"]
  zip_exclude_packages: ["test", "tkinter"]
  include_msvcr: true
  optimize: 2
```

#### PyInstaller

```yaml
compiler: "PyInstaller"
compiler_options:
  log-level: "DEBUG"
  collect-all: "numpy"
  onefile: true
  windowed: false
```

#### Nuitka

```yaml
compiler: "Nuitka"
compiler_options:
  show-progress: true
  enable-plugin: "numpy"
  onefile: true
  windows-disable-console: false
```

---

## Troubleshooting

### Command Not Found

If `ezcompiler` command is not found:

```bash
# Ensure installation path is in PATH
python -m pip install --user ezcompiler

# Or use python module syntax
python -m ezcompiler init
```

### Configuration Errors

If configuration is invalid:

```bash
# Use verbose mode for detailed error messages
ezcompiler --verbose generate setup --config ezcompiler.yaml
```

### Permission Errors

If you encounter permission errors:

```bash
# Run with appropriate permissions
sudo ezcompiler generate setup --config ezcompiler.yaml

# Or change output directory
ezcompiler generate setup --config ezcompiler.yaml --output ~/setup.py
```

---

## Advanced Usage

### Scripting and Automation

```bash
#!/bin/bash
# build.sh - Automated build script

# Generate configuration
ezcompiler generate config \
    --project-name "$PROJECT_NAME" \
    --main-file "$MAIN_FILE" \
    --version "$VERSION" \
    --output "ezcompiler.yaml"

# Generate setup and version files
ezcompiler generate setup --config ezcompiler.yaml
ezcompiler generate version --config ezcompiler.yaml

echo "Build configuration complete!"
```

### CI/CD Integration

#### GitHub Actions

```yaml
name: Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"
      - name: Install EzCompiler
        run: pip install ezcompiler
      - name: Generate config
        run: |
          ezcompiler generate config \
            --project-name "${{ github.event.repository.name }}" \
            --main-file "main.py" \
            --version "${{ github.ref_name }}"
      - name: Generate setup
        run: ezcompiler generate setup --config ezcompiler.yaml
```

---

## See Also

- [Getting Started](../getting-started.md) – Installation and basic usage
- [API Reference](../api/index.md) – Python API documentation
- [Examples](../examples/index.md) – Code examples
- [Configuration Guide](../guides/configuration.md) – Detailed configuration guide

---

## Need Help?

- **Documentation**: [Full Documentation](../index.md)
- **Examples**: [Code Examples](../examples/index.md)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
