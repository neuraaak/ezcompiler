# Getting started

This guide walks you through installing EzCompiler and running your first compilation.

## 🔧 Prerequisites

- Python >= 3.11
- One compilation backend: `cx_Freeze`, `PyInstaller`, or `Nuitka`
- PyYAML >= 6.0

## Installation

=== "uv"

    ```bash
    uv add ezcompiler
    ```

=== "pip"

    ```bash
    pip install ezcompiler
    ```

### From source

=== "uv"

    ```bash
    git clone https://github.com/neuraaak/ezcompiler.git
    cd ezcompiler
    uv pip install -e .
    ```

=== "pip"

    ```bash
    git clone https://github.com/neuraaak/ezcompiler.git
    cd ezcompiler
    pip install .
    ```

### Development installation

For contributors and developers:

=== "uv"

    ```bash
    uv pip install -e ".[dev]"
    ```

=== "pip"

    ```bash
    pip install -e ".[dev]"
    ```

This installs EzCompiler in editable mode with all development dependencies (testing, linting, formatting tools).

---

## 📝 First steps

### Basic Project Compilation

```python
from ezcompiler import EzCompiler, CompilerConfig

# Create configuration
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Initialize compiler
ezcompiler = EzCompiler(config)

# Compile project
ezcompiler.compile_project(compiler="PyInstaller")
```

### Complete Workflow Example

```python
from ezcompiler import EzCompiler, CompilerConfig

# Create comprehensive configuration
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={
        "files": ["config.yaml", "data.json"],
        "folders": ["assets", "templates"]
    },
    output_folder="dist",
    packages=["requests", "pandas"],
    excludes=["debugpy", "pytest"],
)

# Initialize compiler
ezcompiler = EzCompiler(config)

# Full workflow
ezcompiler.compile_project(compiler="PyInstaller")
ezcompiler.zip_compiled_project()
ezcompiler.upload_to_repo(structure="disk", repo_path="./releases")
```

---

## Configuration options

### From Python Code

```python
from ezcompiler import CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
    compiler="PyInstaller",
    packages=["requests"],
    excludes=["debugpy"],
)
```

### From YAML File

Create `ezcompiler.yaml`:

```yaml
version: "1.0.0"
project_name: "MyApp"
main_file: "main.py"
output_folder: "dist"
compiler: "PyInstaller"
packages:
  - "requests"
  - "pandas"
excludes:
  - "debugpy"
  - "test"
include_files:
  files:
    - "config.yaml"
  folders:
    - "assets"
```

Then load it:

```python
from ezcompiler import EzCompiler
import yaml

with open("ezcompiler.yaml") as f:
    config_dict = yaml.safe_load(f)

ezcompiler = EzCompiler.from_dict(config_dict)
ezcompiler.compile_project()
```

### From JSON File

Create `ezcompiler.json`:

```json
{
  "version": "1.0.0",
  "project_name": "MyApp",
  "main_file": "main.py",
  "output_folder": "dist",
  "packages": ["requests", "pandas"]
}
```

---

## Using the CLI

See the [CLI Reference](cli/index.md) for the full command listing and option tables.

EzCompiler includes a powerful command-line interface:

### Initialize Project

```bash
ezcompiler init
```

This will guide you through an interactive setup process.

### Generate Configuration File

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py"
```

### Generate Setup File

```bash
ezcompiler generate setup --config ezcompiler.yaml
```

### Generate Version File

```bash
ezcompiler generate version --config ezcompiler.yaml
```

### Generate Template

```bash
# Generate config template
ezcompiler generate template --type config --mockup

# Generate setup template
ezcompiler generate template --type setup --mockup

