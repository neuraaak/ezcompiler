# 🚀 EzCompiler

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgray.svg?style=for-the-badge&logo=windows)](https://pypi.org/project/ezcompiler/)
[![Version](https://img.shields.io/badge/Version-2.3.1-orange.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)
[![PyPI](https://img.shields.io/badge/PyPI-ezcompiler-green.svg?style=for-the-badge&logo=pypi)](https://pypi.org/project/ezcompiler/)
[![Docs](https://img.shields.io/badge/Docs-Online-blue.svg?style=for-the-badge&logo=readthedocs)](https://neuraaak.github.io/ezcompiler/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)
[![Tests](https://img.shields.io/badge/Tests-233%20passing-success.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)
[![Coverage](https://img.shields.io/badge/Coverage-63%25-green.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)

![EzCompiler Logo](docs/assets/logo-min.png)

**EzCompiler** is a professional Python library for compiling projects into executable files with automatic version management, packaging, and distribution. It provides a unified interface for multiple compilers (Cx_Freeze, PyInstaller, Nuitka) with modular architecture and complete type hints.

## 📦 Installation

```bash
pip install ezcompiler
```

Or from source:

```bash
git clone https://github.com/neuraaak/ezcompiler.git
cd ezcompiler && pip install .
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
compiler.run_pipeline(
    console=True,
    upload_structure="disk",
    upload_destination="./releases",
)
```

## 🎯 Key Features

- **✅ Multi-Compiler Support**: Cx_Freeze, PyInstaller, and Nuitka with unified interface
- **✅ Automatic File Generation**: Version files, setup.py, and configuration from templates
- **✅ Template System**: Flexible file generation based on customizable templates
- **✅ Packaging**: Automatic ZIP archive creation for distribution
- **✅ Distribution**: Upload support for local disk and remote HTTP/HTTPS servers
- **✅ Configuration Management**: Centralized configuration with automatic validation
- **✅ Structured Logging**: Integration with Ezpl for professional logging
- **✅ Full Type Hints**: Complete typing support for IDEs and linters

## 📚 Documentation

- **[📖 Getting Started](docs/getting-started.md)** – Installation and first steps
- **[📋 API Reference](docs/api/index.md)** – Complete API documentation with auto-generation
- **[🖥️ CLI Reference](docs/cli/index.md)** – Command-line interface guide
- **[⚙️ Configuration Guide](docs/guides/configuration.md)** – Detailed configuration options
- **[💡 Examples](docs/examples/index.md)** – Usage examples and demonstrations
- **[👨‍💻 Development Guide](docs/guides/development.md)** – Development workflow and contribution guide
- **[🌐 Online Documentation](https://neuraaak.github.io/ezcompiler/)** – Full documentation website

## 🧪 Testing

Comprehensive test suite with 233 test cases covering unit, integration, and robustness scenarios (~63% coverage).

```bash
# Install dev dependencies
pip install -e ".[dev]"

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
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting and formatting
ruff check .
ruff format --check .
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
| **ezpl**        | latest  | Structured logging framework  |

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

# Run full pipeline with DLP progress (version, compile, zip, upload)
compiler.run_pipeline(
    console=True,
    upload_structure="disk",
    upload_destination="./releases",
)

# Or call individual steps manually:
# compiler.generate_version_file()
# compiler.compile_project(compiler="Nuitka")
# compiler.zip_compiled_project()
# compiler.upload_to_repo(structure="disk", repo_path="./releases")
```

## 🛡️ Robustness

EzCompiler is designed for production use with comprehensive error handling:

- Full type hints for IDE support and static analysis
- Robust error handling with specific exceptions
- Automatic validation of configuration
- Cross-platform file operations
- Support for various file encodings and special characters

## 💻 CLI Usage

```bash
# Interactive project initialization
ezcompiler init

# Generate configuration
ezcompiler generate config \
  --project-name "MyApp" \
  --version "1.0.0" \
  --main-file "main.py"

# Generate setup.py
ezcompiler generate setup --config ezcompiler.yaml

# Generate version file
ezcompiler generate version --config ezcompiler.yaml

# Generate templates
ezcompiler generate template --type config --mockup
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
└── assets/templates/    # Template files (config, setup, version)
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

- Generate setup.py files for PyPI distribution
- Create Windows version information files
- Automate build workflows

### Project Management

- Centralized configuration via YAML/JSON files
- Customizable templates for file generation
- Integration into CI/CD pipelines

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. 🍴 Fork the project
2. 🌿 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔀 Open a Pull Request

## ⭐ Support

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **💡 Feature Requests**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **📚 Documentation**: [Complete Documentation](https://neuraaak.github.io/ezcompiler/)

## 📝 License

MIT License – See [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
- **PyPI Package**: [https://pypi.org/project/ezcompiler/](https://pypi.org/project/ezcompiler/)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Documentation**: [https://neuraaak.github.io/ezcompiler/](https://neuraaak.github.io/ezcompiler/)

---

**EzCompiler** – Professional Python project compilation and distribution. 🚀
