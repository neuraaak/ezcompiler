# EzCompiler

[![PyPI version](https://img.shields.io/pypi/v/ezcompiler?style=flat&logo=pypi&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![Python versions](https://img.shields.io/pypi/pyversions/ezcompiler?style=flat&logo=python&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![PyPI status](https://img.shields.io/pypi/status/ezcompiler?style=flat&logo=pypi&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat&logo=github&logoColor=white)](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/neuraaak/ezcompiler/01-ci.yml?style=flat&label=ci&logo=githubactions&logoColor=white)](https://github.com/neuraaak/ezcompiler/actions/workflows/01-ci.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=flat&logo=materialformkdocs&logoColor=white)](https://neuraaak.github.io/ezcompiler/)
[![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9?style=flat&logo=uv&logoColor=white)](https://github.com/astral-sh/uv)
[![linter](https://img.shields.io/badge/linter-ruff-D7FF64?style=flat&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![type checker](https://img.shields.io/badge/type%20checker-ty-261230?style=flat&logo=astral&logoColor=white)](https://github.com/astral-sh/ty)
[![tests](https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://github.com/pytest-dev/pytest)

![EzCompiler Logo](https://raw.githubusercontent.com/neuraaak/ezcompiler/refs/heads/main/docs/assets/logo-min.png)

**EzCompiler** is a professional Python library for compiling projects into executable files with automatic version management, packaging, and distribution. It provides a unified interface for multiple compilers (Cx_Freeze, PyInstaller, Nuitka) with modular architecture and complete type hints.

## 📦 Installation

```bash
# With uv (recommended)
uv add ezcompiler

# With pip
pip install ezcompiler
```

Or from source:

```bash
git clone https://github.com/neuraaak/ezcompiler.git
cd ezcompiler

uv pip install -e .   # uv
pip install -e .      # pip
```

The unreleased `main` branch can also be installed directly:

```bash
uv pip install git+https://github.com/neuraaak/ezcompiler.git
pip install git+https://github.com/neuraaak/ezcompiler.git
```

## 🚀 Quick Start

```python
from ezcompiler import EzCompiler

# Initialize
compiler = EzCompiler()

# Configure project
compiler.init_project(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Run the full build pipeline with DLP progress display
# (version, compile, zip, installer, TUF release — all local)
compiler.run_pipeline(console=True)
```

Publication is a separate, deliberate CLI step:

```bash
# Publication is a separate CLI step: it reads your ezcompiler.yaml / pyproject.toml
ezcompiler publish release --release-destination disk --destination ./releases
```

## 🎯 Key Features

- **✅ Multi-Compiler Support**: Cx_Freeze, PyInstaller, and Nuitka with unified interface
- **✅ Automatic File Generation**: Version files, `build.py` scripts, and configuration from templates
- **✅ Template System**: Flexible file generation based on customizable templates
- **✅ Packaging**: Automatic ZIP archive creation for distribution
- **✅ Publication**: `ezcompiler publish` to local disk, HTTP/HTTPS servers, R2 or GitHub Releases, with a recap and confirmation before irreversible steps
- **✅ Configuration Management**: Centralized configuration with automatic validation
- **✅ Structured Logging**: Integration with Ezpl for professional logging
- **✅ Full Type Hints**: Complete typing support for IDEs and linters

## 📚 Documentation

Complete documentation is available at **[neuraaak.github.io/ezcompiler](https://neuraaak.github.io/ezcompiler/)**

- **[Getting Started](https://neuraaak.github.io/ezcompiler/getting-started/)** – Installation, basic usage, and first steps
- **[API Reference](https://neuraaak.github.io/ezcompiler/api/)** – Complete API documentation with examples
- **[CLI Reference](https://neuraaak.github.io/ezcompiler/cli/)** – Command-line interface guide
- **[User Guides](https://neuraaak.github.io/ezcompiler/guides/)** – Configuration, development, and testing guides
- **[Examples](https://neuraaak.github.io/ezcompiler/examples/)** – Practical examples and demonstrations

## 🧪 Testing

Comprehensive test suite with 999 test cases covering unit, integration, and robustness scenarios (82.85% branch coverage, CI gate at 70%).

```bash
# Install dev dependencies
uv sync --all-extras --group dev

# Run all tests
pytest tests/

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration
python tests/run_tests.py --type robustness

# With coverage
python tests/run_tests.py --coverage
```

See **[Development Guide](docs/guides/development.md)** for testing details.

## 🛠️ Development Setup

For contributors and developers:

```bash
# Install in development mode with all dependencies
uv sync --all-extras --group dev

# Run tests
pytest tests/

# Run linting and formatting
ruff check .
ruff format --check .
ty check src/ezcompiler/
pyright src/ezcompiler/
PYTHONPATH=src lint-imports
```

## 🎨 Main Components

- **`EzCompiler`**: Main facade class for orchestrating the entire compilation process
- **`CompilerConfig`**: Centralized configuration management
- **`CompilationResult`**: Result type for compilation operations (shared layer)
- **`PipelineService`**: Full compile → zip → upload pipeline orchestration
- **`CompilerService`**: Compiler selection and execution
- **`ConfigService`**: Configuration loading with cascade merge
- **`TemplateService`**: Template processing and file generation
- **`CompilerFactory`**: Factory for creating compiler instances
- **`BaseCompiler`**: Abstract base class for compiler adapters
- **`CxFreezeCompiler`**: Cx_Freeze compiler implementation
- **`PyInstallerCompiler`**: PyInstaller compiler implementation
- **`NuitkaCompiler`**: Nuitka compiler implementation (standalone & onefile)
- **`BaseFileWriter`** / **`DiskFileWriter`**: File writer port and disk adapter
- **`BaseUploader`**: Abstract base class for uploader adapters
- **`DiskUploader`**: Local disk uploader
- **`ServerUploader`**: HTTP/HTTPS uploader

## 📦 Dependencies

| Package         | Version | Description                   |
| --------------- | ------- | ----------------------------- |
| **cx_Freeze**   | 7.0-9.0 | Python to executable compiler |
| **PyInstaller** | 5.0+    | Python to executable compiler |
| **Nuitka**      | 2.4+    | Python to executable compiler |
| **InquirerPy**  | 0.3.4+  | Interactive CLI interface     |
| **requests**    | 2.32.3+ | HTTP library for uploads      |
| **PyYAML**      | 6.0+    | YAML file processing          |
| **click**       | 8.0.0+  | CLI framework                 |
| **ezplog**      | 1.0.0+  | Structured logging framework  |

## 🔧 Quick API Reference

```python
from ezcompiler import EzCompiler, CompilerConfig

# Create compiler instance
compiler = EzCompiler()

# Initialize project
compiler.init_project(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": ["config.yaml"], "folders": ["assets"]},
    output_folder="dist",
)

# Run full pipeline with DLP progress (version, compile, zip, installer, release)
compiler.run_pipeline(console=True)

# Or call individual steps manually:
# compiler.generate_version_file()
# compiler.compile_project(compiler="Nuitka")
# compiler.zip_compiled_project()
```

The Python API never publishes. Use the CLI afterwards:
`ezcompiler publish update` (TUF update tree) and `ezcompiler publish release`
(installer + ZIP). `EzCompiler.upload()` is deprecated and will be removed in v5.

## 🛡️ Robustness

EzCompiler is designed for production use with comprehensive error handling:

- Full type hints for IDE support and static analysis
- Robust error handling with specific exceptions
- Automatic validation of configuration
- Cross-platform file operations
- Support for various file encodings and special characters

## 💻 CLI Usage

```bash
# Create a YAML configuration file
ezcompiler init yaml

# Generate configuration
ezcompiler generate config \
  --project-name "MyApp" \
  --version "1.0.0" \
  --main-file "main.py"

# Generate build.py
ezcompiler generate build --config ezcompiler.yaml

# Generate a version file
ezcompiler generate template --type version

# Generate templates
ezcompiler generate template --type config --mockup

# Publish the TUF update tree, then the release
ezcompiler publish update
ezcompiler publish release
```

See **[CLI Reference](docs/cli/index.md)** for complete reference.

## 🔄 Configuration

### YAML Configuration

```yaml
version: "1.0.0"
project_name: "MyApp"
main_file: "main.py"
output_folder: "dist"

include_files:
  files:
    - "config.yaml"
  folders:
    - "assets"

packages:
  - "requests"
  - "pandas"

excludes:
  - "debugpy"
  - "test"

compilation:
  compiler: "auto" # "auto", "Cx_Freeze", "PyInstaller", or "Nuitka"
  console: true
  zip_needed: true
  repo_needed: false
```

See **[Configuration Guide](docs/guides/configuration.md)** for detailed configuration options.

## 📊 Architecture

```txt
ezcompiler/
├── interfaces/          # CLI and Python API (entry points)
├── services/            # Business logic orchestration
│   ├── compiler_service.py
│   ├── config_service.py
│   ├── pipeline_service.py
│   ├── template_service.py
│   └── uploader_service.py
├── adapters/            # Concrete compiler and uploader implementations
│   ├── cx_freeze_compiler.py
│   ├── pyinstaller_compiler.py
│   ├── nuitka_compiler.py
│   ├── compiler_factory.py
│   ├── disk_file_writer.py
│   ├── disk_uploader.py
│   └── server_uploader.py
├── shared/              # Configuration, result types and exceptions
│   ├── compiler_config.py
│   └── compilation_result.py
├── utils/               # Utility functions
└── assets/templates/    # Template files (build, config, installer, updater, version)
```

`assets/` is a dedicated resource layer for non-executable project artifacts
(template files, static generation resources). It is consumed by services
through template loaders and remains isolated from business orchestration logic.

## 🚀 Use Cases

### Python Project Compilation

- Create Windows executables from Python scripts
- Package projects with dependencies
- Automatically generate configuration files

### Automated Distribution

- Create ZIP archives for distribution
- Automatic upload to local or remote repositories
- Version management and metadata handling

### Development Tools

- Generate `build.py` pipeline scripts for repeatable builds
- Create Windows version information files
- Automate build workflows

### Project Management

- Centralized configuration via YAML/JSON files
- Customizable templates for file generation
- Integration into CI/CD pipelines

## 🤝 Contributing

1. Clone the repository (`git clone https://github.com/neuraaak/ezcompiler.git`)
2. Create a feature branch (`git checkout -b feat/ma-feature`)
3. Commit your changes
4. Submit a Pull Request for internal review
5. Review is handled through pull requests

## ⭐ Support

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **💡 Feature Requests**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **📚 Documentation**: [Complete Documentation](https://neuraaak.github.io/ezcompiler/)

## 📝 License

MIT License – See [LICENSE](LICENSE) file for details.

## 👥 Ownership

Maintained by **Neuraaak**.

- **Contact**: <floriansalort@gmail.com>

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Documentation**: [https://neuraaak.github.io/ezcompiler/](https://neuraaak.github.io/ezcompiler/)

---

**EzCompiler** – Professional Python project compilation and distribution. 🚀
