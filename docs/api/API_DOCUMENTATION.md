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
      - [Build Pipeline](#build-pipeline)
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
    - [NuitkaCompiler](#nuitkacompiler)
    - [TemplateLoader](#templateloader)
    - [TemplateService](#templateservice)
    - [BaseUploader](#baseuploader)
    - [DiskUploader](#diskuploader)
    - [ServerUploader](#serveruploader)
    - [UploaderFactory](#uploaderfactory)
    - [Utility Classes](#utility-classes)
      - [FileUtils](#fileutils)
      - [ValidationUtils](#validationutils)
      - [ZipUtils](#ziputils)
    - [Exceptions](#exceptions)
  - [🧪 Usage Examples](#-usage-examples)
    - [Basic Usage with run\_pipeline()](#basic-usage-with-run_pipeline)
    - [Basic Usage with Individual Steps](#basic-usage-with-individual-steps)
    - [Configuration from Files](#configuration-from-files)
    - [Advanced Compilation](#advanced-compilation)
    - [Distribution and Upload](#distribution-and-upload)
    - [Template Generation](#template-generation)
    - [Type Hints for Better IDE Support](#type-hints-for-better-ide-support)
  - [🎯 Best Practices](#-best-practices)
    - [Type Safety](#type-safety)
    - [Configuration](#configuration)
    - [Compilation (Best Practices)](#compilation-best-practices)
    - [Error Handling](#error-handling)
    - [Testing](#testing)
    - [Performance](#performance)
  - [📝 Type Reference](#-type-reference)
    - [Type Aliases](#type-aliases)
    - [Return Types](#return-types)

---

## 🧠 Main Module (`ezcompiler`)

### Class EzCompiler

**File:** `ezcompiler/interfaces/python_api.py`

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
- Initializes `TemplateService`, `CompilerService`, and `UploaderService` instances
- Initializes compiler state to `None` (created on demand)
- Configures internal state and compilation result tracking

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
- `compiler`: Compiler to use ("PyInstaller", "Cx_Freeze", "Nuitka", or None for interactive/auto)

**Compiler Selection:**

- If `compiler` is specified, uses that compiler directly
- If `None`, checks for command-line arguments (`-cxf`, `-pyi`, or `-nui`)
- If no arguments, prompts interactively via `InquirerPy`

**ZIP Requirement:**

- `Cx_Freeze`: `zip_needed = True` (directory-based output)
- `PyInstaller` (onefile): `zip_needed = False` (single file output)
- `Nuitka` (standalone): `zip_needed = True` (directory-based output)
- `Nuitka` (onefile): `zip_needed = False` (single file output)

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

#### Build Pipeline

- `run_pipeline(
    console: bool = True,
    compiler: str | None = None,
    skip_zip: bool = False,
    skip_upload: bool = False,
    upload_structure: Literal["server", "disk"] | None = None,
    upload_destination: str | None = None,
    upload_config: dict[str, Any] | None = None,
) -> None`: Run the full build pipeline with DLP visual progress tracking

**Parameters:**

- `console`: Whether to show console window (default: True)
- `compiler`: Compiler to use or None for auto-selection ("Cx_Freeze", "PyInstaller", "Nuitka")
- `skip_zip`: Skip ZIP archive creation (default: False)
- `skip_upload`: Skip upload step (default: False)
- `upload_structure`: Upload type ("server" or "disk")
- `upload_destination`: Upload destination path or URL
- `upload_config`: Additional uploader configuration options

**Behavior:**

Executes version generation, compilation, optional ZIP creation, and optional upload in sequence with a DynamicLayeredProgress (DLP) display from ezpl. Each stage is visualized with spinners and progress bars.

**Example:**

```python
ezcompiler = EzCompiler()
ezcompiler.init_project(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

# Run full pipeline with DLP progress display
ezcompiler.run_pipeline(
    console=True,
    compiler="Nuitka",
    upload_structure="disk",
    upload_destination="./releases",
)

# Or skip optional steps
ezcompiler.run_pipeline(
    console=False,
    skip_zip=True,
    skip_upload=True,
)
```

---

### CompilerConfig

**File:** `ezcompiler/shared/compiler_config.py`

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
- `compiler: str = "auto"`: Compiler choice ("auto", "PyInstaller", "Cx_Freeze", "Nuitka")
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

**File:** `ezcompiler/protocols/base_compiler.py`

Abstract base class for all compiler implementations.

**Main attributes:**

- `config: CompilerConfig`: Compilation configuration
- `_zip_needed: bool`: Whether ZIP archive is needed after compilation

**Abstract methods:**

- `compile() -> None`: Execute compilation (must be implemented by subclasses)
- `get_compiler_name() -> str`: Return compiler name (must be implemented by subclasses)

**Properties:**

- `zip_needed -> bool`: Whether ZIP archive is needed

**Static methods:**

- `extract_error_summary(output: str) -> str`: Extract a human-readable error summary from compiler subprocess output

**Helper methods:**

- `_validate_config() -> None`: Validate configuration before compilation
- `_prepare_output_dir() -> None`: Prepare output directory
- `_log_info(message: str) -> None`: Log info message
- `_log_error(message: str) -> None`: Log error message

---

### CxFreezeCompiler

**File:** `ezcompiler/protocols/cx_freeze_compiler.py`

Cx_Freeze compiler implementation. Creates directory-based executables.

**Characteristics:**

- `_zip_needed = True` (always creates directory output)
- Better performance for large applications
- Supports complex dependencies

**Example:**

```python
from ezcompiler.protocols import CxFreezeCompiler
from ezcompiler import CompilerConfig

config = CompilerConfig(...)
compiler = CxFreezeCompiler(config)
compiler.compile()
```

---

### PyInstallerCompiler

**File:** `ezcompiler/protocols/pyinstaller_compiler.py`

PyInstaller compiler implementation. Creates single-file executables.

**Characteristics:**

- `zip_needed = False` (creates single file in onefile mode)
- `zip_needed = True` (creates directory in onedir mode)
- Simpler distribution (single executable in onefile)
- Output folder flattening: nested subfolder contents are moved to output_folder

**Example:**

```python
from ezcompiler.protocols import PyInstallerCompiler
from ezcompiler import CompilerConfig

config = CompilerConfig(...)
compiler = PyInstallerCompiler(config)
compiler.compile()
```

---

### NuitkaCompiler

**File:** `ezcompiler/protocols/nuitka_compiler.py`

Nuitka compiler implementation. Creates standalone executables or single-file executables.

**Characteristics:**

- `zip_needed = True` (standalone mode, directory output)
- `zip_needed = False` (onefile mode, single executable)
- Best optimization: compiles Python to C then to native code
- Requires MSVC backend on Python 3.13+ (MinGW64 not compatible)
- Output folder flattening: nested `.dist` folder contents are moved to output_folder

**Example:**

```python
from ezcompiler.protocols import NuitkaCompiler
from ezcompiler import CompilerConfig

config = CompilerConfig(...)
compiler = NuitkaCompiler(config)
compiler.compile()
```

---

### TemplateLoader

**File:** `ezcompiler/utils/template_loader.py`

Loader for accessing EzCompiler template files from the assets directory.

**Main methods:**

- `load_template(template_name: str) -> str`: Load a template file by name
- `get_template_path(template_name: str) -> Path`: Get the full path to a template
- `list_templates() -> list[str]`: List all available templates

**Available Templates:**

- `config/config.yaml.template`: YAML configuration template
- `config/config.json.template`: JSON configuration template
- `setup/setup.py.template`: Setup file template
- `version/version_info.txt.template`: Version information template

---

### TemplateService

**File:** `ezcompiler/services/template_service.py`

Service for processing templates with variable substitution and generating project files.

**Main methods:**

- `generate_version_file(config_dict: dict[str, Any], output_path: Path) -> None`: Generate version info file
- `generate_setup_file(config_dict: dict[str, Any], output_path: Path) -> None`: Generate setup.py file
- `generate_config_file(config_dict: dict[str, Any], output_path: Path, format: str = "yaml") -> None`: Generate config file
- `process_template(template_name: str, variables: dict[str, str]) -> str`: Process a template with variable substitution

**Variable Format:**

Variables use the format `#VARIABLE_NAME#` for substitution.

**Example:**

```python
from ezcompiler.services import TemplateService

service = TemplateService()
service.generate_version_file(
    config_dict={"version": "1.0.0", "project_name": "MyApp", ...},
    output_path=Path("version_info.txt"),
)
```

---

### BaseUploader

**File:** `ezcompiler/protocols/base_uploader.py`

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

**File:** `ezcompiler/protocols/disk_uploader.py`

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

**File:** `ezcompiler/protocols/server_uploader.py`

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

**File:** `ezcompiler/services/uploader_service.py`

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

**File:** `ezcompiler/shared/exceptions/`

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
from ezcompiler.shared.exceptions import ConfigurationError, CompilationError

try:
    ezcompiler.compile_project()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CompilationError as e:
    print(f"Compilation failed: {e}")
```

---

## 🧪 Usage Examples

### Basic Usage with run_pipeline()

```python
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

# Run full pipeline with DLP progress display
ezcompiler.run_pipeline(
    console=True,
    upload_structure="disk",
    upload_destination="./releases",
)
```

### Basic Usage with Individual Steps

```python
from ezcompiler import EzCompiler

ezcompiler = EzCompiler()
ezcompiler.init_project(
    version="1.0.0",
    project_name="MyProject",
    main_file="main.py",
    include_files={"files": ["config.yaml"], "folders": ["assets"]},
    output_folder="dist",
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

# Or use run_pipeline() for DLP progress display
# ezcompiler.run_pipeline(console=False, compiler="Nuitka")
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
from ezcompiler.protocols import BaseCompiler, CxFreezeCompiler, PyInstallerCompiler, NuitkaCompiler
from ezcompiler.protocols import BaseUploader, DiskUploader, ServerUploader

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

### Compilation (Best Practices)

- **Choose the right compiler**:
  - `Cx_Freeze`: For directory-based output, complex dependencies
  - `PyInstaller`: For single-file distribution, simpler deployment
  - `Nuitka`: For best performance, compiles to native C code
- **Test multiple compilers**: Different compilers may handle dependencies differently
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
- **Consider Nuitka for best performance**: Compiles to native C code for optimal speed
- **Consider Cx_Freeze for large apps**: Better handling of complex dependencies
- **Use `run_pipeline()`**: Provides DLP progress display for better user experience

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