# Generate version template
ezcompiler generate template --type version --mockup
```

For more details, see the [CLI Reference](cli/index.md).

---

## Choosing a compiler

EzCompiler supports three compilation backends:

### PyInstaller (Single-File Executables)

**Best for:**

- Simple distribution
- Single-file executables
- Quick prototyping

```python
ezcompiler.compile_project(compiler="PyInstaller")
```

**Pros:**

- Single executable file
- Easy distribution
- Wide platform support

**Cons:**

- Slower startup time
- Larger file size

### Cx_Freeze (Directory-Based Builds)

**Best for:**

- Large applications
- Better performance
- Modular distribution

```python
ezcompiler.compile_project(compiler="Cx_Freeze")
```

**Pros:**

- Faster execution
- Better for large apps
- More granular control

**Cons:**

- Directory structure (multiple files)
- More complex distribution

### Nuitka (Optimized Compilation)

**Best for:**

- Maximum performance
- Native compilation
- Production deployments

```python
ezcompiler.compile_project(compiler="Nuitka")
```

**Pros:**

- Best performance
- True native compilation
- Smaller memory footprint

**Cons:**

- Longer compilation time
- More complex setup

---

## Compiler-specific options

### Cx_Freeze Options

```python
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
    compiler="Cx_Freeze",
    compiler_options={
        "zip_include_packages": ["*"],
        "zip_exclude_packages": ["test", "tkinter"],
        "include_msvcr": True,
        "optimize": 2
    }
)
```

### PyInstaller Options

```python
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
    compiler="PyInstaller",
    compiler_options={
        "log-level": "DEBUG",
        "collect-all": "numpy",
        "onefile": True
    }
)
```

### Nuitka Options

```python
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
    compiler="Nuitka",
    compiler_options={
        "show-progress": True,
        "enable-plugin": "numpy",
        "onefile": True
    }
)
```

---

## Including files and folders

### Include Specific Files

```python
config = CompilerConfig(
    # ... other options ...
    include_files={
        "files": [
            "config.yaml",
            "data.json",
            "README.txt"
        ],
        "folders": []
    }
)
```

### Include Entire Folders

```python
config = CompilerConfig(
    # ... other options ...
    include_files={
        "files": [],
        "folders": [
            "assets",
            "templates",
            "locale"
        ]
    }
)
```

### Mixed Approach

```python
config = CompilerConfig(
    # ... other options ...
    include_files={
        "files": ["config.yaml", "data.json"],
        "folders": ["assets", "templates"]
    }
)
```

---

## Package management

### Include Required Packages

```python
config = CompilerConfig(
    # ... other options ...
    packages=[
        "requests",
        "pandas",
        "numpy",
        "sqlalchemy"
    ]
)
```

### Exclude Unnecessary Packages

```python
config = CompilerConfig(
    # ... other options ...
    excludes=[
        "debugpy",
        "pytest",
        "mypy",
        "ruff"
    ]
)
```

---

## Packaging and distribution

### Create ZIP Archive

```python
# After compilation
ezcompiler.zip_compiled_project()
```

This creates a ZIP archive of the compiled project in the output folder.

### Upload to Disk Repository

```python
# Upload to local disk
ezcompiler.upload_to_repo(
    structure="disk",
    repo_path="./releases"
)
```

### Upload to HTTP Server

```python
# Upload to HTTP server
ezcompiler.upload_to_repo(
    structure="server",
    repo_url="https://releases.mycompany.com/upload",
    credentials={"username": "user", "password": "pass"}
)
```

---

## Type hints support

EzCompiler provides full type hints for better IDE support:

```python
from ezcompiler import EzCompiler, CompilerConfig

# Type-annotated configuration
config: CompilerConfig = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Type-safe compiler instance
ezcompiler: EzCompiler = EzCompiler(config)

# Type-safe method calls
result: bool = ezcompiler.compile_project(compiler="PyInstaller")
```

### IDE Benefits

With full type hints, you get:

- **Auto-completion** for methods and properties
- **Type checking** with mypy, pyright, or IDE built-in checkers
- **Inline documentation** from docstrings
- **Error detection** before runtime

---

## ➡️ Next steps

Now that you've compiled your first project, explore these resources:

- **[API Reference](api/index.md)** – Detailed documentation for each module with all classes and methods
- **[CLI Reference](cli/index.md)** – Complete command-line interface documentation
- **[Examples](examples/index.md)** – Complete code examples and use cases
- **[User Guides](guides/index.md)** – In-depth tutorials for configuration and best practices

---

## Troubleshooting

### Import Error

If you encounter import errors:

```python
# Make sure you're importing from 'ezcompiler'
from ezcompiler import EzCompiler, CompilerConfig  # Correct
```

### Compiler Not Found

If compilation fails with "compiler not found":

```bash
# Install the compiler you want to use
pip install cx-freeze      # For Cx_Freeze
pip install pyinstaller    # For PyInstaller
pip install nuitka         # For Nuitka
```

### Version Compatibility

Check your installed version:

```python
import ezcompiler
print(ezcompiler.__version__)  # Should be 2.3.1 or higher
```

Or from command line:

```bash
ezcompiler --version
```

### Compilation Errors

If compilation fails:

1. Check that all required files exist
2. Verify package names are correct
3. Check compiler-specific logs in the output folder
4. Enable debug logging from the host application.

   EzCompiler uses the [`ezplog`](https://pypi.org/project/ezplog/) `lib_mode`
   pattern: its printer and logger are passive proxies that produce no output
   until the host application initializes Ezpl. The library never configures
   logging on its own.

   ```python
   from ezplog import Ezpl
   from ezcompiler import EzCompiler, CompilerConfig

   # Host application configures logging once, at the entry point.
   Ezpl(level="DEBUG")

   ezcompiler = EzCompiler(config)
   ezcompiler.compile_project()

   # Direct access to the underlying proxies if needed:
   ezcompiler.logger.debug("Custom debug message")
   ezcompiler.printer.info("Custom console message")
   ```

### Configuration Errors

If configuration is invalid:

```python
from ezcompiler.shared.exceptions import ConfigurationError

try:
    ezcompiler = EzCompiler(config)
    ezcompiler.compile_project()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

---

## Need help?

- **Documentation**: [Full API Reference](api/index.md)
- **Examples**: [Code Examples](examples/index.md)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)

---

**Ready to compile your Python projects.**
