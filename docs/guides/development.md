# Development Guide

Development workflow and contribution guide for **EzCompiler**.

## Overview

This guide covers setting up a development environment, running tests, contributing code, and following project conventions.

---

## Development Setup

### Prerequisites

- **Python** >= 3.11
- **Git** for version control
- **pip** for package management

### Clone Repository

```bash
git clone https://github.com/neuraaak/ezcompiler.git
cd ezcompiler
```

### Install Development Dependencies

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install specific dependency groups
pip install -e ".[test]"  # Testing dependencies
pip install -e ".[docs]"  # Documentation dependencies
```

### Verify Installation

```bash
# Check installed version
python -c "import ezcompiler; print(ezcompiler.__version__)"

# Run tests
pytest tests/

# Build documentation
mkdocs serve
```

---

## Project Structure

```text
ezcompiler/
├── src/
│   └── ezcompiler/          # Main package
│       ├── __init__.py         # Package initialization
│       ├── types.py            # Public type aliases
│       ├── interfaces/         # Public interfaces
│       │   ├── python_api.py   # EzCompiler main class
│       │   └── cli_interface.py # CLI interface
│       ├── services/           # Business logic
│       │   ├── compiler_service.py
│       │   ├── config_service.py
│       │   ├── pipeline_service.py
│       │   ├── template_service.py
│       │   └── uploader_service.py
│       ├── adapters/           # Concrete implementations
│       │   ├── base_compiler.py
│       │   ├── compiler_factory.py
│       │   ├── cx_freeze_compiler.py
│       │   ├── pyinstaller_compiler.py
│       │   ├── nuitka_compiler.py
│       │   ├── base_file_writer.py
│       │   ├── disk_file_writer.py
│       │   ├── base_uploader.py
│       │   ├── disk_uploader.py
│       │   └── server_uploader.py
│       ├── shared/             # Shared components
│       │   ├── compilation_result.py
│       │   ├── compiler_config.py
│       │   └── exceptions/
│       ├── utils/              # Utilities
│       │   ├── file_utils.py
│       │   ├── config_utils.py
│       │   ├── template_utils.py
│       │   ├── zip_utils.py
│       │   └── validators/     # Validation modules
│       └── assets/             # Templates and resources
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
├── pyproject.toml         # Project metadata
├── README.md
└── LICENSE
```

---

## Code Standards

### Python Style

EzCompiler follows these coding standards:

- **PEP 8** - Python style guide
- **Type Hints** - Full type annotations for Python 3.11+
- **Docstrings** - Google-style docstrings for all public APIs
- **Line Length** - 88 characters (Ruff default)

### Type Hints

Use type hints for all functions and methods:

```python
from pathlib import Path

