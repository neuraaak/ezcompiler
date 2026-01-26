# Configuration Guide – EzCompiler

## Overview

This guide provides comprehensive instructions for configuring **EzCompiler** projects using configuration files. EzCompiler supports both YAML and JSON configuration formats.

## Table of Contents

- [Configuration Guide – EzCompiler](#configuration-guide--ezcompiler)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Configuration Files](#configuration-files)
    - [File Formats](#file-formats)
    - [File Locations](#file-locations)
    - [Priority Order](#priority-order)
  - [Configuration Schema](#configuration-schema)
    - [Required Fields](#required-fields)
    - [Optional Fields](#optional-fields)
    - [Compilation Fields](#compilation-fields)
    - [Upload Fields](#upload-fields)
  - [YAML Configuration](#yaml-configuration)
    - [Complete Example](#complete-example)
    - [Minimal Example](#minimal-example)
  - [JSON Configuration](#json-configuration)
    - [Complete Example](#complete-example-1)
    - [Minimal Example](#minimal-example-1)
  - [Field Reference](#field-reference)
    - [version](#version)
    - [project\_name](#project_name)
    - [main\_file](#main_file)
    - [output\_folder](#output_folder)
    - [include\_files](#include_files)
    - [packages](#packages)
    - [excludes](#excludes)
    - [compiler](#compiler)
    - [upload\_structure](#upload_structure)
  - [Configuration Examples](#configuration-examples)
    - [Console Application](#console-application)
    - [GUI Application](#gui-application)
    - [Multi-Package Application](#multi-package-application)
    - [Server Upload Configuration](#server-upload-configuration)
  - [Validation](#validation)
    - [Required Validation](#required-validation)
    - [Version Format](#version-format)
    - [Path Validation](#path-validation)
  - [Environment Variables](#environment-variables)
  - [Best Practices](#best-practices)
    - [1. Use Version Control](#1-use-version-control)
    - [2. Use YAML for Readability](#2-use-yaml-for-readability)
    - [3. Use Consistent Excludes](#3-use-consistent-excludes)
    - [4. Organize Include Files](#4-organize-include-files)
    - [5. Use Semantic Versioning](#5-use-semantic-versioning)
  - [Troubleshooting](#troubleshooting)
    - [Configuration Not Found](#configuration-not-found)
    - [Invalid YAML Syntax](#invalid-yaml-syntax)
    - [Invalid JSON Syntax](#invalid-json-syntax)
    - [Missing Required Field](#missing-required-field)
    - [Invalid Version Format](#invalid-version-format)
  - [Additional Resources](#additional-resources)

---

## Configuration Files

### File Formats

EzCompiler supports two configuration formats:

| Format | File              | Description                        |
| ------ | ----------------- | ---------------------------------- |
| YAML   | `ezcompiler.yaml` | Human-readable, supports comments  |
| JSON   | `ezcompiler.json` | Machine-readable, widely supported |

### File Locations

Configuration files can be placed in:

1. **Project root** (recommended): `./ezcompiler.yaml` or `./ezcompiler.json`
2. **Custom location**: Specified via `--config` option
3. **Config directory**: `./config/ezcompiler.yaml`

### Priority Order

When using the CLI or API, configuration is resolved in this order:

1. **Command-line arguments** – Highest priority
2. **Configuration file** – Medium priority
3. **Default values** – Lowest priority

---

## Configuration Schema

### Required Fields

These fields must be provided for compilation:

| Field           | Type     | Description                         |
| --------------- | -------- | ----------------------------------- |
| `version`       | `string` | Project version (e.g., "1.0.0")     |
| `project_name`  | `string` | Project name                        |
| `main_file`     | `string` | Main Python file to compile         |
| `output_folder` | `string` | Output directory for compiled files |

### Optional Fields

| Field                 | Type             | Default              | Description         |
| --------------------- | ---------------- | -------------------- | ------------------- |
| `project_description` | `string`         | `""`                 | Project description |
| `company_name`        | `string`         | `""`                 | Company name        |
| `author`              | `string`         | `""`                 | Author name         |
| `icon`                | `string \| null` | `null`               | Path to icon file   |
| `version_file`        | `string`         | `"version_info.txt"` | Version file name   |

### Compilation Fields

| Field           | Type      | Default                           | Description                   |
| --------------- | --------- | --------------------------------- | ----------------------------- |
| `include_files` | `object`  | `{}`                              | Files and folders to include  |
| `packages`      | `list`    | `[]`                              | Packages to include           |
| `includes`      | `list`    | `[]`                              | Modules to include explicitly |
| `excludes`      | `list`    | `["debugpy", "test", "unittest"]` | Modules to exclude            |
| `console`       | `boolean` | `true`                            | Show console window           |
| `compiler`      | `string`  | `"auto"`                          | Compiler choice               |
| `optimize`      | `boolean` | `true`                            | Enable optimization           |
| `strip`         | `boolean` | `false`                           | Strip symbols                 |
| `debug`         | `boolean` | `false`                           | Debug mode                    |

### Upload Fields

| Field              | Type             | Default      | Description           |
| ------------------ | ---------------- | ------------ | --------------------- |
| `zip_needed`       | `boolean`        | `true`       | Create ZIP archive    |
| `repo_needed`      | `boolean`        | `false`      | Upload to repository  |
| `upload_structure` | `string`         | `"disk"`     | Upload structure      |
| `repo_path`        | `string`         | `"releases"` | Repository path       |
| `server_url`       | `string \| null` | `null`       | Server URL for upload |

---

## YAML Configuration

### Complete Example

```yaml
# ///////////////////////////////////////////////////////////////
# EzCompiler Configuration
# Project: MyAwesomeApp
# ///////////////////////////////////////////////////////////////

# ---------------------------------------------------------------
# PROJECT INFORMATION
# ---------------------------------------------------------------

version: "2.0.0"
project_name: "MyAwesomeApp"
project_description: "A feature-rich Python application"
company_name: "TechCorp Inc."
author: "Jane Developer"

# ---------------------------------------------------------------
# FILE CONFIGURATION
# ---------------------------------------------------------------

main_file: "src/main.py"
icon: "resources/app.ico"
version_file: "version_info.txt"
output_folder: "build/dist"

# Files and folders to include in the build
include_files:
  files:
    - "config.yaml"
    - "README.md"
    - "LICENSE"
    - "data/defaults.json"
  folders:
    - "assets"
    - "templates"
    - "locale"

# ---------------------------------------------------------------
# COMPILATION SETTINGS
# ---------------------------------------------------------------

# Packages to include in the build
packages:
  - "requests"
  - "pandas"
  - "numpy"
  - "matplotlib"
  - "PyYAML"

# Modules to include explicitly (rarely needed)
includes:
  - "encodings"
  - "json"

# Modules to exclude from the build
excludes:
  - "debugpy"
  - "test"
  - "unittest"
  - "pytest"
  - "mypy"
  - "black"
  - "ruff"

# Compilation options
console: false          # GUI application (no console window)
compiler: "Cx_Freeze"   # Use Cx_Freeze compiler
optimize: true          # Enable optimization
strip: true             # Strip debug symbols
debug: false            # Disable debug mode

# ---------------------------------------------------------------
# DISTRIBUTION SETTINGS
# ---------------------------------------------------------------

zip_needed: true              # Create ZIP archive after compilation
repo_needed: true             # Upload to repository
upload_structure: "disk"      # Upload to local disk
repo_path: "./releases/v2.0.0"  # Repository path
server_url: null              # No server upload
```

### Minimal Example

```yaml
# Minimal EzCompiler configuration
version: "1.0.0"
project_name: "SimpleApp"
main_file: "main.py"
output_folder: "dist"
```

---

## JSON Configuration

### Complete Example

```json
{
  "$schema": "https://ezcompiler.dev/schema/config.json",
  
  "version": "2.0.0",
  "project_name": "MyAwesomeApp",
  "project_description": "A feature-rich Python application",
  "company_name": "TechCorp Inc.",
  "author": "Jane Developer",
  
  "main_file": "src/main.py",
  "icon": "resources/app.ico",
  "version_file": "version_info.txt",
  "output_folder": "build/dist",
  
  "include_files": {
    "files": [
      "config.yaml",
      "README.md",
      "LICENSE",
      "data/defaults.json"
    ],
    "folders": [
      "assets",
      "templates",
      "locale"
    ]
  },
  
  "packages": [
    "requests",
    "pandas",
    "numpy",
    "matplotlib",
    "PyYAML"
  ],
  
  "includes": [
    "encodings",
    "json"
  ],
  
  "excludes": [
    "debugpy",
    "test",
    "unittest",
    "pytest",
    "mypy",
    "black",
    "ruff"
  ],
  
  "console": false,
  "compiler": "Cx_Freeze",
  "optimize": true,
  "strip": true,
  "debug": false,
  
  "zip_needed": true,
  "repo_needed": true,
  "upload_structure": "disk",
  "repo_path": "./releases/v2.0.0",
  "server_url": null
}
```

### Minimal Example

```json
{
  "version": "1.0.0",
  "project_name": "SimpleApp",
  "main_file": "main.py",
  "output_folder": "dist"
}
```

---

## Field Reference

### version

Project version string following semantic versioning.

**Format:** `MAJOR.MINOR.PATCH` (e.g., "1.0.0", "2.1.3")

```yaml
version: "1.0.0"
```

**Validation:**
- Must contain at least 2 parts separated by dots
- Each part must be a valid integer
- Examples: "1.0", "1.0.0", "1.0.0.0"

### project_name

Project name used in executable and file names.

```yaml
project_name: "MyProject"
```

**Best Practices:**
- Use alphanumeric characters and underscores
- Avoid spaces (use underscores instead)
- Keep it concise but descriptive

### main_file

Path to the main Python file to compile.

```yaml
main_file: "main.py"
# Or with subdirectory
main_file: "src/main.py"
```

**Notes:**
- Relative to project root
- Must exist at compilation time
- Must be a valid Python file

### output_folder

Directory where compiled files will be placed.

```yaml
output_folder: "dist"
# Or with subdirectory
output_folder: "build/output"
```

**Notes:**
- Created automatically if doesn't exist
- Relative to project root
- Cleaned before compilation (optional)

### include_files

Files and folders to include in the compiled application.

```yaml
include_files:
  files:
    - "config.yaml"
    - "data/defaults.json"
    - "README.md"
  folders:
    - "assets"
    - "templates"
    - "locale"
```

**Structure:**
- `files`: List of individual files to include
- `folders`: List of directories to include (recursive)

### packages

Python packages to include in the build.

```yaml
packages:
  - "requests"
  - "pandas"
  - "numpy"
```

**Notes:**
- Package names as they appear in import statements
- Dependencies are usually detected automatically
- Add packages that aren't detected automatically

### excludes

Modules to exclude from the build.

```yaml
excludes:
  - "debugpy"
  - "test"
  - "unittest"
  - "pytest"
```

**Common Excludes:**
- Development tools: `debugpy`, `pytest`, `mypy`, `black`, `ruff`
- Test modules: `test`, `unittest`, `tests`
- Large unused modules: `tkinter` (if not used)

### compiler

Compiler to use for building the executable.

```yaml
compiler: "auto"  # Automatic selection
# Or
compiler: "PyInstaller"
# Or
compiler: "Cx_Freeze"
```

**Options:**
- `auto`: Automatic selection based on requirements
- `PyInstaller`: Single-file executables, simpler distribution
- `Cx_Freeze`: Directory-based, better performance for large apps

### upload_structure

Structure type for uploading compiled files.

```yaml
upload_structure: "disk"  # Local disk
# Or
upload_structure: "server"  # HTTP/HTTPS server
```

**Options:**
- `disk`: Copy to local filesystem
- `server`: Upload via HTTP POST/PUT

---

## Configuration Examples

### Console Application

```yaml
version: "1.0.0"
project_name: "ConsoleApp"
main_file: "cli.py"
output_folder: "dist"

console: true  # Show console window
compiler: "PyInstaller"

packages:
  - "click"
  - "rich"

excludes:
  - "debugpy"
  - "test"
```

### GUI Application

```yaml
version: "1.0.0"
project_name: "DesktopApp"
main_file: "gui/main.py"
output_folder: "dist"

icon: "resources/app.ico"
console: false  # Hide console window
compiler: "Cx_Freeze"

include_files:
  folders:
    - "resources"
    - "themes"

packages:
  - "PyQt5"
  - "requests"

excludes:
  - "debugpy"
  - "test"
  - "tkinter"  # Not using tkinter
```

### Multi-Package Application

```yaml
version: "2.0.0"
project_name: "DataProcessor"
main_file: "src/main.py"
output_folder: "build/dist"

packages:
  - "pandas"
  - "numpy"
  - "scipy"
  - "matplotlib"
  - "seaborn"
  - "scikit-learn"
  - "openpyxl"
  - "xlrd"

includes:
  - "encodings"
  - "json"
  - "csv"

excludes:
  - "debugpy"
  - "test"
  - "pytest"
  - "ipython"
  - "jupyter"

optimize: true
strip: true
```

### Server Upload Configuration

```yaml
version: "1.0.0"
project_name: "WebService"
main_file: "service.py"
output_folder: "dist"

zip_needed: true
repo_needed: true
upload_structure: "server"
server_url: "https://releases.example.com/api/upload"

# Additional upload config can be passed via API
# Example: authentication headers, timeouts, etc.
```

---

## Validation

### Required Validation

The following fields are validated as required:

```python
required_fields = ["version", "project_name", "main_file", "output_folder"]
```

If any required field is missing, a `ConfigurationError` is raised.

### Version Format

Version must follow semantic versioning:

```python
# Valid versions
"1.0"
"1.0.0"
"1.0.0.0"
"2.1.3"

# Invalid versions
"v1.0.0"  # No prefix allowed
"1"       # At least 2 parts required
"1.a.0"   # Non-numeric parts
```

### Path Validation

Paths are validated for:

- Valid characters (no invalid filesystem characters)
- Reasonable length (not too long)
- Existence (for input files, at compilation time)

---

## Environment Variables

EzCompiler supports configuration via environment variables:

| Variable              | Description                        |
| --------------------- | ---------------------------------- |
| `EZCOMPILER_CONFIG`   | Path to default configuration file |
| `EZCOMPILER_OUTPUT`   | Default output directory           |
| `EZCOMPILER_COMPILER` | Default compiler choice            |

**Example:**

```bash
export EZCOMPILER_CONFIG="./config/ezcompiler.yaml"
export EZCOMPILER_OUTPUT="./build"
export EZCOMPILER_COMPILER="PyInstaller"
```

---

## Best Practices

### 1. Use Version Control

Keep configuration files in version control:

```gitignore
# .gitignore - Don't ignore config files
!ezcompiler.yaml
!ezcompiler.json
```

### 2. Use YAML for Readability

YAML supports comments and is more human-readable:

```yaml
# This is a comment explaining the configuration
version: "1.0.0"
project_name: "MyApp"
```

### 3. Use Consistent Excludes

Always exclude development and test packages:

```yaml
excludes:
  - "debugpy"
  - "test"
  - "unittest"
  - "pytest"
  - "mypy"
  - "black"
  - "ruff"
  - "flake8"
```

### 4. Organize Include Files

Keep include files organized:

```yaml
include_files:
  files:
    # Configuration files
    - "config.yaml"
    - "settings.json"
    # Documentation
    - "README.md"
    - "LICENSE"
  folders:
    # Resources
    - "assets"
    - "templates"
    - "locale"
```

### 5. Use Semantic Versioning

Follow semantic versioning for releases:

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

---

## Troubleshooting

### Configuration Not Found

```bash
Error: Configuration file not found
```

**Solution:** Check the file path and ensure the file exists:

```bash
ezcompiler generate setup --config ./ezcompiler.yaml
```

### Invalid YAML Syntax

```bash
Error: YAML parsing error
```

**Solution:** Validate YAML syntax online or use a YAML linter:

```bash
python -c "import yaml; yaml.safe_load(open('ezcompiler.yaml'))"
```

### Invalid JSON Syntax

```bash
Error: JSON parsing error
```

**Solution:** Validate JSON syntax:

```bash
python -c "import json; json.load(open('ezcompiler.json'))"
```

### Missing Required Field

```bash
Error: Required field 'project_name' is missing
```

**Solution:** Add the required field to your configuration:

```yaml
project_name: "MyProject"
```

### Invalid Version Format

```bash
Error: Invalid version format
```

**Solution:** Use semantic versioning format:

```yaml
version: "1.0.0"  # Correct
# NOT:
# version: "v1.0.0"  # Wrong - no prefix
# version: "1"       # Wrong - need at least 2 parts
```

---

## Additional Resources

- **[CLI Documentation](CLI_DOCUMENTATION.md)** – Command-line interface reference
- **[API Documentation](../api/API_DOCUMENTATION.md)** – Complete API reference
- **[Examples](../examples/EXAMPLES.md)** – Usage examples

---

**EzCompiler Configuration Guide** – Your reference for configuring EzCompiler projects.
