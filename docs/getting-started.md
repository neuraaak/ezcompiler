# Getting Started

This guide will help you get started with **EzCompiler** quickly and easily.

## Installation

### From PyPI (Recommended)

```bash
pip install ezcompiler
```

### From Source

```bash
git clone https://github.com/neuraaak/ezcompiler.git
cd ezcompiler
pip install .
```

### Development Installation

For contributors and developers:

```bash
pip install -e ".[dev]"
```

This installs EzCompiler in editable mode with all development dependencies (testing, linting, formatting tools).

---

## Requirements

- **Python** >= 3.11
- **PyYAML** >= 6.0
- **One or more compilers**:
  - **cx_Freeze** >= 7.2.6 (for directory-based builds)
  - **PyInstaller** >= 6.11.1 (for single-file executables)
  - **Nuitka** >= 2.5.7 (for optimized compilation)

---

## First Steps

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

## Configuration Options

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

## Choosing a Compiler

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

## Compiler-Specific Options

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

## Including Files and Folders

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

## Package Management

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

## Packaging and Distribution

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

## Type Hints Support

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

## Next Steps

Now that you've set up EzCompiler, explore these resources:

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
4. Enable debug logging:

```python
ezcompiler = EzCompiler(config, log_level="DEBUG")
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

## Need Help?

- **Documentation**: [Full API Reference](api/index.md)
- **Examples**: [Code Examples](examples/index.md)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)

---

**Ready to compile your Python projects!** 🚀
