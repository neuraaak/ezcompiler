# Examples

Practical code examples and use cases for **EzCompiler**.

## Overview

This section provides complete, runnable examples for common EzCompiler use cases, from basic compilation to advanced distribution workflows.

---

## Basic Usage

### Simple Project Compilation

Compile a basic Python project with PyInstaller:

```python
from ezcompiler import EzCompiler, CompilerConfig

# Create configuration
config = CompilerConfig(
    version="1.0.0",
    project_name="HelloWorld",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Initialize and compile
ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="PyInstaller")
```

### Configuration from YAML

Load configuration from a YAML file:

```python
from ezcompiler import EzCompiler, CompilerConfig
import yaml

# Load configuration from YAML
with open("ezcompiler.yaml") as f:
    config_dict = yaml.safe_load(f)
    config = CompilerConfig.from_dict(config_dict)

# Initialize and compile
ezcompiler = EzCompiler(config)
ezcompiler.compile_project()
```

YAML file (`ezcompiler.yaml`):

```yaml
version: "1.0.0"
project_name: "MyApp"
main_file: "main.py"
output_folder: "dist"
compiler: "PyInstaller"
packages:
  - "requests"
excludes:
  - "debugpy"
```

---

## Compiler-Specific Examples

### Cx_Freeze Compilation

Directory-based build with Cx_Freeze:

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={
        "files": ["config.yaml"],
        "folders": ["assets", "data"]
    },
    output_folder="dist",
    compiler="Cx_Freeze",
    packages=["requests", "pandas"],
    excludes=["debugpy", "pytest"],
    compiler_options={
        "zip_include_packages": ["*"],
        "zip_exclude_packages": ["test"],
        "include_msvcr": True,
        "optimize": 2
    }
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="Cx_Freeze")
```

### PyInstaller Compilation

Single-file executable with PyInstaller:

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={
        "files": ["icon.ico"],
        "folders": ["resources"]
    },
    output_folder="dist",
    compiler="PyInstaller",
    packages=["numpy", "scipy"],
    excludes=["matplotlib"],
    compiler_options={
        "onefile": True,
        "windowed": False,
        "icon": "icon.ico",
        "log-level": "DEBUG"
    }
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="PyInstaller")
```

### Nuitka Compilation

Optimized native compilation with Nuitka:

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": ["data"]},
    output_folder="dist",
    compiler="Nuitka",
    packages=["fastapi", "uvicorn"],
    compiler_options={
        "onefile": True,
        "show-progress": True,
        "enable-plugin": "pyside6",
        "windows-disable-console": False
    }
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="Nuitka")
```

---

## Complete Workflow Examples

### Compile, Package, and Upload to Disk

```python
from ezcompiler import EzCompiler, CompilerConfig

# Configuration
config = CompilerConfig(
    version="1.0.0",
    project_name="ProductionApp",
    main_file="main.py",
    include_files={
        "files": ["config.yaml", "LICENSE"],
        "folders": ["assets", "templates"]
    },
    output_folder="dist",
    compiler="PyInstaller",
    packages=["requests", "pandas"],
    excludes=["debugpy", "pytest"],
)

# Initialize compiler
ezcompiler = EzCompiler(config)

# Complete workflow
print("Compiling project...")
ezcompiler.compile_project(compiler="PyInstaller")

print("Creating ZIP archive...")
ezcompiler.zip_compiled_project()

print("Uploading to disk repository...")
ezcompiler.upload_to_repo(
    structure="disk",
    repo_path="./releases"
)

print("Build complete!")
```

### Compile and Upload to HTTP Server

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="2.1.0",
    project_name="WebApp",
    main_file="app.py",
    include_files={"files": [], "folders": ["static", "templates"]},
    output_folder="dist",
    compiler="Cx_Freeze",
    packages=["flask", "sqlalchemy"],
)

ezcompiler = EzCompiler(config)

# Compile
ezcompiler.compile_project(compiler="Cx_Freeze")

# Package
ezcompiler.zip_compiled_project()

# Upload to HTTP server
ezcompiler.upload_to_repo(
    structure="server",
    repo_url="https://releases.example.com/upload",
    credentials={
        "username": "deploy_user",
        "password": "secure_password"
    }
)
```

---

## Advanced Configuration

### Multi-File Project with Resources

```python
from ezcompiler import EzCompiler, CompilerConfig
from pathlib import Path

# Complex project structure
config = CompilerConfig(
    version="3.0.0",
    project_name="EnterpriseApp",
    main_file="src/main.py",
    include_files={
        "files": [
            "config/app.yaml",
            "config/db.yaml",
            "LICENSE.txt",
            "README.md"
        ],
        "folders": [
            "src/assets",
            "src/templates",
            "locales",
            "plugins"
        ]
    },
    output_folder="build/dist",
    compiler="Cx_Freeze",
    packages=[
        "sqlalchemy",
        "alembic",
        "pydantic",
        "fastapi",
        "uvicorn"
    ],
    excludes=[
        "debugpy",
        "pytest",
        "mypy",
        "ruff",
        "ipython"
    ],
    compiler_options={
        "zip_include_packages": [
            "sqlalchemy",
            "pydantic"
        ],
        "zip_exclude_packages": [
            "test",
            "tests"
        ],
        "include_msvcr": True,
        "optimize": 2
    }
)

ezcompiler = EzCompiler(config, log_level="DEBUG")
ezcompiler.compile_project()
```