def process_files(
    files: list[Path],
    output_dir: Path,
    options: dict[str, str] | None = None,
) -> bool:
    """Process files and save to output directory.

    Args:
        files: List of files to process
        output_dir: Output directory path
        options: Optional processing options

    Returns:
        True if successful, False otherwise

    Raises:
        FileOperationError: If file processing fails
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def compile_project(
    self,
    compiler: str = "Cx_Freeze"
) -> bool:
    """Compile the project using the specified compiler.

    This method compiles the configured project using one of the
    supported compilers (Cx_Freeze, PyInstaller, or Nuitka).

    Args:
        compiler: Compiler name ("Cx_Freeze", "PyInstaller", "Nuitka")

    Returns:
        True if compilation succeeds, False otherwise

    Raises:
        CompilationError: If compilation fails
        ConfigurationError: If configuration is invalid

    Example:
        >>> ezcompiler = EzCompiler(config)
        >>> ezcompiler.compile_project(compiler="PyInstaller")
        True
    """
    ...
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_compiler_service.py

# Run with coverage
pytest tests/ --cov=ezcompiler

# Run with verbose output
pytest tests/ -v

# Run specific test type
pytest tests/unit/
pytest tests/integration/
```

### Writing Tests

Create tests in the `tests/` directory:

```python
# tests/unit/test_compiler_service.py

import pytest
from ezcompiler.services import CompilerService
from ezcompiler.shared import CompilerConfig

def test_compiler_service_initialization():
    """Test CompilerService initialization."""
    config = CompilerConfig(
        version="1.0.0",
        project_name="Test",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )
    service = CompilerService(config)
    assert service.config == config

def test_compiler_selection():
    """Test compiler selection logic."""
    config = CompilerConfig(
        version="1.0.0",
        project_name="Test",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
        compiler="PyInstaller"
    )
    service = CompilerService(config)
    compiler = service.get_compiler()
    assert compiler.name == "PyInstaller"
```

### Test Coverage

Target coverage is **60%** (threshold enforced in CI). Current coverage: **~64%**.

```bash
# Generate coverage report
pytest tests/ --cov=src/ezcompiler --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Linting and Formatting

### Ruff (Linting)

```bash
# Lint code
ruff check src/ezcompiler/ tests/

# Fix auto-fixable issues
ruff check --fix src/ezcompiler/ tests/
```

### Type Checking

Two type checkers are configured for complementary coverage:

```bash
# ty (fast, Astral — used in lint pipeline)
ty check src/ezcompiler/

# pyright (comprehensive static analysis)
pyright src/ezcompiler/
```

### Import Linter (Architecture Contracts)

```bash
# Verify layer dependency contracts
PYTHONPATH=src lint-imports
```

---

## Documentation

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### Writing Documentation

Documentation is in `docs/` directory:

- **User Guides** - `docs/guides/`
- **API Reference** - Auto-generated from docstrings
- **Examples** - `docs/examples/`
- **CLI Reference** - `docs/cli/`

### API Documentation

API documentation is auto-generated from docstrings using mkdocstrings:

```markdown
# api/services.md

## CompilerService

::: ezcompiler.services.compiler_service.CompilerService
```

---

## Contributing

### Contribution Workflow

1. **Fork the repository** on GitHub
2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/ezcompiler.git
   cd ezcompiler
   ```

3. **Create a feature branch**

   ```bash
   git checkout -b feature/my-feature
   ```

4. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

5. **Run tests**

   ```bash
   pytest tests/
   ```

6. **Lint and format**

   ```bash
   ruff format src/ezcompiler/ tests/
   ruff check --fix src/ezcompiler/ tests/
   ty check src/ezcompiler/
   pyright src/ezcompiler/
   PYTHONPATH=src lint-imports
   ```

7. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: Add amazing feature"
   ```

8. **Push to your fork**

   ```bash
   git push origin feature/my-feature
   ```

9. **Open a Pull Request** on GitHub

### Commit Message Convention

Use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Build/tooling changes

Examples:

```bash
git commit -m "feat: Add Nuitka compiler support"
git commit -m "fix: Handle missing config file gracefully"
git commit -m "docs: Update configuration guide"
git commit -m "test: Add tests for template service"
```

### Pull Request Guidelines

- Provide a clear description of changes
- Reference related issues
- Include tests for new features
- Update documentation
- Ensure all tests pass
- Follow code style guidelines

---

## Release Process

### Version Bumping

Update version in:

- `src/ezcompiler/__init__.py`
- `pyproject.toml`

### Creating a Release

1. **Update version**

   ```python
   # src/ezcompiler/__init__.py
   __version__ = "2.3.0"
   ```

2. **Update CHANGELOG**

   ```markdown
   ## [2.3.0] - 2024-01-15

   ### Added

   - New feature X
   - New feature Y

   ### Fixed

   - Bug fix A
   - Bug fix B
   ```

3. **Commit changes**

   ```bash
   git add .
   git commit -m "chore: Bump version to 2.3.0"
   ```

4. **Create tag**

   ```bash
   git tag v2.3.0
   git push origin v2.3.0
   ```

5. **Build and publish**

   ```bash
   python -m build
   python -m twine upload dist/*
   ```

---

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Reinstall in editable mode
pip install -e .
```

### Test Failures

If tests fail:

```bash
# Run with verbose output
pytest tests/ -v

# Run specific failing test
pytest tests/unit/test_specific.py::test_function -v
```

### Type Check Errors

If type checking reports errors, run the configured checkers:

```bash
# ty (fast, Astral)
ty check src/ezcompiler/

# pyright (comprehensive)
pyright src/ezcompiler/
```

---

## See Also

- [Getting Started](../getting-started.md) - Installation and basic usage
- [API Reference](../api/index.md) - Complete API documentation
- [Configuration Guide](configuration.md) - Configuration options
- [Examples](../examples/index.md) - Code examples

---

## Need Help?

- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neuraaak/ezcompiler/discussions)
- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)

---

**Thank you for contributing to EzCompiler!** 🙏
