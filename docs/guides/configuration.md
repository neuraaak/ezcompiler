# Configuration Guide

Comprehensive guide to configuring **EzCompiler** projects.

## Overview

This guide covers all configuration options for EzCompiler, including YAML and JSON formats, compiler-specific settings, and best practices for managing project configurations.

---

## Configuration Formats

EzCompiler supports two configuration formats: **YAML** (recommended) and **JSON**.

### YAML Configuration (Recommended)

YAML provides a human-readable format with support for comments:

```yaml
# Project metadata
version: "1.0.0"
project_name: "MyApplication"
project_description: "A sample application"
company_name: "My Company"
author: "John Doe"

# Build configuration
main_file: "main.py"
output_folder: "dist"
compiler: "PyInstaller"

# Dependencies
packages:
  - "requests"
  - "pandas"
  - "numpy"

# Exclusions
excludes:
  - "debugpy"
  - "pytest"
  - "mypy"

# Files to include
include_files:
  files:
    - "config.yaml"
    - "data.json"
    - "LICENSE"
  folders:
    - "assets"
    - "templates"
    - "locales"

# Compiler-specific options
compiler_options:
  log-level: "INFO"
  onefile: true
```

### JSON Configuration

JSON format for programmatic configuration:

```json
{
  "version": "1.0.0",
  "project_name": "MyApplication",
  "main_file": "main.py",
  "output_folder": "dist",
  "compiler": "PyInstaller",
  "packages": ["requests", "pandas"],
  "excludes": ["debugpy", "pytest"],
  "include_files": {
    "files": ["config.yaml"],
    "folders": ["assets"]
  },
  "compiler_options": {
    "onefile": true
  }
}
```

---

## Required Fields

These fields are required in every configuration:

| Field           | Type   | Description                           | Example     |
| --------------- | ------ | ------------------------------------- | ----------- |
| `version`       | string | Project version (semantic versioning) | `"1.0.0"`   |
| `project_name`  | string | Project name                          | `"MyApp"`   |
| `main_file`     | string | Main Python script file               | `"main.py"` |
| `output_folder` | string | Output directory for compiled project | `"dist"`    |

---

## Optional Fields

### Project Metadata

| Field                 | Type   | Description                  | Default |
| --------------------- | ------ | ---------------------------- | ------- |
| `project_description` | string | Project description          | `""`    |
| `company_name`        | string | Company or organization name | `""`    |
| `author`              | string | Author name                  | `""`    |

### Compilation Settings

| Field              | Type   | Description                  | Default                        |
| ------------------ | ------ | ---------------------------- | ------------------------------ |
| `compiler`         | string | Compiler to use              | `"Cx_Freeze"`                  |
| `packages`         | list   | List of packages to include  | `[]`                           |
| `excludes`         | list   | List of packages to exclude  | `[]`                           |
| `include_files`    | dict   | Files and folders to include | `{"files": [], "folders": []}` |
| `compiler_options` | dict   | Compiler-specific options    | `{}`                           |

---

## Compiler Selection

EzCompiler supports three compilation backends:

### Cx_Freeze

**Best for:** Directory-based builds, large applications

```yaml
compiler: "Cx_Freeze"
compiler_options:
  zip_include_packages: ["*"]
  zip_exclude_packages: ["test", "tkinter"]
  include_msvcr: true
  optimize: 2
```

**Common Options:**

- `zip_include_packages`: Packages to include in ZIP
- `zip_exclude_packages`: Packages to exclude from ZIP
- `include_msvcr`: Include Microsoft Visual C runtime
- `optimize`: Optimization level (0, 1, 2)

### PyInstaller

**Best for:** Single-file executables, simple distribution

```yaml
compiler: "PyInstaller"
compiler_options:
  onefile: true
  windowed: false
  icon: "icon.ico"
  log-level: "DEBUG"
```

**Common Options:**

- `onefile`: Create single executable file
- `windowed`: Hide console window (GUI apps)
- `icon`: Application icon file
- `log-level`: Logging level
- `collect-all`: Collect all files from package

### Nuitka

**Best for:** Optimized compilation, maximum performance

```yaml
compiler: "Nuitka"
compiler_options:
  onefile: true
  show-progress: true
  enable-plugin: "pyside6"
  windows-disable-console: false
```

**Common Options:**

- `onefile`: Create single executable
- `show-progress`: Show compilation progress
- `enable-plugin`: Enable specific plugins
- `windows-disable-console`: Disable console window

---

## Package Management

### Including Packages

Specify required packages:

```yaml
packages:
  - "requests"
  - "pandas"
  - "numpy"
  - "sqlalchemy"
  - "pydantic"
```

### Excluding Packages

Exclude unnecessary development packages:

```yaml
excludes:
  - "debugpy"
  - "pytest"
  - "mypy"
  - "ruff"
  - "ipython"
```

---

## Including Files and Folders

### Include Specific Files

```yaml
include_files:
  files:
    - "config.yaml"
    - "data.json"
    - "LICENSE"
    - "README.md"
```

### Include Entire Folders

