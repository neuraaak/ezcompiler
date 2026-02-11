# Welcome to EzCompiler Documentation

[![PyPI](https://img.shields.io/badge/PyPI-ezcompiler-orange.svg)](https://pypi.org/project/ezcompiler/)
[![PyPI version](https://img.shields.io/pypi/v/ezcompiler)](https://pypi.org/project/ezcompiler/)
[![Python versions](https://img.shields.io/pypi/pyversions/ezcompiler)](https://pypi.org/project/ezcompiler/)
[![License](https://img.shields.io/pypi/l/ezcompiler)](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE)

![EzCompiler Logo](https://raw.githubusercontent.com/neuraaak/ezcompiler/refs/heads/main/docs/assets/logo-min.png)

**EzCompiler** is a comprehensive Python framework for project compilation, version file generation, packaging, and distribution. It provides a clean and typed API suitable for professional and industrial Python applications.

## ✨ Key Features

- **✅ Multi-Compiler Support**: Cx_Freeze, PyInstaller, and Nuitka compilation backends
- **✅ Version File Generation**: Automatic version file creation for Windows executables
- **✅ Project Packaging**: ZIP archive creation with configurable compression
- **✅ Upload Backends**: Disk and HTTP server distribution support
- **✅ Template System**: Template-based generation for configuration, setup, and version files
- **✅ Fully Typed API**: Complete Python 3.10+ type hints for excellent IDE support
- **✅ Modular Validators**: 9 specialized validation modules for robust input validation
- **✅ CLI Interface**: Interactive command-line tool for automation and batch operations
- **✅ Production Ready**: Battle-tested framework for professional applications

## 🚀 Quick Start

### Installation

```bash
pip install ezcompiler
```

Or from source:

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

## 📚 Documentation Structure

| Section                               | Description                                          |
| ------------------------------------- | ---------------------------------------------------- |
| [Getting Started](getting-started.md) | Installation, basic usage, and first steps           |
| [API Reference](api/index.md)         | Complete API documentation for all modules           |
| [CLI Reference](cli/index.md)         | Command-line interface documentation                 |
| [Examples](examples/index.md)         | Practical examples and use cases                     |
| [User Guides](guides/index.md)        | In-depth guides for configuration and best practices |

## 🎯 Main Components

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

## 🔧 CLI Commands

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

## 📦 Core Dependencies

- **Python >= 3.10** – Modern Python with type hints support
- **PyYAML >= 6.0** – YAML configuration support
- **cx_Freeze / PyInstaller / Nuitka** – Compilation backends (optional)

## 🎨 Architecture Layers

| Layer                           | Components                                            | Description                            |
| ------------------------------- | ----------------------------------------------------- | -------------------------------------- |
| [Interfaces](api/interfaces.md) | `EzCompiler`, `CLIInterface`                          | Public APIs and user-facing interfaces |
| [Services](api/services.md)     | `CompilerService`, `ConfigService`, `TemplateService` | Business logic and orchestration       |
| [Protocols](api/protocols.md)   | Compilers, Uploaders                                  | Implementation protocols and adapters  |
| [Utils](api/utils.md)           | File, Config, Template, Zip, Validators               | Utility functions and validation       |

## 📝 License

MIT License – See [LICENSE](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
- **PyPI**: [https://pypi.org/project/ezcompiler/](https://pypi.org/project/ezcompiler/)
- **Issues**: [https://github.com/neuraaak/ezcompiler/issues](https://github.com/neuraaak/ezcompiler/issues)
- **Documentation**: [https://neuraaak.github.io/ezcompiler/](https://neuraaak.github.io/ezcompiler/)

---

**EzCompiler** – Professional Python project compilation and distribution. 🚀
