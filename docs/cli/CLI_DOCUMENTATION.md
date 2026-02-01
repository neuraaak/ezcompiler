# Complete CLI Documentation – EzCompiler

## Overview

This documentation presents all the commands available in the **EzCompiler CLI**, organized by functionality. The CLI provides a complete interface for project initialization, file generation, and configuration management.

## Table of Contents

- [Complete CLI Documentation – EzCompiler](#complete-cli-documentation--ezcompiler)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [🚀 Installation](#-installation)
  - [📋 Command Reference](#-command-reference)
    - [Main Command](#main-command)
    - [init Command](#init-command)
    - [generate Command Group](#generate-command-group)
      - [generate config](#generate-config)
      - [generate setup](#generate-setup)
      - [generate version](#generate-version)
      - [generate template](#generate-template)
  - [⚙️ Options Reference](#️-options-reference)
    - [Project Options](#project-options)
    - [Compilation Options](#compilation-options)
    - [Upload Options](#upload-options)
    - [Output Options](#output-options)
  - [🎯 Usage Examples](#-usage-examples)
    - [Basic Usage](#basic-usage)
    - [Advanced Configuration](#advanced-configuration)
    - [Template Generation](#template-generation)
    - [Server Upload Configuration](#server-upload-configuration)
  - [📁 Generated Files](#-generated-files)
    - [Configuration Files](#configuration-files)
    - [Setup Files](#setup-files)
    - [Version Files](#version-files)
  - [🔧 Troubleshooting](#-troubleshooting)
    - [Common Issues](#common-issues)
    - [Getting Help](#getting-help)
    - [Verbose Output](#verbose-output)
  - [Additional Resources](#additional-resources)

---

## 🚀 Installation

Install EzCompiler with pip:

```bash
pip install ezcompiler
```

Verify the installation:

```bash
ezcompiler --version
```

---

## 📋 Command Reference

### Main Command

```bash
ezcompiler [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**

- `--help`: Show help message and exit
- `--version`: Show version and exit

**Available Commands:**

- `init`: Initialize a new project interactively
- `generate`: Generate configuration and setup files

### init Command

Initialize a new EzCompiler project with interactive prompts.

```bash
ezcompiler init
```

**Behavior:**

This command starts an interactive wizard that prompts for:

1. Project name
2. Version
3. Description
4. Company name
5. Author
6. Main file

**Generated Files:**

- `ezcompiler.yaml` – YAML configuration file
- `ezcompiler.json` – JSON configuration file
- `setup.py` – Cx_Freeze setup file
- `version_info.txt` – Windows version information

**Example:**

```bash
$ ezcompiler init
? Project name: MyAwesomeProject
? Version [1.0.0]: 1.0.0
? Description: An awesome Python application
? Company name: MyCompany
? Author: John Doe
? Main file [main.py]: src/main.py

✅ Project initialized successfully!
   - Created ezcompiler.yaml
   - Created ezcompiler.json
   - Created setup.py
   - Created version_info.txt
```

---

### generate Command Group

Generate various configuration and setup files.

```bash
ezcompiler generate [OPTIONS] COMMAND [ARGS]...
```

**Available Subcommands:**

- `config`: Generate configuration files (YAML and JSON)
- `setup`: Generate setup.py file
- `version`: Generate version information file
- `template`: Generate raw template files

---

#### generate config

Generate configuration files from command-line parameters.

```bash
ezcompiler generate config [OPTIONS]
```

**Required Options:**

- `--project-name, -n TEXT`: Project name (required)

**Project Options:**

- `--version, -v TEXT`: Project version [default: 1.0.0]
- `--project-description, -d TEXT`: Project description
- `--company-name, -c TEXT`: Company name
- `--author, -a TEXT`: Author name
- `--main-file, -m TEXT`: Main Python file [default: main.py]
- `--icon, -i PATH`: Path to icon file
- `--version-file, -vf TEXT`: Version file name [default: version_info.txt]
- `--output-folder, -o PATH`: Output folder for compilation [default: dist]

**Compilation Options:**

- `--include-files, -f TEXT`: Files to include (multiple allowed)
- `--include-folders, -fd TEXT`: Folders to include (multiple allowed)
- `--packages, -p TEXT`: Packages to include (multiple allowed)
- `--includes, -inc TEXT`: Modules to include explicitly (multiple allowed)
- `--excludes, -exc TEXT`: Modules to exclude (multiple allowed) [default: debugpy, test, unittest]
- `--console / --no-console`: Show console window [default: console]
- `--compiler, -comp TEXT`: Compiler to use (auto/Cx_Freeze/PyInstaller/Nuitka) [default: auto]
- `--optimize / --no-optimize`: Enable optimization [default: optimize]
- `--strip / --no-strip`: Strip symbols [default: no-strip]
- `--debug / --no-debug`: Debug mode [default: no-debug]

**Upload Options:**

- `--zip-needed / --no-zip-needed`: Create ZIP archive [default: zip-needed]
- `--repo-needed / --no-repo-needed`: Upload to repository [default: no-repo-needed]
- `--upload-structure, -us TEXT`: Upload structure (disk/server) [default: disk]
- `--repo-path, -rp PATH`: Repository path [default: releases]
- `--server-url, -su TEXT`: Server URL for upload

**Output Options:**

- `--output, -out PATH`: Output directory for generated files [default: .]

**Example:**

```bash
ezcompiler generate config \
  --project-name "MyProject" \
  --version "1.0.0" \
  --project-description "My awesome project" \
  --company-name "MyCompany" \
  --author "John Doe" \
  --main-file "main.py" \
  --output-folder "dist" \
  --include-files "config.yaml" \
  --include-folders "assets" \
  --packages "requests" "pandas" \
  --excludes "debugpy" "test" \
  --compiler "PyInstaller" \
  --console \
  --zip-needed
```

---

#### generate setup

Generate a `setup.py` file for compilation.

```bash
ezcompiler generate setup [OPTIONS]
```

**Configuration Source (choose one):**

- `--config, -c PATH`: Path to configuration file (YAML or JSON)
- Or use individual options (same as `generate config`)

**Options (when not using --config):**

- `--version, -v TEXT`: Project version [default: 1.0.0]
- `--project-name, -n TEXT`: Project name (required if no config file)
- `--project-description, -d TEXT`: Project description
- `--company-name, -cn TEXT`: Company name
- `--author, -a TEXT`: Author name
- `--main-file, -m TEXT`: Main Python file [default: main.py]
- `--icon, -i PATH`: Path to icon file
- `--version-file, -vf TEXT`: Version file name [default: version_info.txt]
- `--output-folder, -o PATH`: Output folder [default: dist]
- `--include-files, -f TEXT`: Files to include (multiple allowed)
- `--include-folders, -fd TEXT`: Folders to include (multiple allowed)
- `--packages, -p TEXT`: Packages to include (multiple allowed)
- `--includes, -inc TEXT`: Modules to include (multiple allowed)
- `--excludes, -exc TEXT`: Modules to exclude (multiple allowed)
- `--output, -out PATH`: Output directory [default: .]

**Examples:**

Using configuration file:

```bash
ezcompiler generate setup --config ezcompiler.yaml
```

Using parameters:

```bash
ezcompiler generate setup \
  --project-name "MyProject" \
  --version "1.0.0" \
  --main-file "main.py" \
  --packages "requests" "pandas"
```

---

#### generate version

Generate a Windows version information file.

```bash
ezcompiler generate version [OPTIONS]
```

**Configuration Source (choose one):**

- `--config, -c PATH`: Path to configuration file (YAML or JSON)
- Or use individual options

**Options (when not using --config):**

- `--version, -v TEXT`: Project version [default: 1.0.0]
- `--project-name, -n TEXT`: Project name (required if no config file)
- `--project-description, -d TEXT`: Project description
- `--company-name, -cn TEXT`: Company name
- `--version-file, -vf TEXT`: Version file name [default: version_info.txt]
- `--output, -o PATH`: Output directory [default: .]

**Examples:**

Using configuration file:

```bash
ezcompiler generate version --config ezcompiler.yaml
```

Using parameters:

```bash
ezcompiler generate version \
  --project-name "MyProject" \
  --version "1.0.0" \
  --company-name "MyCompany" \
  --project-description "My awesome project"
```

---

#### generate template

Generate raw template files without variable substitution.

```bash
ezcompiler generate template [OPTIONS]
```

**Options:**

- `--type, -t TEXT`: Template type (required)
  - `config`: Configuration template (YAML/JSON)
  - `setup`: Setup.py template
  - `version`: Version file template
- `--format, -f TEXT`: Template format
  - For `config`: `yaml` (default) or `json`
  - For `setup`: `py` (default)
  - For `version`: `txt` (default)
- `--output, -o PATH`: Output directory [default: .]
- `--filename, -N TEXT`: Custom filename (optional)
- `--mockup, -m`: Generate with example values instead of placeholders

**Examples:**

Generate YAML config template:

```bash
ezcompiler generate template --type config --format yaml
```

Generate setup.py template with mockup values:

```bash
ezcompiler generate template --type setup --mockup
```

Generate version template with custom filename:

```bash
ezcompiler generate template --type version --filename my_version.txt
```

---

## ⚙️ Options Reference

### Project Options

| Option                  | Short | Description                   | Default            |
| ----------------------- | ----- | ----------------------------- | ------------------ |
| `--version`             | `-v`  | Project version               | `1.0.0`            |
| `--project-name`        | `-n`  | Project name                  | Required           |
| `--project-description` | `-d`  | Project description           | `""`               |
| `--company-name`        | `-c`  | Company name                  | `""`               |
| `--author`              | `-a`  | Author name                   | `""`               |
| `--main-file`           | `-m`  | Main Python file              | `main.py`          |
| `--icon`                | `-i`  | Path to icon file             | `None`             |
| `--version-file`        | `-vf` | Version file name             | `version_info.txt` |
| `--output-folder`       | `-o`  | Output folder for compilation | `dist`             |

### Compilation Options

| Option              | Short  | Description                                   | Default                     |
| ------------------- | ------ | --------------------------------------------- | --------------------------- |
| `--include-files`   | `-f`   | Files to include                              | `[]`                        |
| `--include-folders` | `-fd`  | Folders to include                            | `[]`                        |
| `--packages`        | `-p`   | Packages to include                           | `[]`                        |
| `--includes`        | `-inc` | Modules to include                            | `[]`                        |
| `--excludes`        | `-exc` | Modules to exclude                            | `[debugpy, test, unittest]` |
| `--console`         |        | Show console window                           | `True`                      |
| `--compiler`        | `-comp`| Compiler (auto/Cx_Freeze/PyInstaller/Nuitka)  | `auto`                      |
| `--optimize`        | `-opt` | Enable optimization                           | `True`                      |
| `--strip`           | `-s`   | Strip symbols                                 | `False`                     |
| `--debug`           | `-dbg` | Debug mode                                    | `False`                     |

### Upload Options

| Option               | Short | Description                    | Default    |
| -------------------- | ----- | ------------------------------ | ---------- |
| `--zip-needed`       | `-z`  | Create ZIP archive             | `True`     |
| `--repo-needed`      | `-r`  | Upload to repository           | `False`    |
| `--upload-structure` | `-us` | Upload structure (disk/server) | `disk`     |
| `--repo-path`        | `-rp` | Repository path                | `releases` |
| `--server-url`       | `-su` | Server URL for upload          | `None`     |

### Output Options

| Option     | Short  | Description                          | Default |
| ---------- | ------ | ------------------------------------ | ------- |
| `--output` | `-out` | Output directory for generated files | `.`     |
| `--config` | `-c`   | Path to configuration file           | `None`  |

---

## 🎯 Usage Examples

### Basic Usage

**Initialize a new project:**

```bash
ezcompiler init
```

**Generate configuration:**

```bash
ezcompiler generate config \
  --project-name "HelloWorld" \
  --version "1.0.0" \
  --main-file "hello.py"
```

**Generate setup.py from config:**

```bash
ezcompiler generate setup --config ezcompiler.yaml
```

### Advanced Configuration

**Full configuration with all options:**

```bash
ezcompiler generate config \
  --project-name "AdvancedApp" \
  --version "2.0.0" \
  --project-description "A feature-rich application" \
  --company-name "TechCorp Inc." \
  --author "Jane Developer" \
  --main-file "src/main.py" \
  --icon "resources/app.ico" \
  --output-folder "build/dist" \
  --include-files "config.yaml" "README.md" "LICENSE" \
  --include-folders "assets" "data" "templates" \
  --packages "requests" "pandas" "numpy" "matplotlib" \
  --includes "encodings" "json" \
  --excludes "debugpy" "test" "unittest" "pytest" "mypy" \
  --no-console \
  --compiler "Cx_Freeze" \
  --optimize \
  --strip \
  --zip-needed \
  --repo-needed \
  --upload-structure "disk" \
  --repo-path "./releases/v2.0.0"
```

### Template Generation

**Generate all templates:**

```bash
# Configuration templates
ezcompiler generate template --type config --format yaml
ezcompiler generate template --type config --format json

# Setup template
ezcompiler generate template --type setup

# Version template
ezcompiler generate template --type version
```

**Generate templates with mockup values:**

```bash
ezcompiler generate template --type config --mockup
ezcompiler generate template --type setup --mockup
```

### Server Upload Configuration

**Configure for server upload:**

```bash
ezcompiler generate config \
  --project-name "WebApp" \
  --version "1.0.0" \
  --main-file "app.py" \
  --zip-needed \
  --repo-needed \
  --upload-structure "server" \
  --server-url "https://api.example.com/releases"
```

---

## 📁 Generated Files

### Configuration Files

**ezcompiler.yaml:**

```yaml
# EzCompiler Configuration
version: "1.0.0"
project_name: "MyProject"
project_description: "Project description"
company_name: "MyCompany"
author: "Author Name"
main_file: "main.py"
icon: null
version_file: "version_info.txt"
output_folder: "dist"

include_files:
  files:
    - "config.yaml"
  folders:
    - "assets"

packages:
  - "requests"

includes: []
excludes:
  - "debugpy"
  - "test"
  - "unittest"

console: true
compiler: "auto"
optimize: true
strip: false
debug: false

zip_needed: true
repo_needed: false
upload_structure: "disk"
repo_path: "releases"
server_url: null
```

**ezcompiler.json:**

```json
{
  "version": "1.0.0",
  "project_name": "MyProject",
  "project_description": "Project description",
  "company_name": "MyCompany",
  "author": "Author Name",
  "main_file": "main.py",
  "icon": null,
  "version_file": "version_info.txt",
  "output_folder": "dist",
  "include_files": {
    "files": ["config.yaml"],
    "folders": ["assets"]
  },
  "packages": ["requests"],
  "includes": [],
  "excludes": ["debugpy", "test", "unittest"],
  "console": true,
  "compiler": "auto",
  "optimize": true,
  "strip": false,
  "debug": false,
  "zip_needed": true,
  "repo_needed": false,
  "upload_structure": "disk",
  "repo_path": "releases",
  "server_url": null
}
```

### Setup Files

**setup.py:**

```python
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["requests"],
    "includes": [],
    "excludes": ["debugpy", "test", "unittest"],
    "include_files": [
        "config.yaml",
        "assets/",
    ],
}

setup(
    name="MyProject",
    version="1.0.0",
    description="Project description",
    author="Author Name",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=None,  # Console application
            target_name="MyProject.exe",
            icon=None,
        )
    ],
)
```

### Version Files

**version_info.txt:**

```python
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904B0',
                    [
                        StringStruct(u'CompanyName', u'MyCompany'),
                        StringStruct(u'FileDescription', u'Project description'),
                        StringStruct(u'FileVersion', u'1.0.0'),
                        StringStruct(u'InternalName', u'MyProject'),
                        StringStruct(u'LegalCopyright', u'© MyCompany'),
                        StringStruct(u'OriginalFilename', u'MyProject.exe'),
                        StringStruct(u'ProductName', u'MyProject'),
                        StringStruct(u'ProductVersion', u'1.0.0'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "Project name is required"

```bash
# Make sure to provide --project-name
ezcompiler generate config --project-name "MyProject" ...
```

#### Issue: "Configuration file not found"

```bash
# Check the path to your configuration file
ezcompiler generate setup --config ./ezcompiler.yaml
```

#### Issue: "Invalid compiler name"

```bash
# Valid compiler names are: auto, Cx_Freeze, PyInstaller, Nuitka
ezcompiler generate config --compiler "PyInstaller" ...
```

#### Issue: "Invalid upload structure"

```bash
# Valid upload structures are: disk, server
ezcompiler generate config --upload-structure "disk" ...
```

### Getting Help

```bash
# General help
ezcompiler --help

# Command-specific help
ezcompiler init --help
ezcompiler generate --help
ezcompiler generate config --help
ezcompiler generate setup --help
ezcompiler generate version --help
ezcompiler generate template --help
```

### Verbose Output

For debugging, use the `--debug` flag when generating configuration:

```bash
ezcompiler generate config --project-name "Test" --debug
```

---

## Additional Resources

- **[API Documentation](../api/API_DOCUMENTATION.md)** – Complete API reference
- **[Configuration Guide](CONFIG_GUIDE.md)** – Configuration file guide
- **[Examples](../examples/EXAMPLES.md)** – Usage examples
- **[Test Documentation](../tests/TEST_DOCUMENTATION.md)** – Test suite documentation

---

**EzCompiler CLI** – Command-line interface for Python project compilation and distribution.
