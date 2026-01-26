# Complete API Documentation – EzCompiler

## Overview

This documentation presents all the components available in the **EzCompiler** library, organized by functional modules. Each component is designed to offer specialized functionality while ensuring API and design consistency.

## Table of Contents

- [Complete API Documentation – EzCompiler](#complete-api-documentation--ezcompiler)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [🧠 Main Module (`ezcompiler`)](#-main-module-ezcompiler)
    - [Class EzCompiler](#class-ezcompiler)
      - [Initialization](#initialization)
      - [Getters](#getters)
      - [Project Initialization](#project-initialization)
      - [File Generation](#file-generation)
      - [Compilation](#compilation)
      - [Distribution](#distribution)
    - [CompilerConfig](#compilerconfig)
      - [Required Fields](#required-fields)
      - [Optional Fields](#optional-fields)
      - [Compilation Fields](#compilation-fields)
      - [Upload Fields](#upload-fields)
      - [Advanced Fields](#advanced-fields)
      - [Methods](#methods)
    - [BaseCompiler](#basecompiler)
    - [CxFreezeCompiler](#cxfreezecompiler)
    - [PyInstallerCompiler](#pyinstallercompiler)
    - [VersionGenerator](#versiongenerator)
    - [SetupGenerator](#setupgenerator)
    - [TemplateManager](#templatemanager)
    - [TemplateProcessor](#templateprocessor)
    - [BaseUploader](#baseuploader)
    - [DiskUploader](#diskuploader)
    - [ServerUploader](#serveruploader)
    - [UploaderFactory](#uploaderfactory)
    - [Utility Classes](#utility-classes)
    - [Exceptions](#exceptions)
  - [🧪 Usage Examples](#-usage-examples)
    - [Basic Usage](#basic-usage)
    - [Configuration from Files](#configuration-from-files)
    - [Advanced Compilation](#advanced-compilation)
    - [Distribution and Upload](#distribution-and-upload)
    - [Template Generation](#template-generation)
    - [Type Hints for Better IDE Support](#type-hints-for-better-ide-support)
  - [🎯 Best Practices](#-best-practices)
    - [Type Safety](#type-safety)
    - [Configuration](#configuration)
    - [Compilation](#compilation-1)
    - [Error Handling](#error-handling)
    - [Testing](#testing)
    - [Performance](#performance)
  - [📝 Type Reference](#-type-reference)
    - [Type Aliases](#type-aliases)
    - [Return Types](#return-types)

---

## 🧠 Main Module (`ezcompiler`)

### Class EzCompiler

**File:** `ezcompiler/ezcompiler.py`

The main entry point of the library. Provides a facade for orchestrating the entire compilation and distribution process.

**Type Hints:**

```python
from ezcompiler import EzCompiler, CompilerConfig
from ezcompiler import Config, Compiler  # Type aliases

ezcompiler = EzCompiler()
config: Config = ezcompiler.config  # Type: CompilerConfig
```

**Main methods:**

#### Initialization

- `EzCompiler(
    log_rotation: str = "10 MB",
    log_level: str = "INFO",
) -> EzCompiler`: Creates an EzCompiler instance

**Parameters:**

- `log_rotation`: Log file rotation setting (e.g., "10 MB", "1 day")
- `log_level`: Log level for the internal logger (DEBUG, INFO, WARNING, ERROR)

**Behavior:**

- Creates an internal `Ezpl` instance for logging and printing
- Initializes `VersionGenerator` and `SetupGenerator` instances
- Initializes compiler state to `None` (created on demand)
- Configures internal state (`_compiler_choice`, `_zip_needed`)

#### Getters

- `logger -> EzLogger`: Returns the internal logger instance for file logging
- `printer -> EzPrinter`: Returns the internal printer instance for console output
- `ezpl -> Ezpl`: Returns the internal Ezpl instance
- `config -> CompilerConfig`: Returns the current compilation configuration

#### Project Initialization

- `init_project(
    version: str,
    project_name: str,
    main_file: str,
    include_files: dict[str, list[str]],
    output_folder: Path | str,
    **kwargs
) -> None`: Initialize a project with all required configuration

**Parameters:**

- `version`: Project version string (e.g., "1.0.0")
- `project_name`: Name of the project
- `main_file`: Main Python file to compile
- `include_files`: Dictionary with keys "files" and "folders" listing files/folders to include
- `output_folder`: Output directory for compiled files
- `**kwargs`: Additional configuration options (company_name, project_description, author, icon, etc.)

**Example:**

```python
from ezcompiler import EzCompiler

ezcompiler = EzCompiler()
ezcompiler.init_project(
    version="1.0.0",
    project_name="MyProject",
    main_file="main.py",
    include_files={"files": ["config.yaml"], "folders": ["assets"]},
    output_folder="dist",
    company_name="MyCompany",
    project_description="My awesome project",
)
```

#### File Generation

- `generate_version_file(name: str = "version_info.txt") -> None`: Generate a version info file
- `generate_setup_file(file_path: Path | str) -> None`: Generate a setup.py file

**Example:**

```python
ezcompiler.init_project(...)
ezcompiler.generate_version_file("version_info.txt")
ezcompiler.generate_setup_file("setup.py")
```

#### Compilation

- `compile_project(console: bool = True, compiler: str | None = None) -> None`: Compile the project

**Parameters:**

- `console`: Whether to show console window (True for console apps, False for GUI)
- `compiler`: Compiler to use ("PyInstaller", "Cx_Freeze", or None for interactive/auto)

**Compiler Selection:**

- If `compiler` is specified, uses that compiler directly
- If `None`, checks for command-line arguments (`-cxf` or `-pyi`)
- If no arguments, prompts interactively via `InquirerPy`

**ZIP Requirement:**

- `Cx_Freeze`: `_zip_needed = True` (directory-based output)
- `PyInstaller` (onefile): `_zip_needed = False` (single file output)

**Example:**

```python
ezcompiler.init_project(...)
ezcompiler.compile_project(console=True, compiler="PyInstaller")
# Or interactive selection:
ezcompiler.compile_project(console=False)
```

#### Distribution

- `zip_compiled_project() -> None`: Create a ZIP archive of the compiled project
- `upload_to_repo(
    structure: Literal["server", "disk"],
    repo_path: Path | str,
    upload_config: dict[str, Any] | None = None
) -> None`: Upload the compiled project to a repository

**Example:**

```python
ezcompiler.init_project(...)
ezcompiler.compile_project(...)
ezcompiler.zip_compiled_project()
ezcompiler.upload_to_repo(
    structure="disk",
    repo_path="./releases",
    upload_config={"preserve_permissions": True}
)
```

---

### CompilerConfig

**File:** `ezcompiler/core/compiler_config.py`

Dataclass for managing all project compilation configuration.

**Type Hints:**

```python
from ezcompiler import CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyProject",
    main_file="main.py",
    output_folder="dist",
)
```

#### Required Fields

- `version: str`: Project version (e.g., "1.0.0")
- `project_name: str`: Project name
- `main_file: str`: Main Python file to compile
- `output_folder: str`: Output directory for compiled files

#### Optional Fields

- `project_description: str = ""`: Project description
- `company_name: str = ""`: Company name
- `author: str = ""`: Author name
- `icon: str | None = None`: Path to icon file
- `version_file: str = "version_info.txt"`: Version file name

#### Compilation Fields

- `include_files: dict[str, list[str]]`: Files and folders to include
- `packages: list[str]`: Packages to include
- `includes: list[str]`: Modules to include explicitly
- `excludes: list[str]`: Modules to exclude
- `console: bool = True`: Show console window
- `compiler: str = "auto"`: Compiler choice ("auto", "PyInstaller", "Cx_Freeze")
- `optimize: bool = True`: Enable optimization
- `strip: bool = False`: Strip symbols
- `debug: bool = False`: Debug mode

#### Upload Fields

- `zip_needed: bool = True`: Create ZIP archive
- `repo_needed: bool = False`: Upload to repository
- `upload_structure: str = "disk"`: Upload structure ("disk", "server")
- `repo_path: str = "releases"`: Repository path
- `server_url: str | None = None`: Server URL for upload

#### Advanced Fields

- `extra_options: dict[str, Any]`: Extra compiler-specific options

#### Methods

- `validate() -> None`: Validate configuration (called in `__post_init__`)
- `to_dict() -> dict[str, Any]`: Convert configuration to dictionary
- `from_dict(data: dict[str, Any]) -> CompilerConfig`: Create from dictionary (classmethod)
- `output_path -> Path`: Property returning the output folder as Path
- `version_tuple -> tuple[int, ...]`: Property returning version as tuple

**Example:**

```python
from ezcompiler import CompilerConfig

# Create from parameters
config = CompilerConfig(
    version="1.0.0",
    project_name="MyProject",
    main_file="main.py",
    output_folder="dist",
    company_name="MyCompany",
    packages=["requests", "pandas"],
    excludes=["debugpy", "test"],
)

# Create from dictionary
config_dict = config.to_dict()
config2 = CompilerConfig.from_dict(config_dict)

# Access properties
print(config.output_path)  # Path("dist")
print(config.version_tuple)  # (1, 0, 0)
```

---

### BaseCompiler

**File:** `ezcompiler/compilers/base_compiler.py`

Abstract base class for all compiler implementations.

**Main attributes:**

- `config: CompilerConfig`: Compilation configuration
- `_zip_needed: bool`: Whether ZIP archive is needed after compilation

**Abstract methods:**

- `compile() -> None`: Execute compilation (must be implemented by subclasses)
- `get_compiler_name() -> str`: Return compiler name (must be implemented by subclasses)

**Properties:**

- `zip_needed -> bool`: Whether ZIP archive is needed

**Helper methods:**

- `_validate_config() -> None`: Validate configuration before compilation
- `_prepare_output_dir() -> None`: Prepare output directory
- `_log_info(message: str) -> None`: Log info message
- `_log_error(message: str) -> None`: Log error message

---

### CxFreezeCompiler

**File:** `ezcompiler/compilers/cx_freeze_compiler.py`

Cx_Freeze compiler implementation. Creates directory-based executables.

**Characteristics:**

- `_zip_needed = True` (always creates directory output)
- Better performance for large applications
- Supports complex dependencies

**Example:**

```python
from ezcompiler.compilers import CxFreezeCompiler
from ezcompiler import CompilerConfig

config = CompilerConfig(...)
compiler = CxFreezeCompiler(config)
compiler.compile()
```

---

### PyInstallerCompiler

**File:** `ezcompiler/compilers/pyinstaller_compiler.py`

PyInstaller compiler implementation. Creates single-file executables.

**Characteristics:**

- `_zip_needed = False` (creates single file in onefile mode)
- Simpler distribution (single executable)
- Smaller file size for simple applications

**Example:**

```python
from ezcompiler.compilers import PyInstallerCompiler
from ezcompiler import CompilerConfig

config = CompilerConfig(...)
compiler = PyInstallerCompiler(config)
compiler.compile()
```

---

### VersionGenerator

**File:** `ezcompiler/generators/version_generator.py`

Generator for Windows version information files.

**Main methods:**

- `generate(config: dict[str, Any], output_path: Path | None = None) -> str`: Generate version file content
- `generate_to_file(config: dict[str, Any], output_path: Path) -> None`: Generate and write version file

**Template Variables:**

- `#VERSION#`: Full version string (e.g., "1.0.0")
- `#VERSION_TUPLE#`: Version as tuple (e.g., "(1, 0, 0, 0)")
- `#COMPANY_NAME#`: Company name
- `#PROJECT_NAME#`: Project name
- `#PROJECT_DESCRIPTION#`: Project description
- `#FILE_VERSION#`: File version string

**Example:**

```python
from ezcompiler.generators import VersionGenerator

generator = VersionGenerator()
content = generator.generate({
    "version": "1.0.0",
    "project_name": "MyProject",
    "company_name": "MyCompany",
    "project_description": "My awesome project",
})
```

---

### SetupGenerator

**File:** `ezcompiler/generators/setup_generator.py`

Generator for `setup.py` files.

**Main methods:**

- `generate_from_config(config: dict[str, Any], output_dir: Path | None = None) -> str`: Generate setup.py content
- `generate_to_file(config: dict[str, Any], output_path: Path) -> None`: Generate and write setup.py file

**Template Variables:**

- `#PROJECT_NAME#`: Project name
- `#VERSION#`: Version string
- `#AUTHOR#`: Author name
- `#COMPANY_NAME#`: Company name
- `#PROJECT_DESCRIPTION#`: Project description
- `#MAIN_FILE#`: Main file path
- `#ICON#`: Icon file path
- `#INCLUDE_FILES#`: Files to include (formatted list)
- `#PACKAGES#`: Packages to include
- `#INCLUDES#`: Modules to include
- `#EXCLUDES#`: Modules to exclude

**Example:**

```python
from ezcompiler.generators import SetupGenerator

generator = SetupGenerator()
content = generator.generate_from_config({
    "version": "1.0.0",
    "project_name": "MyProject",
    "main_file": "main.py",
    "packages": ["requests", "pandas"],
})
```

---

### TemplateManager

**File:** `ezcompiler/templates/template_manager.py`

Manager for loading and processing EzCompiler templates.

**Main methods:**

- `load_template(template_name: str) -> str`: Load a template file by name
- `get_template_path(template_name: str) -> Path`: Get the full path to a template
- `list_templates() -> list[str]`: List all available templates
- `process_template(template_name: str, variables: dict[str, str]) -> str`: Load and process a template

**Available Templates:**

- `config.yaml`: YAML configuration template
- `config.json`: JSON configuration template
- `setup.py`: Setup file template
- `version_info.txt`: Version information template

**Example:**

```python
from ezcompiler.templates import TemplateManager

manager = TemplateManager()
templates = manager.list_templates()
content = manager.process_template("config.yaml", {
    "PROJECT_NAME": "MyProject",
    "VERSION": "1.0.0",
})
```

---

### TemplateProcessor

**File:** `ezcompiler/templates/template_utils.py`

Utility for processing templates with variable substitution.

**Main methods:**

- `substitute(template: str, variables: dict[str, str]) -> str`: Substitute variables in template
- `generate_mockup(template_type: str) -> str`: Generate template with example values
- `validate_template(template: str, required_vars: list[str]) -> bool`: Validate template has all required variables

**Variable Format:**

Variables use the format `#VARIABLE_NAME#` for substitution.

**Example:**

```python
from ezcompiler.templates import TemplateProcessor

processor = TemplateProcessor()
result = processor.substitute(
    "Project: #PROJECT_NAME# v#VERSION#",
    {"PROJECT_NAME": "MyProject", "VERSION": "1.0.0"}
)
# Result: "Project: MyProject v1.0.0"
```

---

### BaseUploader

**File:** `ezcompiler/uploaders/base.py`

Abstract base class for all uploader implementations.

**Main attributes:**

- `source_path: Path`: Source file/directory to upload
- `destination_path: Path`: Destination path
- `_logger: EzLogger | None`: Logger instance
- `_printer: EzPrinter | None`: Printer instance

**Abstract methods:**

- `upload() -> bool`: Execute upload (must be implemented by subclasses)
- `validate() -> bool`: Validate upload configuration (must be implemented by subclasses)

**Helper methods:**

- `_log_info(message: str) -> None`: Log info message
- `_log_error(message: str) -> None`: Log error message

---

### DiskUploader

**File:** `ezcompiler/uploaders/disk.py`

Uploader implementation for local disk operations.

**Features:**

- Copy files/directories to local paths
- Preserve file permissions (optional)
- Create destination directories automatically
- Progress callback support

**Example:**

```python
from ezcompiler.uploaders import DiskUploader
from pathlib import Path

uploader = DiskUploader(
    source_path=Path("dist/MyProject"),
    destination_path=Path("releases/v1.0.0"),
)
success = uploader.upload()
```

---

### ServerUploader

**File:** `ezcompiler/uploaders/server.py`

Uploader implementation for HTTP/HTTPS uploads.

**Features:**

- Upload files via HTTP POST/PUT
- Support for authentication headers
- Retry logic for failed uploads
- Progress callback support

**Example:**

```python
from ezcompiler.uploaders import ServerUploader
from pathlib import Path

uploader = ServerUploader(
    source_path=Path("dist/MyProject.zip"),
    destination_url="https://api.example.com/upload",
    headers={"Authorization": "Bearer token"},
)
success = uploader.upload()
```

---

### UploaderFactory

**File:** `ezcompiler/uploaders/factory.py`

Factory for creating uploader instances.

**Main methods:**

- `create_uploader(
    structure: Literal["disk", "server"],
    source_path: Path,
    destination: Path | str,
    **kwargs
) -> BaseUploader`: Create an uploader instance

**Example:**

```python
from ezcompiler.uploaders import UploaderFactory
from pathlib import Path

uploader = UploaderFactory.create_uploader(
    structure="disk",
    source_path=Path("dist/MyProject"),
    destination=Path("releases/v1.0.0"),
)
uploader.upload()
```

---

### Utility Classes

**File:** `ezcompiler/utils/`

#### FileUtils

**File:** `ezcompiler/utils/file_utils.py`

Static methods for file and directory operations.

**Methods:**

- `ensure_directory(path: Path) -> None`: Create directory if not exists
- `copy_file(src: Path, dst: Path) -> None`: Copy a file
- `copy_directory(src: Path, dst: Path) -> None`: Copy a directory recursively
- `delete_directory(path: Path) -> None`: Delete a directory recursively
- `get_file_size(path: Path) -> int`: Get file size in bytes

#### ValidationUtils

**File:** `ezcompiler/utils/validation_utils.py`

Static methods for validation operations.

**Methods:**

- `validate_version(version: str) -> bool`: Validate version string format
- `validate_path(path: Path | str) -> bool`: Validate path exists
- `validate_compiler_name(name: str) -> bool`: Validate compiler name
- `validate_upload_structure(structure: str) -> bool`: Validate upload structure

#### ZipUtils

**File:** `ezcompiler/utils/zip_utils.py`

Static methods for ZIP archive operations.

**Methods:**

- `create_zip_archive(source: Path, destination: Path, progress_callback: Callable | None = None) -> None`: Create ZIP archive
- `extract_zip_archive(source: Path, destination: Path) -> None`: Extract ZIP archive
- `list_zip_contents(archive: Path) -> list[str]`: List ZIP archive contents

---

### Exceptions

**File:** `ezcompiler/core/exceptions.py`

Custom exception classes for better error handling.

**Base Exception:**

- `EzCompilerError(message: str)`: Base exception class

**Specific Exceptions:**

- `CompilationError(message: str)`: Compilation-related errors
- `ConfigurationError(message: str)`: Configuration-related errors
- `TemplateError(message: str)`: Template processing errors
- `VersionError(message: str)`: Version generation errors
- `UploadError(message: str)`: Upload-related errors
- `ValidationError(message: str)`: Validation errors

**Example:**

```python
from ezcompiler.core.exceptions import ConfigurationError, CompilationError

try:
    ezcompiler.compile_project()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CompilationError as e:
    print(f"Compilation failed: {e}")
```

---

## 🧪 Usage Examples

### Basic Usage

```python
from pathlib import Path
from ezcompiler import EzCompiler

# Create compiler instance
ezcompiler = EzCompiler()

# Initialize project
ezcompiler.init_project(
    version="1.0.0",
    project_name="MyProject",
    main_file="main.py",
    include_files={"files": ["config.yaml"], "folders": ["assets"]},
    output_folder="dist",
    company_name="MyCompany",
    project_description="My awesome project",
)

# Generate supporting files
ezcompiler.generate_version_file("version_info.txt")
ezcompiler.generate_setup_file("setup.py")

# Compile project
ezcompiler.compile_project(console=True, compiler="PyInstaller")

# Create distribution
ezcompiler.zip_compiled_project()
ezcompiler.upload_to_repo(structure="disk", repo_path="./releases")
```

### Configuration from Files

```python
import yaml
from pathlib import Path
from ezcompiler import EzCompiler, CompilerConfig

# Load configuration from YAML
with open("ezcompiler.yaml") as f:
    config_dict = yaml.safe_load(f)

# Create config object
config = CompilerConfig.from_dict(config_dict)

# Create compiler and use config
ezcompiler = EzCompiler()
ezcompiler._config = config

# Continue with compilation...
ezcompiler.compile_project()
```

### Advanced Compilation

```python
from ezcompiler import EzCompiler

ezcompiler = EzCompiler(log_level="DEBUG")

# Initialize with advanced options
ezcompiler.init_project(
    version="2.0.0",
    project_name="AdvancedApp",
    main_file="src/main.py",
    include_files={
        "files": ["config.yaml", "README.md", "LICENSE"],
        "folders": ["assets", "data", "templates"]
    },
    output_folder="build/dist",
    company_name="TechCorp",
    project_description="Advanced application with many features",
    author="John Doe",
    icon="resources/icon.ico",
    packages=["requests", "pandas", "numpy", "matplotlib"],
    includes=["encodings", "json"],
    excludes=["debugpy", "test", "unittest", "pytest"],
    optimize=True,
    strip=True,
    console=False,  # GUI application
)

# Compile with specific compiler
ezcompiler.compile_project(console=False, compiler="Cx_Freeze")
```

### Distribution and Upload

```python
from ezcompiler import EzCompiler

ezcompiler = EzCompiler()
ezcompiler.init_project(...)
ezcompiler.compile_project()

# Create ZIP archive
ezcompiler.zip_compiled_project()

# Upload to local disk
ezcompiler.upload_to_repo(
    structure="disk",
    repo_path="./releases/v1.0.0",
    upload_config={"preserve_permissions": True}
)

# Or upload to server
ezcompiler.upload_to_repo(
    structure="server",
    repo_path="https://api.example.com/releases",
    upload_config={
        "headers": {"Authorization": "Bearer token"},
        "timeout": 300,
    }
)
```

### Template Generation

```python
from ezcompiler.templates import TemplateManager, TemplateProcessor

# Using TemplateManager
manager = TemplateManager()

# List available templates
templates = manager.list_templates()
print(f"Available templates: {templates}")

# Process a template
content = manager.process_template("config.yaml", {
    "PROJECT_NAME": "MyProject",
    "VERSION": "1.0.0",
    "MAIN_FILE": "main.py",
    "OUTPUT_FOLDER": "dist",
})

# Using TemplateProcessor directly
processor = TemplateProcessor()

# Generate mockup with example values
mockup = processor.generate_mockup("config")

# Substitute variables
result = processor.substitute(
    "Project #PROJECT_NAME# version #VERSION#",
    {"PROJECT_NAME": "Test", "VERSION": "0.1.0"}
)
```

### Type Hints for Better IDE Support

```python
from ezcompiler import EzCompiler, CompilerConfig
from ezcompiler import Config, Compiler  # Type aliases
from ezcompiler.compilers import BaseCompiler, CxFreezeCompiler, PyInstallerCompiler
from ezcompiler.uploaders import BaseUploader, DiskUploader, ServerUploader

# Type hints enable full IDE autocompletion
ezcompiler = EzCompiler()
config: Config = ezcompiler.config  # Autocompletion works!

# Compiler type hints
compiler: Compiler = CxFreezeCompiler(config)
compiler.compile()  # Autocompletion works!

# Uploader type hints
uploader: BaseUploader = DiskUploader(...)
uploader.upload()  # Autocompletion works!
```

---

## 🎯 Best Practices

### Type Safety

- **Use type hints**: Import type aliases from `ezcompiler` for better IDE support
- **Type your variables**: Enable full autocompletion with explicit types
- **Use CompilerConfig**: Always use `CompilerConfig` dataclass for configuration

### Configuration

- **Use configuration files**: Store configuration in YAML or JSON for version control
- **Validate early**: Call `config.validate()` before compilation
- **Use sensible defaults**: Most fields have reasonable defaults

**Configuration Priority:**

1. **Direct parameters** - Highest priority
2. **Configuration file** (YAML/JSON)
3. **Default values** - Lowest priority

### Compilation

- **Choose the right compiler**:
  - `PyInstaller`: For single-file distribution, simpler deployment
  - `Cx_Freeze`: For better performance, complex dependencies
- **Test both compilers**: Different compilers may handle dependencies differently
- **Use console=False for GUI apps**: Hides the console window

### Error Handling

- **Catch specific exceptions**: Use `CompilationError`, `ConfigurationError`, etc.
- **Log errors**: EzCompiler provides comprehensive logging
- **Validate configuration**: Check configuration before compilation

```python
from ezcompiler import EzCompiler
from ezcompiler.core.exceptions import (
    CompilationError,
    ConfigurationError,
    TemplateError,
)

try:
    ezcompiler = EzCompiler()
    ezcompiler.init_project(...)
    ezcompiler.compile_project()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CompilationError as e:
    print(f"Compilation failed: {e}")
except TemplateError as e:
    print(f"Template error: {e}")
```

### Testing

- **Test compilation locally**: Always test before deploying
- **Test on target platforms**: Compiled executables are platform-specific
- **Use the --debug flag**: Enable debug mode for troubleshooting

### Performance

- **Use optimization**: Enable `optimize=True` for smaller executables
- **Exclude unnecessary packages**: Use `excludes` to remove unused modules
- **Consider Cx_Freeze for large apps**: Better performance for complex applications

---

## 📝 Type Reference

### Type Aliases

```python
from ezcompiler import Config, Compiler

# Type aliases for better IDE support
Config = CompilerConfig
Compiler = BaseCompiler
```

### Return Types

```python
# EzCompiler methods
ezcompiler.logger -> EzLogger
ezcompiler.printer -> EzPrinter
ezcompiler.ezpl -> Ezpl
ezcompiler.config -> CompilerConfig

# Generator methods
version_generator.generate(...) -> str
setup_generator.generate_from_config(...) -> str

# Template methods
template_manager.load_template(...) -> str
template_manager.list_templates() -> list[str]
template_processor.substitute(...) -> str

# Uploader methods
uploader.upload() -> bool
uploader.validate() -> bool
uploader_factory.create_uploader(...) -> BaseUploader

# Config methods
config.to_dict() -> dict[str, Any]
CompilerConfig.from_dict(...) -> CompilerConfig
config.output_path -> Path
config.version_tuple -> tuple[int, ...]
```

---

**EzCompiler – Complete API documentation for professional Python project compilation and distribution.**