### Conditional Compilation

```python
from ezcompiler import EzCompiler, CompilerConfig
import sys

# Choose compiler based on platform
if sys.platform == "win32":
    compiler = "Cx_Freeze"
    compiler_opts = {
        "include_msvcr": True,
        "optimize": 2
    }
elif sys.platform == "darwin":
    compiler = "PyInstaller"
    compiler_opts = {
        "onefile": True,
        "windowed": True
    }
else:  # Linux
    compiler = "Nuitka"
    compiler_opts = {
        "onefile": True,
        "show-progress": True
    }

config = CompilerConfig(
    version="1.0.0",
    project_name="CrossPlatformApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
    compiler=compiler,
    compiler_options=compiler_opts
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler=compiler)
```

---

## Error Handling

### Comprehensive Error Handling

```python
from ezcompiler import EzCompiler, CompilerConfig
from ezcompiler.shared.exceptions import (
    CompilationError,
    ConfigurationError,
    FileOperationError,
    UploadError
)

config = CompilerConfig(
    version="1.0.0",
    project_name="RobustApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

try:
    ezcompiler = EzCompiler(config)

    # Compile
    ezcompiler.compile_project(compiler="PyInstaller")

    # Package
    ezcompiler.zip_compiled_project()

    # Upload
    ezcompiler.upload_to_repo(
        structure="disk",
        repo_path="./releases"
    )

    print("✓ Build successful!")

except ConfigurationError as e:
    print(f"✗ Configuration error: {e}")
    exit(1)

except CompilationError as e:
    print(f"✗ Compilation failed: {e}")
    print("Check compiler logs in the output folder")
    exit(2)

except FileOperationError as e:
    print(f"✗ File operation error: {e}")
    exit(3)

except UploadError as e:
    print(f"✗ Upload failed: {e}")
    exit(4)

except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(255)
```

---

## CI/CD Integration

### GitHub Actions Workflow

`.github/workflows/build.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - "v*"

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install ezcompiler
          pip install -r requirements.txt

      - name: Build project
        run: |
          python build.py

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist-${{ matrix.os }}-py${{ matrix.python-version }}
          path: dist/*.zip
```

Build script (`build.py`):

```python
from ezcompiler import EzCompiler, CompilerConfig
import sys

config = CompilerConfig(
    version="1.0.0",
    project_name="CIApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
    compiler="PyInstaller" if sys.platform == "win32" else "Nuitka",
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project()
ezcompiler.zip_compiled_project()
```

### GitLab CI Pipeline

`.gitlab-ci.yml`:

```yaml
stages:
  - build
  - package
  - deploy

build:
  stage: build
  image: python:3.11
  script:
    - pip install ezcompiler
    - pip install -r requirements.txt
    - python build.py
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

package:
  stage: package
  script:
    - python package.py
  dependencies:
    - build
  artifacts:
    paths:
      - dist/*.zip

deploy:
  stage: deploy
  script:
    - python deploy.py
  dependencies:
    - package
  only:
    - tags
```

---

## Template Usage

### Generate Template Files

```python
from ezcompiler.services import TemplateService

# Initialize template service
template_service = TemplateService()

# Process configuration template
config_content = template_service.process_template(
    template_name="config.yaml",
    variables={
        "PROJECT_NAME": "MyApp",
        "VERSION": "1.0.0",
        "MAIN_FILE": "main.py"
    }
)

# Save to file
with open("ezcompiler.yaml", "w") as f:
    f.write(config_content)
```

---

## Best Practices

### Project Structure

Recommended project structure for EzCompiler projects:

```text
myproject/
├── src/
│   ├── main.py
│   ├── config/
│   └── utils/
├── assets/
│   ├── images/
│   └── fonts/
├── config/
│   └── app.yaml
├── ezcompiler.yaml
├── requirements.txt
└── build.py
```

### Build Script Template

`build.py`:

```python
#!/usr/bin/env python3
"""Build script for MyProject."""

from ezcompiler import EzCompiler, CompilerConfig
from pathlib import Path
import yaml

def load_config(path: str) -> CompilerConfig:
    """Load configuration from YAML file."""
    with open(path) as f:
        config_dict = yaml.safe_load(f)
    return CompilerConfig.from_dict(config_dict)

def main():
    """Main build function."""
    # Load configuration
    config = load_config("ezcompiler.yaml")

    # Initialize compiler
    ezcompiler = EzCompiler(config, log_level="INFO")

    # Build workflow
    print("Starting build process...")

    print("1. Compiling project...")
    ezcompiler.compile_project()

    print("2. Creating ZIP archive...")
    ezcompiler.zip_compiled_project()

    print("3. Uploading to repository...")
    ezcompiler.upload_to_repo(
        structure="disk",
        repo_path="./releases"
    )

    print("✓ Build complete!")

if __name__ == "__main__":
    main()
```

---

## See Also

- [Getting Started](../getting-started.md) – Installation and basic usage
- [API Reference](../api/index.md) – Complete API documentation
- [CLI Reference](../cli/index.md) – Command-line interface
- [User Guides](../guides/index.md) – Configuration and best practices

---

## Need Help?

- **Documentation**: [Full Documentation](../index.md)
- **API Reference**: [API Docs](../api/index.md)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
