# 📚 EzCompiler Documentation

Welcome to the **EzCompiler** documentation. This directory contains comprehensive guides and references for using the Python project compilation and distribution library.

## Quick Navigation

### 📖 Getting Started

Start here if you're new to EzCompiler:

- **[API Summary](api/SUMMARY.md)** – Quick overview of the main components and architecture
- **[Examples](examples/EXAMPLES.md)** – Practical usage examples for common scenarios

### 🔧 Detailed References

Comprehensive documentation for specific areas:

- **[Complete API Documentation](api/API_DOCUMENTATION.md)** – Full API reference with all classes, methods, and parameters
- **[CLI Documentation](cli/CLI_DOCUMENTATION.md)** – Command-line interface reference with all commands and options
- **[Configuration Guide](cli/CONFIG_GUIDE.md)** – How to configure EzCompiler with YAML and JSON files

### 🧪 Testing

Information about the test suite:

- **[Test Summary](tests/SUMMARY.md)** – Quick overview of test coverage and running tests
- **[Complete Test Documentation](tests/TEST_DOCUMENTATION.md)** – Detailed test suite structure and specifications

---

## Documentation Structure

```
docs/
├── README.md (this file)
├── api/
│   ├── SUMMARY.md                   # Quick API reference
│   └── API_DOCUMENTATION.md         # Complete API documentation
├── cli/
│   ├── CLI_DOCUMENTATION.md         # Command-line interface guide
│   └── CONFIG_GUIDE.md              # Configuration file guide
├── examples/
│   └── EXAMPLES.md                  # Usage examples
└── tests/
    ├── SUMMARY.md                   # Quick test overview
    └── TEST_DOCUMENTATION.md        # Complete test documentation
```

---

## Key Topics

### Installation

```bash
pip install ezcompiler
```

### Quick Start

```python
from ezcompiler import EzCompiler

# Create compiler
ezcompiler = EzCompiler()

# Initialize project
ezcompiler.init_project(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Compile
ezcompiler.compile_project(compiler="PyInstaller")
```

### Main Components

- **EzCompiler** – Main facade class for orchestrating the entire process
- **CompilerConfig** – Configuration dataclass for all compilation settings
- **Compilers** – CxFreezeCompiler and PyInstallerCompiler implementations
- **Generators** – VersionGenerator and SetupGenerator for file creation
- **Templates** – Template system for dynamic content generation
- **Uploaders** – DiskUploader and ServerUploader for distribution
- **Utils** – Utility classes for file, validation, and ZIP operations

### Common Use Cases

#### Simple Console Application

```bash
ezcompiler init
ezcompiler generate config --project-name "MyApp" --main-file "main.py"
ezcompiler generate setup --config ezcompiler.yaml
```

#### Build and Distribute

```python
ezcompiler.compile_project(compiler="PyInstaller")
ezcompiler.zip_compiled_project()
ezcompiler.upload_to_repo(structure="disk", repo_path="./releases")
```

#### CI/CD Integration