```yaml
include_files:
  folders:
    - "assets"
    - "templates"
    - "locales"
    - "data"
```

### Mixed Approach

```yaml
include_files:
  files:
    - "config.yaml"
    - "LICENSE"
  folders:
    - "assets"
    - "templates"
```

---

## Complete Configuration Examples

### Simple Console Application

```yaml
version: "1.0.0"
project_name: "SimpleApp"
main_file: "main.py"
output_folder: "dist"
compiler: "PyInstaller"

packages:
  - "requests"

compiler_options:
  onefile: true
  windowed: false
```

### GUI Application

```yaml
version: "2.0.0"
project_name: "GUIApp"
project_description: "Desktop GUI Application"
company_name: "My Company"
author: "John Doe"
main_file: "app.py"
output_folder: "build/dist"
compiler: "Cx_Freeze"

packages:
  - "PySide6"
  - "requests"

excludes:
  - "debugpy"
  - "pytest"

include_files:
  files:
    - "icon.ico"
    - "config.yaml"
  folders:
    - "assets"
    - "ui"

compiler_options:
  zip_include_packages: ["*"]
  include_msvcr: true
  optimize: 2
```

### Web Application

```yaml
version: "1.5.0"
project_name: "WebApp"
main_file: "server.py"
output_folder: "dist"
compiler: "Nuitka"

packages:
  - "fastapi"
  - "uvicorn"
  - "sqlalchemy"
  - "pydantic"

excludes:
  - "debugpy"
  - "pytest"

include_files:
  files:
    - "config.yaml"
    - "alembic.ini"
  folders:
    - "static"
    - "templates"
    - "migrations"

compiler_options:
  onefile: false
  show-progress: true
  enable-plugin: "numpy"
```

---

## Loading Configuration

### From YAML File

```python
from ezcompiler import EzCompiler, CompilerConfig
import yaml

# Load from YAML
with open("ezcompiler.yaml") as f:
    config_dict = yaml.safe_load(f)
    config = CompilerConfig.from_dict(config_dict)

ezcompiler = EzCompiler(config)
```

### From JSON File

```python
from ezcompiler import EzCompiler, CompilerConfig
import json

# Load from JSON
with open("ezcompiler.json") as f:
    config_dict = json.load(f)
    config = CompilerConfig.from_dict(config_dict)

ezcompiler = EzCompiler(config)
```

### From Python Dictionary

```python
from ezcompiler import EzCompiler, CompilerConfig

# Create from dictionary
config_dict = {
    "version": "1.0.0",
    "project_name": "MyApp",
    "main_file": "main.py",
    "output_folder": "dist",
    "packages": ["requests"],
}

config = CompilerConfig.from_dict(config_dict)
ezcompiler = EzCompiler(config)
```

---

## Best Practices

### 1. Use Version Control

Store configuration files in version control:

```bash
git add ezcompiler.yaml
git commit -m "Add build configuration"
```

### 2. Environment-Specific Configurations

Create separate configurations for different environments:

```text
config/
├── ezcompiler-dev.yaml
├── ezcompiler-staging.yaml
└── ezcompiler-prod.yaml
```

### 3. Template Variables

Use environment variables for sensitive data:

```yaml
version: "${VERSION}"
project_name: "${PROJECT_NAME}"
```

### 4. Validation

Always validate configuration before building:

```python
from ezcompiler import EzCompiler, CompilerConfig
from ezcompiler.shared.exceptions import ConfigurationError

try:
    config = CompilerConfig.from_dict(config_dict)
    ezcompiler = EzCompiler(config)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    exit(1)
```

### 5. Documentation

Document your configuration choices:

```yaml
# ezcompiler.yaml

# Project metadata
version: "1.0.0" # Semantic versioning
project_name: "MyApp"

# Compiler: Using PyInstaller for single-file distribution
compiler: "PyInstaller"

# Include only production dependencies
packages:
  - "requests" # HTTP library
  - "pandas" # Data analysis

# Exclude development tools to reduce size
excludes:
  - "debugpy"
  - "pytest"
```

---

## Troubleshooting

### Configuration Validation Errors

If you encounter validation errors:

```python
from ezcompiler.utils.validators import schema_validators

# Validate configuration schema
is_valid = schema_validators.validate_dict_schema(
    config_dict,
    required_keys=["version", "project_name", "main_file", "output_folder"]
)
```

### Missing Required Fields

Ensure all required fields are present:

```yaml
version: "1.0.0" # Required
project_name: "MyApp" # Required
main_file: "main.py" # Required
output_folder: "dist" # Required
```

### Invalid Compiler Options

Check compiler-specific documentation for valid options.

---

## See Also

- [Getting Started](../getting-started.md) - Installation and basic usage
- [API Reference](../api/index.md) - Complete API documentation
- [Examples](../examples/index.md) - Configuration examples
- [CLI Reference](../cli/index.md) - Command-line configuration

---

## Need Help?

- **Documentation**: [Full Documentation](../index.md)
- **Examples**: [Code Examples](../examples/index.md)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
