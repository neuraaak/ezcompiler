# 🚀 EzCompiler

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgray.svg?style=for-the-badge&logo=windows)](https://pypi.org/project/ezcompiler/)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)
[![PyPI](https://img.shields.io/badge/PyPI-ezcompiler-green.svg?style=for-the-badge&logo=pypi)](https://pypi.org/project/ezcompiler/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)
[![Tests](https://img.shields.io/badge/Tests-150%2B%20passing-success.svg?style=for-the-badge)](https://github.com/neuraaak/ezcompiler)

**EzCompiler** is a professional Python library for compiling projects into executable files with automatic version management, packaging, and distribution. It provides a unified interface for multiple compilers (Cx_Freeze, PyInstaller) with modular architecture and complete type hints.

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

# Generate supporting files
compiler.generate_version_file()
compiler.generate_setup_file("setup.py")

# Compile project
compiler.compile_project(compiler="PyInstaller")

# Create distribution
compiler.zip_compiled_project()
compiler.upload_to_repo(structure="disk", repo_path="./releases")
```

## 🎯 Key Features

- **✅ Multi-Compiler Support**: CxFreezeCompiler and PyInstallerCompiler with unified interface
- **✅ Automatic File Generation**: Version files, setup.py, and configuration from templates
- **✅ Template System**: Flexible file generation based on customizable templates
- **✅ Packaging**: Automatic ZIP archive creation for distribution
- **✅ Distribution**: Upload support for local disk and remote HTTP/HTTPS servers
- **✅ Configuration Management**: Centralized configuration with automatic validation
- **✅ Structured Logging**: Integration with Ezpl for professional logging
- **✅ Full Type Hints**: Complete typing support for IDEs and linters

## 📚 Documentation

- **[📖 Complete API Documentation](docs/api/API_DOCUMENTATION.md)** – Full API reference with examples
- **[📋 API Summary](docs/api/SUMMARY.md)** – Quick API overview
- **[🖥️ CLI Documentation](docs/cli/CLI_DOCUMENTATION.md)** – Command-line interface guide
- **[⚙️ Configuration Guide](docs/cli/CONFIG_GUIDE.md)** – Configuration management
- **[💡 Examples](docs/examples/EXAMPLES.md)** – Usage examples and demonstrations
- **[🧪 Test Documentation](docs/tests/TEST_DOCUMENTATION.md)** – Complete test suite documentation
- **[📊 Test Summary](docs/tests/SUMMARY.md)** – Quick test overview

## 🧪 Testing

Comprehensive test suite with 150+ test cases covering unit, integration, and robustness scenarios.

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

See **[Test Documentation](docs/tests/TEST_DOCUMENTATION.md)** for complete details.

## 🛠️ Development Setup

For contributors and developers:

```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting and formatting
ruff check .
black --check .
mypy ezcompiler/
```

## 🎨 Main Components

- **`EzCompiler`**: Main facade class for orchestrating the entire compilation process
- **`CompilerConfig`**: Centralized configuration management
- **`BaseCompiler`**: Abstract base class for compiler implementations
- **`CxFreezeCompiler`**: Cx_Freeze compiler implementation
- **`PyInstallerCompiler`**: PyInstaller compiler implementation
- **`VersionGenerator`**: Windows version information file generator
- **`SetupGenerator`**: Setup.py file generator
- **`TemplateManager`**: Template system manager
- **`BaseUploader`**: Abstract base class for uploaders
- **`DiskUploader`**: Local disk uploader
- **`ServerUploader`**: HTTP/HTTPS uploader

## 📦 Dependencies

| Package         | Version | Description                   |
| --------------- | ------- | ----------------------------- |
| **cx_Freeze**   | 7.1.0+  | Python to executable compiler |
| **PyInstaller** | 6.10.0+ | Python to executable compiler |
| **InquirerPy**  | 0.3.4+  | Interactive CLI interface     |
| **requests**    | 2.32.3+ | HTTP library for uploads      |
| **PyYAML**      | 6.0+    | YAML file processing          |
| **click**       | 8.0.0+  | CLI framework                 |
| **ezpl**        | 1.4.0+  | Structured logging framework  |

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

# Generate files
compiler.generate_version_file()
compiler.generate_setup_file("setup.py")

# Compile
compiler.compile_project(compiler="PyInstaller")

# Distribute
compiler.zip_compiled_project()
compiler.upload_to_repo(structure="disk", repo_path="./releases")

# Access components
logger = compiler.logger
printer = compiler.printer
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

See **[CLI Documentation](docs/cli/CLI_DOCUMENTATION.md)** for complete reference.

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

compiler: "PyInstaller"
console: true
zip_needed: true
```

See **[Configuration Guide](docs/cli/CONFIG_GUIDE.md)** for detailed configuration options.

## 📊 Architecture

```txt
ezcompiler/
├── core/                 # Configuration and exceptions
├── compilers/           # Compiler implementations
├── generators/          # File generators
├── templates/           # Template system
├── uploaders/           # Distribution uploaders
├── utils/              # Utility functions
├── cli.py              # Command-line interface
├── ezcompiler.py       # Main facade class
└── helper.py           # Helper functions
```

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
- **📚 Documentation**: [Complete API Docs](docs/api/API_DOCUMENTATION.md)

## 📝 License

MIT License – See [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Documentation**: [Complete Documentation](docs/README.md)

---

**EzCompiler** – Professional Python project compilation and distribution. 🚀
