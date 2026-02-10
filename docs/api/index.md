# API Reference

Complete API reference for **EzCompiler** framework.

## Overview

The EzCompiler API provides a comprehensive framework for Python project compilation and distribution. The framework is organized into **4 main layers** with complete type hints, Google-style docstrings, and extensive error handling.

## Quick Reference

| Component                   | Description                            | Documentation                     |
| --------------------------- | -------------------------------------- | --------------------------------- |
| [Interfaces](interfaces.md) | Public APIs and user-facing interfaces | Main facade and CLI               |
| [Services](services.md)     | Business logic and orchestration       | Core service implementations      |
| [Protocols](protocols.md)   | Compiler and uploader implementations  | Protocol adapters and backends    |
| [Shared](shared.md)         | Configuration and exceptions           | Shared data structures            |
| [Utils](utils.md)           | Utility functions and validators       | File, config, template operations |

## Import Examples

The main classes can be imported directly from the package:

```python
from ezcompiler import EzCompiler, CompilerConfig
```

Or from submodules:

```python
from ezcompiler.interfaces import EzCompiler
from ezcompiler.shared import CompilerConfig
from ezcompiler.services import CompilerService
from ezcompiler.protocols import CxFreezeCompiler
```

---

## Architecture Layers

### Interfaces Layer

The interfaces layer provides user-facing APIs:

- **`EzCompiler`** – Main facade class that orchestrates the entire compilation workflow
- **`CLIInterface`** – Interactive command-line interface with rich formatting

[View Interfaces Documentation →](interfaces.md)

### Services Layer

The services layer implements business logic and orchestration:

- **`CompilerService`** – Manages compiler selection and compilation process
- **`ConfigService`** – Handles configuration loading and validation
- **`TemplateService`** – Processes templates and generates files
- **`UploaderService`** – Orchestrates upload operations

[View Services Documentation →](services.md)

### Protocols Layer

The protocols layer defines implementation protocols:

**Compilers:**

- **`BaseCompiler`** – Abstract base class for all compilers
- **`CxFreezeCompiler`** – Cx_Freeze implementation
- **`PyInstallerCompiler`** – PyInstaller implementation
- **`NuitkaCompiler`** – Nuitka implementation

**Uploaders:**

- **`BaseUploader`** – Abstract base class for all uploaders
- **`DiskUploader`** – Local disk upload backend
- **`ServerUploader`** – HTTP/HTTPS server upload backend

[View Protocols Documentation →](protocols.md)

### Shared Layer

The shared layer contains common data structures and exceptions:

- **`CompilerConfig`** – Main configuration dataclass
- **Exception hierarchy** – Typed exceptions for error handling

[View Shared Documentation →](shared.md)

### Utils Layer

The utils layer provides utility functions and validators:

- **`FileUtils`** – File operations and management
- **`ConfigUtils`** – Configuration parsing (YAML/JSON)
- **`TemplateUtils`** – Template processing
- **`ZipUtils`** – ZIP archive operations
- **`Validators`** – 9 specialized validation modules

[View Utils Documentation →](utils.md)

---

## API Design Principles

### Type Safety

EzCompiler provides complete type hints for all public APIs:

- **Full type annotations** – Python 3.10+ type hints throughout
- **IDE support** – Excellent auto-completion and error detection
- **Type checking** – Compatible with mypy, pyright, and other type checkers
- **Runtime validation** – Type hints used for parameter validation

```python
from ezcompiler import EzCompiler, CompilerConfig

# Type-safe configuration
config: CompilerConfig = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Type-safe compiler
ezcompiler: EzCompiler = EzCompiler(config)
```

### Error Handling

Comprehensive exception hierarchy for granular error handling:

```python
from ezcompiler import EzCompiler
from ezcompiler.shared.exceptions import (
    CompilationError,
    ConfigurationError,
    TemplateError,
    UploadError
)

try:
    ezcompiler = EzCompiler(config)
    ezcompiler.compile_project()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CompilationError as e:
    print(f"Compilation failed: {e}")
except TemplateError as e:
    print(f"Template error: {e}")
```

### Configuration Management

Flexible configuration with YAML/JSON support:

```python
from ezcompiler import CompilerConfig
import yaml

# From dictionary
config = CompilerConfig.from_dict({
    "version": "1.0.0",
    "project_name": "MyApp",
    "main_file": "main.py",
    "include_files": {"files": [], "folders": []},
    "output_folder": "dist",
})

# From YAML file
with open("ezcompiler.yaml") as f:
    config_dict = yaml.safe_load(f)
    config = CompilerConfig.from_dict(config_dict)
```

### Template System

Dynamic file generation with template processing:

```python
from ezcompiler.services import TemplateService

template_service = TemplateService()
content = template_service.process_template(
    template_name="config.yaml",
    variables={"PROJECT_NAME": "MyApp", "VERSION": "1.0.0"}
)
```

---

## Quick Start Example

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

# Package and upload
ezcompiler.zip_compiled_project()
ezcompiler.upload_to_repo(structure="disk", repo_path="./releases")
```

---

## Installation

```bash
pip install ezcompiler
```

For development installation:

```bash
git clone https://github.com/neuraaak/ezcompiler.git
cd ezcompiler
pip install -e ".[dev]"
```

---

## Detailed Documentation

Select a module from the navigation menu or the table above to view detailed documentation with:

- Complete class and method signatures
- Parameter descriptions
- Return value documentation
- Exception specifications
- Usage examples
- Type annotations

## Module Documentation

| Module                      | Description                                        |
| --------------------------- | -------------------------------------------------- |
| [Interfaces](interfaces.md) | Public APIs and user-facing interfaces             |
| [Services](services.md)     | Business logic services and orchestration          |
| [Protocols](protocols.md)   | Compiler and uploader protocol implementations     |
| [Shared](shared.md)         | Configuration dataclasses and exception hierarchy  |
| [Utils](utils.md)           | Utility functions, file operations, and validators |

---

## Need Help?

- **Quick Start**: See [Getting Started](../getting-started.md)
- **Examples**: Check out [Examples](../examples/index.md)
- **Guides**: Read [User Guides](../guides/index.md)
- **CLI**: View [CLI Reference](../cli/index.md)
- **Issues**: Report bugs on [GitHub](https://github.com/neuraaak/ezcompiler/issues)
