# Usage Examples – EzCompiler

## Overview

This documentation presents comprehensive usage examples for the **EzCompiler** library, covering both the Python API and CLI interfaces. Each example includes complete code and explanations.

## Table of Contents

- [Usage Examples – EzCompiler](#usage-examples--ezcompiler)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [🚀 Quick Start](#-quick-start)
    - [Installation](#installation)
    - [First Compilation with run\_pipeline()](#first-compilation-with-run_pipeline)
    - [First Compilation (Individual Steps)](#first-compilation-individual-steps)
  - [📦 Basic Examples](#-basic-examples)
    - [Simple Console Application](#simple-console-application)
    - [GUI Application](#gui-application)
    - [Application with Data Files](#application-with-data-files)
  - [⚙️ Advanced Examples](#️-advanced-examples)
    - [Multi-Package Application](#multi-package-application)
    - [Custom Compiler Selection](#custom-compiler-selection)
    - [Configuration from Files](#configuration-from-files)
    - [Programmatic Configuration with run\_pipeline()](#programmatic-configuration-with-run_pipeline)
    - [Programmatic Configuration with Nuitka](#programmatic-configuration-with-nuitka)
  - [📤 Distribution Examples](#-distribution-examples)
    - [Local Disk Distribution](#local-disk-distribution)
    - [Server Upload](#server-upload)
    - [Complete Distribution Workflow](#complete-distribution-workflow)
  - [🔧 Template Examples](#-template-examples)
    - [Generate Configuration Templates](#generate-configuration-templates)
    - [Custom Template Processing](#custom-template-processing)
  - [🖥️ CLI Examples](#️-cli-examples)
    - [Interactive Project Initialization](#interactive-project-initialization)
    - [Generate Configuration via CLI](#generate-configuration-via-cli)
    - [Generate Setup via CLI](#generate-setup-via-cli)
    - [Generate Version via CLI](#generate-version-via-cli)
  - [🔌 Integration Examples](#-integration-examples)
    - [CI/CD Integration](#cicd-integration)
    - [Build Script Integration](#build-script-integration)
    - [Automated Release Workflow](#automated-release-workflow)
  - [🛠️ Utility Examples](#️-utility-examples)
    - [File Operations](#file-operations)
    - [Validation Operations](#validation-operations)
    - [ZIP Operations](#zip-operations)
  - [🎯 Best Practices Examples](#-best-practices-examples)
    - [Error Handling](#error-handling)
    - [Logging Integration](#logging-integration)
    - [Configuration Management](#configuration-management)
  - [Additional Resources](#additional-resources)

---

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install ezcompiler

# Or install with development dependencies
pip install ezcompiler[dev]

# Verify installation
ezcompiler --version
```

### First Compilation with run_pipeline()

```python
from ezcompiler import EzCompiler

# Create compiler instance
ezcompiler = EzCompiler()

# Initialize project with minimal configuration
ezcompiler.init_project(
    version="1.0.0",
    project_name="HelloWorld",
    main_file="hello.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Compile the project using run_pipeline() with DLP progress display
ezcompiler.run_pipeline(compiler="PyInstaller")
```

### First Compilation (Individual Steps)

```python
from ezcompiler import EzCompiler

ezcompiler = EzCompiler()
ezcompiler.init_project(
    version="1.0.0",
    project_name="HelloWorld",
    main_file="hello.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Compile the project (individual method call)
ezcompiler.compile_project(compiler="PyInstaller")
```

---

## 📦 Basic Examples

### Simple Console Application

**hello.py:**

```python
#!/usr/bin/env python
"""Simple Hello World application."""

def main():
    print("Hello, World!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
```

**build.py:**

```python
from ezcompiler import EzCompiler

def build():
    """Build the Hello World application."""
    ezcompiler = EzCompiler()

    ezcompiler.init_project(
        version="1.0.0",
        project_name="HelloWorld",
        main_file="hello.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
        company_name="My Company",
        project_description="A simple Hello World application",
    )

    # Run pipeline with DLP progress display
    ezcompiler.run_pipeline(console=True, compiler="PyInstaller")

if __name__ == "__main__":
    build()
```

### GUI Application

**gui_app.py:**

```python
#!/usr/bin/env python
"""Simple GUI application with tkinter."""
import tkinter as tk
from tkinter import messagebox

def main():
    root = tk.Tk()
    root.title("My GUI App")
    root.geometry("400x300")
    
    label = tk.Label(root, text="Welcome to My App!", font=("Arial", 16))
    label.pack(pady=50)
    
    def on_click():
        messagebox.showinfo("Hello", "Button clicked!")
    
    button = tk.Button(root, text="Click Me", command=on_click)
    button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()
```

**build_gui.py:**

```python
from ezcompiler import EzCompiler

def build():
    """Build the GUI application."""
    ezcompiler = EzCompiler()

    ezcompiler.init_project(
        version="1.0.0",
        project_name="MyGUIApp",
        main_file="gui_app.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
        company_name="My Company",
        project_description="A GUI application",
        icon="resources/app.ico",  # Optional icon
    )

    # Run pipeline with DLP progress display
    ezcompiler.run_pipeline(console=False, compiler="PyInstaller")

if __name__ == "__main__":
    build()
```

### Application with Data Files

**data_app.py:**

```python
#!/usr/bin/env python
"""Application with configuration and data files."""
import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    print(f"Application: {config['app_name']}")
    print(f"Version: {config['version']}")
    print(f"Settings: {config['settings']}")

if __name__ == "__main__":
    main()
```

**config.yaml:**

```yaml
app_name: DataApp
version: 1.0.0
settings:
  debug: false
  log_level: INFO
```

**build_with_data.py:**

```python
from ezcompiler import EzCompiler

def build():
    """Build application with data files."""
    ezcompiler = EzCompiler()

    ezcompiler.init_project(
        version="1.0.0",
        project_name="DataApp",
        main_file="data_app.py",
        include_files={
            "files": ["config.yaml"],
            "folders": ["data", "templates"],
        },
        output_folder="dist",
        packages=["PyYAML"],
    )

    # Run pipeline with DLP progress display (includes ZIP)
    ezcompiler.run_pipeline(compiler="Cx_Freeze")

if __name__ == "__main__":
    build()
```

---

## ⚙️ Advanced Examples

### Multi-Package Application

```python
from ezcompiler import EzCompiler

def build_data_science_app():
    """Build a data science application with many dependencies."""
    ezcompiler = EzCompiler(log_level="DEBUG")
    
    ezcompiler.init_project(
        version="2.0.0",
        project_name="DataScienceApp",
        main_file="src/main.py",
        include_files={
            "files": [
                "config.yaml",
                "models/trained_model.pkl",
                "data/schema.json",
            ],
            "folders": [
                "assets",
                "templates",
                "notebooks",
            ],
        },
        output_folder="build/dist",
        company_name="DataCorp",
        project_description="Advanced data science application",
        author="Data Team",
        
        # Large package list
        packages=[
            "pandas",
            "numpy",
            "scipy",
            "scikit-learn",
            "matplotlib",
            "seaborn",
            "plotly",
            "openpyxl",
            "xlrd",
            "requests",
            "aiohttp",
            "fastapi",
            "uvicorn",
        ],
        
        # Explicit includes for hidden imports
        includes=[
            "encodings",
            "json",
            "csv",
            "sklearn.utils._typedefs",
            "sklearn.neighbors._partition_nodes",
        ],
        
        # Exclude development tools
        excludes=[
            "debugpy",
            "test",
            "unittest",
            "pytest",
            "mypy",
            "black",
            "ruff",
            "flake8",
            "ipython",
            "jupyter",
            "notebook",
        ],
        
        # Compilation options
        optimize=True,
        strip=True,
        console=False,
    )
    
    # Run pipeline with DLP progress display
    ezcompiler.run_pipeline(compiler="Cx_Freeze")

if __name__ == "__main__":
    build_data_science_app()
```

### Custom Compiler Selection

```python
from ezcompiler import EzCompiler
import sys

def build_with_compiler_choice():
    """Build with compiler selection based on requirements."""
    ezcompiler = EzCompiler()

    ezcompiler.init_project(
        version="1.0.0",
        project_name="FlexibleApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )

    # Choose compiler based on command line argument
    if "-pyi" in sys.argv or "--pyinstaller" in sys.argv:
        compiler = "PyInstaller"
        print("Using PyInstaller (single file)")
    elif "-cxf" in sys.argv or "--cxfreeze" in sys.argv:
        compiler = "Cx_Freeze"
        print("Using Cx_Freeze (directory)")
    elif "-nui" in sys.argv or "--nuitka" in sys.argv:
        compiler = "Nuitka"
        print("Using Nuitka (best performance)")
    else:
        # Interactive selection
        compiler = None
        print("No compiler specified, will prompt for selection")

    # Use run_pipeline() for DLP progress display
    ezcompiler.run_pipeline(compiler=compiler)

if __name__ == "__main__":
    build_with_compiler_choice()
```

### Configuration from Files

```python
import yaml
import json
from pathlib import Path
from ezcompiler import EzCompiler, CompilerConfig

def build_from_yaml():
    """Build from YAML configuration file."""
    # Load YAML configuration
    with open("ezcompiler.yaml") as f:
        config_dict = yaml.safe_load(f)
    
    # Create CompilerConfig from dictionary
    config = CompilerConfig.from_dict(config_dict)
    
    # Create compiler and set config
    ezcompiler = EzCompiler()
    ezcompiler._config = config
    
    # Build
    ezcompiler.generate_version_file()
    ezcompiler.compile_project()
    
    if config.zip_needed:
        ezcompiler.zip_compiled_project()

def build_from_json():
    """Build from JSON configuration file."""
    # Load JSON configuration
    with open("ezcompiler.json") as f:
        config_dict = json.load(f)
    
    config = CompilerConfig.from_dict(config_dict)
    
    ezcompiler = EzCompiler()
    ezcompiler._config = config
    
    ezcompiler.compile_project()

if __name__ == "__main__":
    build_from_yaml()
```

### Programmatic Configuration with run_pipeline()

```python
from ezcompiler import EzCompiler, CompilerConfig
from pathlib import Path

def build_programmatic():
    """Build with programmatic configuration using run_pipeline()."""

    # Create configuration object directly
    config = CompilerConfig(
        version="1.5.0",
        project_name="ProgrammaticApp",
        main_file="app/main.py",
        output_folder="output/release",
        project_description="Built with programmatic configuration",
        company_name="TechCorp",
        author="Development Team",

        include_files={
            "files": ["config.yaml", "README.md"],
            "folders": ["resources", "locales"],
        },

        packages=["requests", "click", "rich"],
        excludes=["debugpy", "test", "pytest"],

        console=True,
        compiler="PyInstaller",
        optimize=True,

        zip_needed=True,
        repo_needed=True,
        upload_structure="disk",
        repo_path="./releases",
    )

    # Validate configuration
    config.validate()

    # Create compiler with config
    ezcompiler = EzCompiler()
    ezcompiler._config = config

    # Run full pipeline with DLP progress display
    ezcompiler.run_pipeline(
        upload_structure=config.upload_structure,
        upload_destination=config.repo_path,
    )

if __name__ == "__main__":
    build_programmatic()
```

### Programmatic Configuration with Nuitka

```python
from ezcompiler import EzCompiler, CompilerConfig

def build_with_nuitka():
    """Build with Nuitka for optimal performance."""

    config = CompilerConfig(
        version="2.0.0",
        project_name="HighPerformanceApp",
        main_file="src/main.py",
        output_folder="dist/nuitka",
        project_description="High-performance Nuitka-compiled application",
        company_name="TechCorp",
        author="Performance Team",

        include_files={
            "files": ["config.yaml", "README.md", "LICENSE"],
            "folders": ["assets", "data"],
        },

        packages=["numpy", "pandas", "requests"],
        excludes=["debugpy", "test", "pytest", "mypy", "black"],

        console=True,
        compiler="Nuitka",  # Use Nuitka for best performance
        optimize=True,
        strip=True,  # Strip debug symbols for smaller executables

        zip_needed=True,
        repo_needed=False,
    )

    config.validate()

    ezcompiler = EzCompiler(log_level="INFO")
    ezcompiler._config = config

    # Run pipeline with DLP progress
    ezcompiler.run_pipeline(
        console=True,
        compiler="Nuitka",
    )

if __name__ == "__main__":
    build_with_nuitka()
```

---

## 📤 Distribution Examples

### Local Disk Distribution

```python
from ezcompiler import EzCompiler
from pathlib import Path

def build_and_distribute():
    """Build and distribute to local disk."""
    ezcompiler = EzCompiler()

    ezcompiler.init_project(
        version="1.0.0",
        project_name="DistributableApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )

    # Run pipeline with upload to local releases
    release_path = Path("./releases/v1.0.0")
    ezcompiler.run_pipeline(
        compiler="Cx_Freeze",
        upload_structure="disk",
        upload_destination=str(release_path),
    )

    print(f"Distribution available at: {release_path}")

if __name__ == "__main__":
    build_and_distribute()
```

### Server Upload

```python
from ezcompiler import EzCompiler

def build_and_upload():
    """Build and upload to server."""
    ezcompiler = EzCompiler()

    ezcompiler.init_project(
        version="1.0.0",
        project_name="ServerApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )

    # Run pipeline with server upload
    ezcompiler.run_pipeline(
        compiler="PyInstaller",
        upload_structure="server",
        upload_destination="https://releases.example.com/api/upload",
        upload_config={
            "headers": {
                "Authorization": "Bearer your-api-token",
                "Content-Type": "application/octet-stream",
            },
            "timeout": 300,
            "retries": 3,
        }
    )

if __name__ == "__main__":
    build_and_upload()
```

### Complete Distribution Workflow

```python
from ezcompiler import EzCompiler
from pathlib import Path
import shutil
import datetime

def full_release_workflow():
    """Complete release workflow with versioning."""
    
    # Configuration
    version = "2.1.0"
    project_name = "ProductionApp"
    
    # Create timestamped release folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    release_folder = Path(f"./releases/{version}_{timestamp}")
    
    ezcompiler = EzCompiler(log_level="INFO")
    
    # Initialize project
    ezcompiler.init_project(
        version=version,
        project_name=project_name,
        main_file="src/main.py",
        include_files={
            "files": ["config.yaml", "README.md", "LICENSE"],
            "folders": ["resources", "data"],
        },
        output_folder="build/output",
        company_name="Production Corp",
        project_description="Production-ready application",
        author="Release Team",
        packages=["requests", "pandas", "PyYAML"],
        excludes=["debugpy", "test", "pytest", "mypy"],
        optimize=True,
        strip=True,
    )
    
    # Run full pipeline with DLP progress
    print("Building and distributing...")
    ezcompiler.run_pipeline(
        console=False,
        compiler="Cx_Freeze",
        upload_structure="disk",
        upload_destination=str(release_folder),
    )
    
    # Create release notes
    release_notes = release_folder / "RELEASE_NOTES.md"
    with open(release_notes, "w") as f:
        f.write(f"# Release {version}\n\n")
        f.write(f"**Date:** {datetime.datetime.now().isoformat()}\n\n")
        f.write("## Changes\n\n")
        f.write("- Initial release\n")
    
    print(f"\nRelease completed: {release_folder}")
    print(f"Release notes: {release_notes}")

if __name__ == "__main__":
    full_release_workflow()
```

---

## 🔧 Template Examples

### Generate Configuration Templates

```python
from ezcompiler.templates import TemplateManager, TemplateProcessor

def generate_templates():
    """Generate all configuration templates."""
    manager = TemplateManager()
    
    # List available templates
    templates = manager.list_templates()
    print(f"Available templates: {templates}")
    
    # Generate YAML config with custom variables
    yaml_content = manager.process_template("config.yaml", {
        "PROJECT_NAME": "MyNewProject",
        "VERSION": "1.0.0",
        "MAIN_FILE": "main.py",
        "OUTPUT_FOLDER": "dist",
        "COMPANY_NAME": "My Company",
        "AUTHOR": "Developer",
    })
    
    with open("generated_config.yaml", "w") as f:
        f.write(yaml_content)
    
    # Generate setup.py template
    setup_content = manager.process_template("setup.py", {
        "PROJECT_NAME": "MyNewProject",
        "VERSION": "1.0.0",
        "MAIN_FILE": "main.py",
        "PACKAGES": '["requests"]',
    })
    
    with open("generated_setup.py", "w") as f:
        f.write(setup_content)

if __name__ == "__main__":
    generate_templates()
```

### Custom Template Processing

```python
from ezcompiler.templates import TemplateProcessor

def custom_template_processing():
    """Custom template processing examples."""
    processor = TemplateProcessor()
    
    # Simple substitution
    template = "Project: #PROJECT_NAME# v#VERSION#"
    result = processor.substitute(template, {
        "PROJECT_NAME": "CustomApp",
        "VERSION": "2.0.0",
    })
    print(result)  # "Project: CustomApp v2.0.0"
    
    # Generate mockup content
    mockup = processor.generate_mockup("config")
    print("Mockup configuration:")
    print(mockup)
    
    # Validate template has required variables
    template = "Name: #NAME#, Version: #VERSION#"
    is_valid = processor.validate_template(template, ["NAME", "VERSION"])
    print(f"Template valid: {is_valid}")  # True
    
    # Missing variable
    is_valid = processor.validate_template(template, ["NAME", "VERSION", "AUTHOR"])
    print(f"Template valid with AUTHOR: {is_valid}")  # False

if __name__ == "__main__":
    custom_template_processing()
```

---

## 🖥️ CLI Examples

### Interactive Project Initialization

```bash
# Start interactive initialization
$ ezcompiler init

? Project name: MyAwesomeApp
? Version [1.0.0]: 1.0.0
? Description: An awesome Python application
? Company name: TechCorp
? Author: Jane Developer
? Main file [main.py]: src/main.py

✅ Project initialized successfully!
   - Created ezcompiler.yaml
   - Created ezcompiler.json
   - Created setup.py
   - Created version_info.txt
```

### Generate Configuration via CLI

```bash
# Basic configuration
ezcompiler generate config \
  --project-name "CLIApp" \
  --version "1.0.0" \
  --main-file "main.py"

# Full configuration
ezcompiler generate config \
  --project-name "FullCLIApp" \
  --version "2.0.0" \
  --project-description "Full CLI application" \
  --company-name "TechCorp" \
  --author "CLI Team" \
  --main-file "src/main.py" \
  --output-folder "dist" \
  --include-files "config.yaml" "README.md" \
  --include-folders "assets" "data" \
  --packages "requests" "pandas" "click" \
  --excludes "debugpy" "test" "pytest" \
  --compiler "PyInstaller" \
  --no-console \
  --optimize \
  --zip-needed \
  --output "./config"
```

### Generate Setup via CLI

```bash
# From configuration file
ezcompiler generate setup --config ezcompiler.yaml

# With parameters
ezcompiler generate setup \
  --project-name "SetupApp" \
  --version "1.0.0" \
  --main-file "main.py" \
  --packages "requests" "pandas"
```

### Generate Version via CLI

```bash
# From configuration file
ezcompiler generate version --config ezcompiler.yaml

# With parameters
ezcompiler generate version \
  --project-name "VersionApp" \
  --version "1.0.0" \
  --company-name "TechCorp" \
  --project-description "Application with version info"
```

---

## 🔌 Integration Examples

### CI/CD Integration

**GitHub Actions (.github/workflows/build.yml):**

```yaml
name: Build Application

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install ezcompiler
        pip install -r requirements.txt
    
    - name: Build application
      run: |
        python build.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: application
        path: dist/
```

**build.py for CI/CD:**

```python
import os
from ezcompiler import EzCompiler

def build():
    # Get version from git tag
    version = os.environ.get("GITHUB_REF_NAME", "v1.0.0").lstrip("v")
    
    ezcompiler = EzCompiler()
    
    ezcompiler.init_project(
        version=version,
        project_name="CIApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )
    
    ezcompiler.generate_version_file()
    ezcompiler.compile_project(compiler="PyInstaller")
    ezcompiler.zip_compiled_project()

if __name__ == "__main__":
    build()
```

### Build Script Integration

**Makefile:**

```makefile
.PHONY: build clean release

VERSION := 1.0.0
PROJECT := MyApp

build:
 python -c "from ezcompiler import EzCompiler; e = EzCompiler(); e.init_project(version='$(VERSION)', project_name='$(PROJECT)', main_file='main.py', include_files={'files': [], 'folders': []}, output_folder='dist'); e.compile_project(compiler='PyInstaller')"

clean:
 rm -rf dist/ build/ *.spec

release: build
 mkdir -p releases/v$(VERSION)
 cp -r dist/* releases/v$(VERSION)/
```

### Automated Release Workflow

```python
import subprocess
from pathlib import Path
from ezcompiler import EzCompiler

def automated_release():
    """Automated release workflow."""
    
    # Get version from git tag
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True
    )
    version = result.stdout.strip().lstrip("v") or "1.0.0"
    
    # Build
    ezcompiler = EzCompiler()
    ezcompiler.init_project(
        version=version,
        project_name="AutoRelease",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )
    
    ezcompiler.generate_version_file()
    ezcompiler.compile_project(compiler="PyInstaller")
    ezcompiler.zip_compiled_project()
    
    # Create release
    release_path = Path(f"./releases/v{version}")
    ezcompiler.upload_to_repo(structure="disk", repo_path=release_path)
    
    print(f"Release v{version} created at {release_path}")

if __name__ == "__main__":
    automated_release()
```

---

## 🛠️ Utility Examples

### File Operations

```python
from ezcompiler.utils import FileUtils
from pathlib import Path

def file_operations_example():
    """File utility operations."""
    
    # Ensure directory exists
    FileUtils.ensure_directory(Path("output/temp"))
    
    # Copy file
    FileUtils.copy_file(
        src=Path("config.yaml"),
        dst=Path("output/config.yaml")
    )
    
    # Copy directory
    FileUtils.copy_directory(
        src=Path("assets"),
        dst=Path("output/assets")
    )
    
    # Get file size
    size = FileUtils.get_file_size(Path("output/config.yaml"))
    print(f"File size: {size} bytes")
    
    # Delete directory
    FileUtils.delete_directory(Path("output/temp"))

if __name__ == "__main__":
    file_operations_example()
```

### Validation Operations

```python
from ezcompiler.utils import ValidationUtils

def validation_example():
    """Validation utility operations."""
    
    # Validate version format
    print(ValidationUtils.validate_version("1.0.0"))  # True
    print(ValidationUtils.validate_version("v1.0"))   # False
    
    # Validate compiler name
    print(ValidationUtils.validate_compiler_name("PyInstaller"))  # True
    print(ValidationUtils.validate_compiler_name("Unknown"))      # False
    
    # Validate upload structure
    print(ValidationUtils.validate_upload_structure("disk"))    # True
    print(ValidationUtils.validate_upload_structure("cloud"))   # False
    
    # Validate path
    print(ValidationUtils.validate_path("./existing_file.py"))  # True/False

if __name__ == "__main__":
    validation_example()
```

### ZIP Operations

```python
from ezcompiler.utils import ZipUtils
from pathlib import Path

def zip_example():
    """ZIP utility operations."""
    
    # Create ZIP archive
    ZipUtils.create_zip_archive(
        source=Path("dist/MyApp"),
        destination=Path("dist/MyApp.zip"),
        progress_callback=lambda p: print(f"Progress: {p}%")
    )
    
    # List ZIP contents
    contents = ZipUtils.list_zip_contents(Path("dist/MyApp.zip"))
    print("ZIP contents:")
    for item in contents:
        print(f"  - {item}")
    
    # Extract ZIP archive
    ZipUtils.extract_zip_archive(
        source=Path("dist/MyApp.zip"),
        destination=Path("extracted/")
    )

if __name__ == "__main__":
    zip_example()
```

---

## 🎯 Best Practices Examples

### Error Handling

```python
from ezcompiler import EzCompiler
from ezcompiler.core.exceptions import (
    EzCompilerError,
    CompilationError,
    ConfigurationError,
    TemplateError,
    UploadError,
)

def build_with_error_handling():
    """Build with comprehensive error handling."""
    
    try:
        ezcompiler = EzCompiler()
        
        ezcompiler.init_project(
            version="1.0.0",
            project_name="SafeApp",
            main_file="main.py",
            include_files={"files": [], "folders": []},
            output_folder="dist",
        )
        
        ezcompiler.generate_version_file()
        ezcompiler.compile_project(compiler="PyInstaller")
        ezcompiler.zip_compiled_project()
        
        print("Build completed successfully!")
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        print("Please check your configuration settings.")
        
    except CompilationError as e:
        print(f"Compilation error: {e}")
        print("Please check your code and dependencies.")
        
    except TemplateError as e:
        print(f"Template error: {e}")
        print("Please check template files.")
        
    except UploadError as e:
        print(f"Upload error: {e}")
        print("Please check upload settings and connectivity.")
        
    except EzCompilerError as e:
        print(f"EzCompiler error: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    build_with_error_handling()
```

### Logging Integration

```python
from ezcompiler import EzCompiler

def build_with_logging():
    """Build with logging integration."""
    
    # Create compiler with debug logging
    ezcompiler = EzCompiler(log_level="DEBUG")
    
    # Access logger and printer
    logger = ezcompiler.logger
    printer = ezcompiler.printer
    
    # Use logging
    printer.info("Starting build process...")
    logger.debug("Debug information")
    
    ezcompiler.init_project(
        version="1.0.0",
        project_name="LoggedApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )
    
    printer.success("Project initialized!")
    
    ezcompiler.compile_project(compiler="PyInstaller")
    
    printer.success("Build completed!")
    logger.info("Build process finished successfully")

if __name__ == "__main__":
    build_with_logging()
```

### Configuration Management

```python
import yaml
from pathlib import Path
from ezcompiler import EzCompiler, CompilerConfig

def managed_configuration():
    """Configuration management best practices."""
    
    # Load base configuration
    config_path = Path("ezcompiler.yaml")
    
    if config_path.exists():
        with open(config_path) as f:
            base_config = yaml.safe_load(f)
    else:
        base_config = {
            "version": "1.0.0",
            "project_name": "DefaultApp",
            "main_file": "main.py",
            "output_folder": "dist",
        }
    
    # Override with environment-specific settings
    import os
    if os.environ.get("BUILD_ENV") == "production":
        base_config["optimize"] = True
        base_config["strip"] = True
        base_config["debug"] = False
        base_config["console"] = False
    else:
        base_config["optimize"] = False
        base_config["strip"] = False
        base_config["debug"] = True
        base_config["console"] = True
    
    # Create and validate configuration
    config = CompilerConfig.from_dict(base_config)
    config.validate()
    
    # Build
    ezcompiler = EzCompiler()
    ezcompiler._config = config
    
    ezcompiler.generate_version_file()
    ezcompiler.compile_project()
    
    # Save final configuration for reference
    final_config = config.to_dict()
    with open("build_config.yaml", "w") as f:
        yaml.dump(final_config, f, default_flow_style=False)

if __name__ == "__main__":
    managed_configuration()
```

---

## Additional Resources

- **[API Documentation](../api/API_DOCUMENTATION.md)** – Complete API reference
- **[CLI Documentation](../cli/CLI_DOCUMENTATION.md)** – Command-line interface
- **[Configuration Guide](../cli/CONFIG_GUIDE.md)** – Configuration file guide
- **[Test Documentation](../tests/TEST_DOCUMENTATION.md)** – Test suite documentation

---

**EzCompiler Examples** – Comprehensive usage examples for Python project compilation and distribution.
