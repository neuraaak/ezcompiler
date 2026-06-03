# EzCompiler

[![PyPI version](https://img.shields.io/pypi/v/ezcompiler?style=flat&logo=pypi&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![Python versions](https://img.shields.io/pypi/pyversions/ezcompiler?style=flat&logo=python&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![PyPI status](https://img.shields.io/pypi/status/ezcompiler?style=flat&logo=pypi&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat&logo=github&logoColor=white)](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/neuraaak/ezcompiler/publish-pypi.yml?style=flat&label=ci&logo=githubactions&logoColor=white)](https://github.com/neuraaak/ezcompiler/actions/workflows/publish-pypi.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=flat&logo=materialformkdocs&logoColor=white)](https://neuraaak.github.io/ezcompiler/)
[![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9?style=flat&logo=uv&logoColor=white)](https://github.com/astral-sh/uv)
[![linter](https://img.shields.io/badge/linter-ruff-orange?style=flat&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![type checker](https://img.shields.io/badge/type%20checker-ty-orange?style=flat&logo=astral&logoColor=white)](https://github.com/astral-sh/ty)

**EzCompiler** is a comprehensive Python framework for project compilation, version file generation, packaging, and distribution. It provides a clean and typed API suitable for professional and industrial Python applications.

## ✨ Key features

- **✅ Multi-Compiler Support**: Cx_Freeze, PyInstaller, and Nuitka compilation backends
- **✅ Version File Generation**: Automatic version file creation for Windows executables
- **✅ Project Packaging**: ZIP archive creation with configurable compression
- **✅ Upload Backends**: Disk and HTTP server distribution support
- **✅ Template System**: Template-based generation for configuration, setup, and version files
- **✅ Fully Typed API**: Complete Python 3.11+ type hints for excellent IDE support
- **✅ Modular Validators**: 9 specialized validation modules for robust input validation
- **✅ CLI Interface**: Interactive command-line tool for automation and batch operations
- **✅ Production Ready**: Battle-tested framework for professional applications

## 🚀 Quick start

### Installation

=== "uv"

    ```bash
    uv add ezcompiler
    ```

=== "pip"

    ```bash
    pip install ezcompiler
    ```

Or from source:

=== "uv"

    ```bash
    git clone https://github.com/neuraaak/ezcompiler.git
    cd ezcompiler && uv pip install ezcompiler
    ```

=== "pip"

    ```bash
    git clone https://github.com/neuraaak/ezcompiler.git
    cd ezcompiler && pip install .
    ```

### First Compilation

```python
from ezcompiler import EzCompiler, CompilerConfig

# Create configuration
config = CompilerConfig(
    version="1.0.0",
    project_name="MyProject",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Initialize compiler
ezcompiler = EzCompiler(config)

# Compile project
ezcompiler.compile_project(compiler="PyInstaller")
```

## 📚 Documentation

| Section                               | Description                                          |
| ------------------------------------- | ---------------------------------------------------- |
| [Getting Started](getting-started.md) | Installation, basic usage, and first steps           |
| [API Reference](api/index.md)         | Complete API documentation for all modules           |
| [CLI Reference](cli/index.md)         | Command-line interface documentation                 |
| [Examples](examples/index.md)         | Practical examples and use cases                     |
| [User Guides](guides/index.md)        | In-depth guides for configuration and best practices |

## 🎯 Main components

EzCompiler is organized into **4 main layers**:

### Interfaces Layer

- **`EzCompiler`** – Main facade class for orchestrating the entire compilation process
- **`CLIInterface`** – Interactive command-line interface with rich output

### Services Layer

- **`CompilerService`** – Compiler selection and orchestration
- **`ConfigService`** – Configuration loading and validation
- **`TemplateService`** – Template processing and file generation
- **`UploaderService`** – Upload orchestration and backend selection

### Protocols Layer

**Compilers:**

- **`CxFreezeCompiler`** – Cx_Freeze implementation for directory-based builds
- **`PyInstallerCompiler`** – PyInstaller implementation for single-file executables
- **`NuitkaCompiler`** – Nuitka implementation for optimized compilation

**Uploaders:**

- **`DiskUploader`** – Local disk upload backend
- **`ServerUploader`** – HTTP/HTTPS server upload backend

### Utils Layer

- **`FileUtils`** – File operations and validation
- **`ConfigUtils`** – Configuration parsing (YAML/JSON)
- **`TemplateUtils`** – Template processing utilities
- **`ZipUtils`** – ZIP archive operations
- **`Validators`** – Modular validation package (9 specialized modules)

For detailed documentation, see [API Reference](api/index.md).

## 💻 CLI commands

EzCompiler provides a comprehensive CLI interface:

```bash
# Initialize project interactively
ezcompiler init

# Generate configuration files
ezcompiler generate config --project-name "MyApp"

# Generate setup.py
ezcompiler generate setup --config ezcompiler.yaml

# Generate version information
ezcompiler generate version --config ezcompiler.yaml

# Generate template files
ezcompiler generate template --type config --mockup
```

See the [CLI Reference](cli/index.md) for complete documentation.

## 📋 Requirements

- **Python >= 3.11** – Modern Python with type hints support
- **PyYAML >= 6.0** – YAML configuration support
- **cx_Freeze / PyInstaller / Nuitka** – Compilation backends (optional)

## Architecture layers

| Layer                           | Components                                            | Description                            |
| ------------------------------- | ----------------------------------------------------- | -------------------------------------- |
| [Interfaces](api/interfaces.md) | `EzCompiler`, `CLIInterface`                          | Public APIs and user-facing interfaces |
| [Services](api/services.md)     | `CompilerService`, `ConfigService`, `TemplateService` | Business logic and orchestration       |
| [Adapters](api/adapters.md)     | Compilers, Uploaders, FileWriters                     | Concrete adapter implementations       |
| [Utils](api/utils.md)           | File, Config, Template, Zip, Validators               | Utility functions and validation       |

## ⚖️ License

MIT License – See [LICENSE](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
- **PyPI**: [https://pypi.org/project/ezcompiler/](https://pypi.org/project/ezcompiler/)
- **Issues**: [https://github.com/neuraaak/ezcompiler/issues](https://github.com/neuraaak/ezcompiler/issues)
- **Documentation**: [https://neuraaak.github.io/ezcompiler/](https://neuraaak.github.io/ezcompiler/)

---

**EzCompiler** – Professional Python project compilation and distribution.