See [CI/CD Integration Examples](examples/EXAMPLES.md#cicd-integration) for GitHub Actions, GitLab CI, and other integration examples.

---

## Documentation by Format

### YAML Configuration

EzCompiler uses YAML for human-readable configuration:

```yaml
version: "1.0.0"
project_name: "MyProject"
main_file: "main.py"
output_folder: "dist"
packages:
  - "requests"
  - "pandas"
excludes:
  - "debugpy"
  - "test"
```

See [Configuration Guide](cli/CONFIG_GUIDE.md) for details.

### JSON Configuration

JSON is also supported for programmatic configuration:

```json
{
  "version": "1.0.0",
  "project_name": "MyProject",
  "main_file": "main.py",
  "output_folder": "dist",
  "packages": ["requests", "pandas"]
}
```

### CLI Commands

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

See [CLI Documentation](cli/CLI_DOCUMENTATION.md) for complete reference.

---

## Type Safety and IDE Support

EzCompiler is fully type-hinted for better IDE support:

```python
from ezcompiler import EzCompiler, CompilerConfig, Config, Compiler

# Type hints enable autocompletion
ezcompiler: EzCompiler = EzCompiler()
config: Config = ezcompiler.config  # CompilerConfig
```

---

## API Overview

### Main Classes

- `ezcompiler.EzCompiler` – Main facade class
- `ezcompiler.core.compiler_config.CompilerConfig` – Configuration dataclass
- `ezcompiler.compilers.base_compiler.BaseCompiler` – Abstract compiler base
- `ezcompiler.compilers.CxFreezeCompiler` – Cx_Freeze implementation
- `ezcompiler.compilers.PyInstallerCompiler` – PyInstaller implementation
- `ezcompiler.generators.VersionGenerator` – Version file generator
- `ezcompiler.generators.SetupGenerator` – Setup file generator
- `ezcompiler.templates.TemplateManager` – Template system manager
- `ezcompiler.uploaders.base.BaseUploader` – Abstract uploader base
- `ezcompiler.uploaders.DiskUploader` – Local disk uploader
- `ezcompiler.uploaders.ServerUploader` – HTTP/HTTPS uploader

### Exceptions

All custom exceptions inherit from `EzCompilerError`:

- `CompilationError` – Compilation failures
- `ConfigurationError` – Configuration issues
- `TemplateError` – Template processing errors
- `VersionError` – Version generation errors
- `UploadError` – Upload failures
- `ValidationError` – Validation errors

---

## Best Practices

### 1. Configuration Management

Always use configuration files for version control:

```python
import yaml
from ezcompiler import CompilerConfig

with open("ezcompiler.yaml") as f:
    config = CompilerConfig.from_dict(yaml.safe_load(f))
```

### 2. Error Handling

Always catch specific exceptions:

```python
from ezcompiler.core.exceptions import CompilationError, ConfigurationError

try:
    ezcompiler.compile_project()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CompilationError as e:
    print(f"Compilation failed: {e}")
```

### 3. Logging Integration

Use the integrated logging system:

```python
ezcompiler = EzCompiler(log_level="DEBUG")
printer = ezcompiler.printer
logger = ezcompiler.logger

printer.info("Starting build...")
logger.debug("Debug information")
```

### 4. Testing

Write comprehensive tests:

```bash
# Run all tests
pytest tests/

# Run specific test type
pytest tests/unit/
pytest tests/integration/

# With coverage
pytest --cov=ezcompiler tests/
```

---

## Advanced Topics

### Custom Compiler Selection

```python
ezcompiler.compile_project(compiler="PyInstaller")  # Single file
ezcompiler.compile_project(compiler="Cx_Freeze")    # Directory
```

### Template Processing

```python
from ezcompiler.templates import TemplateManager

manager = TemplateManager()
content = manager.process_template("config.yaml", {
    "PROJECT_NAME": "MyApp",
    "VERSION": "1.0.0",
})
```

### Distribution Workflows

```python
# Multi-step distribution
ezcompiler.compile_project()
ezcompiler.zip_compiled_project()
ezcompiler.upload_to_repo(structure="disk", repo_path="./releases")
```

---

## Resources

- **[GitHub Repository](https://github.com/example/ezcompiler)** – Source code
- **[Issue Tracker](https://github.com/example/ezcompiler/issues)** – Report bugs
- **[Discussion Forum](https://github.com/example/ezcompiler/discussions)** – Ask questions

---

## Support

For issues or questions:

1. Check the [Examples](examples/EXAMPLES.md) for common use cases
2. Review the [API Documentation](api/API_DOCUMENTATION.md)
3. Check the [FAQ](#faq) section below
4. Open an issue on GitHub

---

## FAQ

### Which compiler should I use?

- **PyInstaller** – Single-file executables, simpler distribution
- **Cx_Freeze** – Directory-based, better performance for large apps

### How do I include data files?

Use the `include_files` configuration:

```yaml
include_files:
  files:
    - "config.yaml"
    - "data.json"
  folders:
    - "assets"
    - "templates"
```

### How do I exclude development packages?

Use the `excludes` configuration:

```yaml
excludes:
  - "debugpy"
  - "test"
  - "pytest"
  - "mypy"
```

### Can I use EzCompiler in CI/CD?

Yes! See [CI/CD Integration Examples](examples/EXAMPLES.md#cicd-integration).

---

**EzCompiler Documentation** – Professional Python project compilation and distribution.
