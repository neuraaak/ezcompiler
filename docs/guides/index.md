# User Guides

In-depth guides and tutorials for **EzCompiler** framework.

## Overview

This section provides comprehensive guides for mastering EzCompiler features and best practices. Whether you're just getting started or looking to contribute to the project, you'll find detailed documentation here.

## Available Guides

| Guide                                   | Description                                       | Level        |
| --------------------------------------- | ------------------------------------------------- | ------------ |
| [Configuration Guide](configuration.md) | Detailed configuration options and best practices | Beginner     |
| [Development Guide](development.md)     | Development workflow and contribution guide       | Intermediate |

## Quick Links

### For Beginners

- [Getting Started](../getting-started.md) - Start here if you're new to EzCompiler
- [Basic Examples](../examples/index.md) - Simple usage examples
- [Configuration Guide](configuration.md) - Learn to configure your projects

### For Developers

- [Development Guide](development.md) - Set up your development environment
- [API Reference](../api/index.md) - Complete API documentation

### For Advanced Users

- [API Reference](../api/index.md) - Detailed module documentation
- [CLI Reference](../cli/index.md) - Command-line interface usage
- [GitHub Repository](https://github.com/neuraaak/ezcompiler) - Source code and issues

## Topics

### Core Concepts

- **Compilation Backends** - Understanding Cx_Freeze, PyInstaller, and Nuitka compilers
- **Configuration Management** - YAML and JSON configuration files
- **Template System** - Dynamic file generation with templates
- **Upload Backends** - Distribution to disk and HTTP servers

### Framework Features

- **Type Safety** - Using Python 3.11+ type hints for better IDE support
- **Error Handling** - Comprehensive exception hierarchy
- **Validation** - 9 specialized validation modules
- **Logging** - Integrated logging and debugging

### Integration

- **Application Integration** - Integrating EzCompiler into your build workflows
- **CI/CD Integration** - GitHub Actions, GitLab CI, and other platforms
- **Template Customization** - Creating custom templates
- **Custom Compilers** - Extending the compiler protocol

### Best Practices

- **Project Structure** - Organizing your project for compilation
- **Performance** - Optimizing compilation and package size
- **Error Handling** - Robust error handling in build scripts
- **Testing** - Testing compiled applications

## Development Workflow

### Setting Up

1. **Clone the repository**

   ```bash
   git clone https://github.com/neuraaak/ezcompiler.git
   cd ezcompiler
   ```

2. **Install in development mode**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks** (if available)

   ```bash
   pre-commit install
   ```

See the [Development Guide](development.md) for detailed setup instructions.

### Testing

Run the test suite to ensure everything works:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=ezcompiler

# Run specific test types
pytest tests/unit/
pytest tests/integration/
```

### Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with tests
4. **Run tests and linting** (`pytest`, `ruff check`)
5. **Commit your changes** with conventional commits
6. **Push to your fork** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request** on GitHub

See the [Development Guide](development.md) for contribution guidelines.

## Code Style

EzCompiler follows these coding standards:

- **PEP 8** - Python style guide
- **Type Hints** - Full type annotations for Python 3.11+
- **Docstrings** - Google-style docstrings for all public APIs
- **Testing** - Comprehensive test coverage
- **Black** - Code formatting (88 character line length)
- **Ruff** - Linting and code quality

## Documentation

### Building Docs

Build the documentation locally:

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve locally
mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### Writing Docs

Documentation is written in Markdown and built with MkDocs Material:

- **Guides** - Located in `docs/guides/`
- **API Reference** - Auto-generated from docstrings with mkdocstrings
- **Examples** - Code examples in `docs/examples/`
- **CLI** - Command-line interface docs in `docs/cli/`

## See Also

- [Getting Started](../getting-started.md) - Quick start guide
- [API Reference](../api/index.md) - Complete API documentation
- [Examples](../examples/index.md) - Practical code examples
- [CLI Reference](../cli/index.md) - Command-line interface

## Need Help?

- **Issues**: [GitHub Issues](https://github.com/neuraaak/ezcompiler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neuraaak/ezcompiler/discussions)
- **Repository**: [https://github.com/neuraaak/ezcompiler](https://github.com/neuraaak/ezcompiler)

---

**Happy building with EzCompiler!** 🚀
