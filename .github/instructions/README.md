# EzCompiler Project Guidelines

**Version:** 2.1.0
**Architecture:** Layered Architecture with Service-Oriented Design
**Target:** Python 3.10+ | Windows Primary (Unix compatible utilities)

---

## Project Philosophy

EzCompiler is a **professional-grade compilation framework** that prioritizes:

1. **Architectural Clarity** - Clear separation of concerns across layers
2. **Multi-Compiler Abstraction** - Unified interface for Cx_Freeze, PyInstaller, and Nuitka
3. **Configuration-Driven** - YAML/JSON-first approach with runtime validation
4. **Production-Ready** - Comprehensive error handling, logging, and validation
5. **Developer Experience** - Both CLI and Python API with progress tracking

**Core Principle:** _Simplify complex compilation workflows through clean abstractions and predictable behavior._

---

## Architectural Rules

### Layered Architecture (Strict Enforcement)

```text
┌─────────────────────────────────────────────────┐
│  interfaces/    (CLI + Python API)              │  ← Public Entry Points
├─────────────────────────────────────────────────┤
│  services/      (Business Orchestration)        │  ← Business Logic
├─────────────────────────────────────────────────┤
│  protocols/     (Abstract + Implementations)    │  ← Compiler/Uploader Abstractions
├─────────────────────────────────────────────────┤
│  shared/        (Config + Exceptions)           │  ← Shared Domain Models
│  utils/         (Domain-Specific Utilities)     │  ← Cross-Cutting Concerns
└─────────────────────────────────────────────────┘
```

**Dependency Flow Rules:**

- ✅ **ALLOWED:** Upper layers depend on lower layers
- ❌ **FORBIDDEN:** Lower layers importing from upper layers
- ❌ **FORBIDDEN:** Cross-layer jumps (interfaces → protocols directly)
- ✅ **ALLOWED:** All layers can use `shared/` and `utils/`

**Example:**

```python
# ✅ CORRECT
from ezcompiler.services.compiler_service import CompilerService
from ezcompiler.shared.compiler_config import CompilerConfig

# ❌ INCORRECT
# services/ importing from interfaces/
from ezcompiler.interfaces.python_api import EzCompiler  # NEVER
```

---

## Layer Responsibilities

### interfaces/ - Public API Layer

**Purpose:** External-facing APIs (CLI and Python)

**Rules:**

- Only layer that directly interacts with end users
- Orchestrates calls to `services/` layer
- Handles user input validation and transformation
- Manages interactive CLI (InquirerPy, Click)
- Implements progress tracking (DLP integration)
- **NEVER** contains business logic or direct compiler/uploader calls

**Key Files:**

- `cli_interface.py` - Click-based CLI with interactive prompts
- `python_api.py` - `EzCompiler` class (main public API)

**Pattern:**

```python
class EzCompiler:
    def __init__(self, config: CompilerConfig | None = None):
        self._config_service = ConfigService(config)
        self._compiler_service = CompilerService(self._config_service)
        # Delegate to services, never implement logic here
```

---

### services/ - Business Logic Layer

**Purpose:** Orchestrate business workflows and coordinate protocols

**Rules:**

- Implements business logic and workflow orchestration
- Coordinates multiple `protocols/` implementations
- Validates business rules (not just data validation)
- Manages service-level error handling and logging
- **NEVER** implements concrete compiler/uploader logic (that's `protocols/`)

**Key Files:**

- `compiler_service.py` - Compiler selection and orchestration
- `config_service.py` - Configuration management and validation
- `template_service.py` - Template generation workflow
- `uploader_service.py` - Upload orchestration

**Pattern:**

```python
class CompilerService:
    def select_compiler(self, compiler_name: str) -> BaseCompiler:
        """Select compiler based on availability and config."""
        # Business logic: validate availability, select best match
        # Returns protocol implementation from protocols/
```

---

### protocols/ - Implementation Abstraction Layer

**Purpose:** Define interfaces and concrete implementations for compilers/uploaders

**Rules:**

- Abstract base classes define contracts (`BaseCompiler`, `BaseUploader`)
- Concrete implementations for each compiler/uploader
- Factory pattern for instantiation (`UploaderFactory`)
- **NEVER** contains business logic (only implementation details)
- Each implementation is self-contained and swappable

**Key Files:**

- `base_compiler.py` - Abstract compiler interface
- `cx_freeze_compiler.py` / `pyinstaller_compiler.py` / `nuitka_compiler.py`
- `base_uploader.py` - Abstract uploader interface
- `disk_uploader.py` / `server_uploader.py`
- `uploader_factory.py` - Factory for uploader instantiation

**Pattern:**

```python
class BaseCompiler(ABC):
    @abstractmethod
    def compile(self, config: CompilerConfig) -> bool:
        """Compile project with specific compiler."""
        pass

class PyInstallerCompiler(BaseCompiler):
    def compile(self, config: CompilerConfig) -> bool:
        # PyInstaller-specific implementation
        pass
```

---

### shared/ - Shared Domain Models

**Purpose:** Central configuration and exception hierarchy

**Rules:**

- `CompilerConfig` is the **single source of truth** for configuration
- All layers read from `CompilerConfig`, never modify it directly (immutable after creation)
- Exception hierarchy mirrors domain structure (not technical structure)
- **NEVER** contains business logic or utilities

**Key Files:**

- `compiler_config.py` - Centralized configuration dataclass
- `exceptions/` - Domain exception hierarchy

**Pattern:**

```python
@dataclass
class CompilerConfig:
    """Immutable configuration object."""
    project_name: str
    version: str
    main_file: str
    # ... all configuration fields

    @classmethod
    def from_dict(cls, data: dict) -> "CompilerConfig":
        """Factory method for dict-based creation."""
```

---

### utils/ - Domain-Specific Utilities

**Purpose:** Reusable utilities organized by domain concern

**Rules:**

- Each utils module is **domain-specific** (compiler, config, file, template, upload, validators, zip)
- Utilities are **pure functions** or simple classes with no side effects when possible
- **NEVER** contains business logic (that's `services/`)
- Can be used by any layer
- Prefer small, focused functions over large utility classes
- **Validators are modular:** The `validators/` package organizes validation functions by domain (format, path, type, value, schema, domain, string, meta)

**Key Files:**

- `compiler_utils.py` - Compiler detection, availability checks
- `config_utils.py` - Config parsing, transformation
- `file_utils.py` - File operations, path handling
- `template_utils.py` - Template rendering, placeholders
- `uploader_utils.py` - Upload helpers
- `validators/` - **Modular validation package** (9 specialized modules)
  - `format_validators.py` - Version, email, URL validation
  - `path_validators.py` - File and directory path validation
  - `type_validators.py` - Type checking and validation
  - `value_validators.py` - Range, length, choice validation
  - `schema_validators.py` - Schema and configuration validation
  - `domain_validators.py` - Domain-specific validators
  - `string_validators.py` - String utilities and pattern validation
  - `meta_validators.py` - Meta-validation utilities
- `zip_utils.py` - Archive creation, compression

**Patterns:**

```python
# Utility function pattern
def check_compiler_availability(compiler_name: str) -> bool:
    """Pure function: check if compiler is installed."""
    # No side effects, deterministic
    return True

# Validator usage pattern
from ezcompiler.utils.validators import validate_email, validate_version_string

if not validate_email(user_email):
    raise ValidationError("Invalid email")
```

---

## Design Patterns in Use

### Factory Pattern

**Where:** `UploaderFactory`, compiler selection in `CompilerService`

**Rule:** Use factories for creating protocol implementations based on runtime configuration.

```python
# ✅ CORRECT
uploader = UploaderFactory.create(upload_structure, config)

# ❌ INCORRECT - Direct instantiation in business logic
uploader = DiskUploader(config)  # Don't hardcode
```

---

### Service Pattern

**Where:** All classes in `services/`

**Rule:** Services orchestrate workflows, never implement concrete logic.

```python
# ✅ CORRECT - Service orchestrates
class CompilerService:
    def compile_project(self, compiler_name: str) -> bool:
        compiler = self._get_compiler(compiler_name)  # Factory
        return compiler.compile(self._config)         # Delegate

# ❌ INCORRECT - Service implements
class CompilerService:
    def compile_project(self, compiler_name: str) -> bool:
        subprocess.run(["pyinstaller", ...])  # NEVER
```

---

### Configuration Object Pattern

**Where:** `CompilerConfig` throughout the codebase

**Rule:** Single, immutable configuration object passed through layers.

```python
# ✅ CORRECT
config = CompilerConfig(project_name="MyApp", version="1.0.0", ...)
service = CompilerService(config)  # Inject config

# ❌ INCORRECT
service.set_project_name("MyApp")  # Don't mutate
```

---

### Dependency Injection

**Where:** All layer boundaries

**Rule:** Inject dependencies through constructors, never use global state.

```python
# ✅ CORRECT
class EzCompiler:
    def __init__(self, config: CompilerConfig | None = None):
        self._config_service = ConfigService(config)
        self._compiler_service = CompilerService(self._config_service)

# ❌ INCORRECT
class EzCompiler:
    def __init__(self):
        self._config = load_global_config()  # No globals
```

---

## Code Organization Standards

### File Structure Template

Every Python file should follow this structure:

```python
# ///////////////////////////////////////////////////////////////
# MODULE_NAME - Brief Description
# Project: EzCompiler
# ///////////////////////////////////////////////////////////////

"""
Module docstring with purpose and usage.

Example:
    >>> from ezcompiler.services.compiler_service import CompilerService
    >>> service = CompilerService(config)
"""

from __future__ import annotations  # Always first import

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
from pathlib import Path
from typing import Optional

# Third-party imports
from click import command

# Local imports
from ezcompiler.shared.compiler_config import CompilerConfig
from ezcompiler.shared.exceptions.services.service_exceptions import CompilerServiceError

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////
DEFAULT_COMPILER = "PyInstaller"

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////

class MyClass:
    """Class docstring."""

    # ------------------------------------------------
    # INIT
    # ------------------------------------------------

    def __init__(self, config: CompilerConfig) -> None:
        """Initialize with config."""
        self._config = config

    # ------------------------------------------------
    # PUBLIC METHODS
    # ------------------------------------------------

    def public_method(self) -> bool:
        """Public method docstring."""
        return True

    # ------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------

    def _private_helper(self) -> None:
        """Private helper docstring."""
        pass

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////

def standalone_function(param: str) -> bool:
    """Function docstring."""
    return True
```

---

## Naming Conventions

### Modules

- **services/** - `*_service.py` (e.g., `compiler_service.py`)
- **protocols/** - `*_compiler.py`, `*_uploader.py`, or `base_*.py`
- **utils/** - `*_utils.py` (e.g., `validation_utils.py`)
- **exceptions/** - `*_exceptions.py` (e.g., `service_exceptions.py`)

### Classes

- **Services:** `*Service` suffix (e.g., `CompilerService`, `ConfigService`)
- **Protocols:** `Base*` for abstracts (e.g., `BaseCompiler`), descriptive names for implementations
- **Configs:** `*Config` suffix (e.g., `CompilerConfig`)
- **Exceptions:** `*Error` suffix (e.g., `CompilationError`, `ValidationError`)

### Functions

- **Public API:** Descriptive verbs (`compile_project`, `upload_to_repo`, `init_project`)
- **Utilities:** Pure function names (`check_compiler_availability`, `validate_path`)
- **Private:** Leading underscore (`_validate_internal`, `_get_compiler`)

---

## Type Hints Rules

### Mandatory Type Hints

```python
# ✅ CORRECT - Always type hint public APIs
def compile_project(
    config: CompilerConfig,
    compiler_name: str | None = None
) -> bool:
    """Compile with specified compiler."""
    pass

# ✅ CORRECT - Type hint class attributes
class CompilerService:
    _config: CompilerConfig
    _logger: logging.Logger

    def __init__(self, config: CompilerConfig) -> None:
        self._config = config
```

### Type Hint Standards

- **Use native types:** `list[str]` not `List[str]` (Python 3.10+)
- **Use union operator:** `str | None` not `Optional[str]` or `Union[str, None]`
- **Import from `collections.abc`:** `Callable`, `Sequence`, `Mapping`
- **Always include return type:** Even for `-> None`
- **Use `from __future__ import annotations`** for forward references

```python
# ✅ CORRECT
from __future__ import annotations
from collections.abc import Callable

def process(items: list[str], callback: Callable[[str], bool]) -> dict[str, int]:
    pass

# ❌ INCORRECT
from typing import List, Dict, Optional, Callable

def process(items: List[str], callback: Callable[[str], bool]) -> Dict[str, int]:
    pass
```

---

## Exception Handling

### Exception Hierarchy

```text
EzCompilerError (base)
├─ Service Exceptions (services/)
│  ├─ CompilationError
│  ├─ CompilerServiceError
│  ├─ ConfigurationError
│  ├─ TemplateServiceError
│  ├─ UploaderServiceError
│  └─ VersionError
└─ Util Exceptions (utils/)
   ├─ CompilerError
   ├─ ConfigError
   ├─ FileOperationError
   ├─ TemplateProcessingError
   ├─ UploadError
   ├─ ValidationError
   └─ ZipError
```

### Exception Rules

1. **Always inherit from `EzCompilerError`** for project-specific exceptions
2. **Use specific exceptions** - never raise generic `Exception`
3. **Preserve exception chains** - use `raise ... from ...`
4. **Log before raising** at service boundaries
5. **Catch specific exceptions** at layer boundaries

```python
# ✅ CORRECT
from ezcompiler.shared.exceptions.services.service_exceptions import CompilationError

def compile_project(config: CompilerConfig) -> bool:
    try:
        result = compiler.compile(config)
    except subprocess.CalledProcessError as e:
        logger.error(f"Compilation failed: {e}")
        raise CompilationError(f"PyInstaller failed: {e}") from e
    return result

# ❌ INCORRECT
def compile_project(config: CompilerConfig) -> bool:
    try:
        result = compiler.compile(config)
    except Exception:  # Too broad
        raise Exception("Failed")  # Lost context, no chain
```

---

## Logging Standards

### Logger Configuration

- **Use ezpl** (ezplog) for all logging
- **Logger naming:** `__name__` for module-level loggers
- **Log levels by layer:**
  - `interfaces/` → `DEBUG`, `INFO`
  - `services/` → `INFO`, `WARNING`, `ERROR`
  - `protocols/` → `WARNING`, `ERROR`
  - `utils/` → Log indirectly via calling layer

### Logging Patterns

```python
# ✅ CORRECT
from ezplog import logger

logger.info(f"Compiling project: {config.project_name}")
logger.warning(f"Compiler {name} not available, falling back to {fallback}")
logger.error(f"Compilation failed: {error}", exc_info=True)

# ❌ INCORRECT
print(f"Compiling...")  # Never use print (except CLI display)
logger.debug(f"ERROR: Failed")  # Wrong level
```

---

## Configuration Management

### CompilerConfig - Single Source of Truth

**Rules:**

1. **Immutable after creation** - use `@dataclass(frozen=False)` but treat as immutable
2. **Validate on construction** - use `__post_init__` for validation
3. **Use factory methods** - `from_dict`, `from_yaml`, `from_json`
4. **Never modify in services** - create new instances if needed
5. **Pass through layers** - inject via constructors

```python
# ✅ CORRECT
config = CompilerConfig.from_yaml("config.yaml")
service = CompilerService(config)  # Inject
result = service.compile_project()

# ❌ INCORRECT
service = CompilerService()
service.load_config("config.yaml")  # Don't mutate
service.config.project_name = "New"  # NEVER mutate
```

### Configuration Validation

- **Validate at boundaries** - when creating `CompilerConfig`
- **Use validation_utils.py** - centralized validation logic
- **Fail fast** - raise `ValidationError` immediately on invalid data
- **Provide clear messages** - include field name and expected format

---

## Testing Standards

### Test Organization

```text
tests/
├── unit/                   # Isolated unit tests
│   ├── test_core.py
│   ├── test_compilers.py
│   └── test_utils.py
├── integration/            # Multi-component tests
│   └── test_ezcompiler_integration.py
└── robustness/             # Edge cases, error handling
    ├── test_edge_cases.py
    └── test_error_handling.py
```

### Test Markers

```python
@pytest.mark.unit           # Fast, isolated tests
@pytest.mark.integration    # Multi-component tests
@pytest.mark.robustness     # Edge cases, errors
@pytest.mark.compiler       # Compiler-specific tests
@pytest.mark.cli            # CLI tests
@pytest.mark.uploader       # Uploader tests
```

### Testing Rules

1. **Target 60-70% coverage** for production code (currently 29% - improvement needed)
2. **Focus on critical paths** - services/, protocols/, shared/
3. **Test error handling** - every exception path should be tested
4. **Use parametrize** - for data-driven tests
5. **Mock external dependencies** - compilers, file I/O, network calls
6. **Test public APIs** - interfaces/ should have high coverage

```python
# ✅ CORRECT - Parametrized, focused test
@pytest.mark.unit
@pytest.mark.parametrize("compiler", ["PyInstaller", "Cx_Freeze", "Nuitka"])
def test_compiler_selection(compiler: str, mock_config: CompilerConfig):
    service = CompilerService(mock_config)
    result = service.select_compiler(compiler)
    assert isinstance(result, BaseCompiler)

# ❌ INCORRECT - Untested edge cases
def test_compiler():
    service = CompilerService(config)
    service.compile_project()  # No assertions, no error cases
```

---

## Platform Considerations

### Windows-First, Unix-Compatible

**Rules:**

1. **Use `pathlib.Path`** exclusively - never `os.path`
2. **Test path handling** - Windows backslashes vs Unix forward slashes
3. **Use `Path.resolve()`** for absolute paths
4. **Handle drive letters** on Windows (e.g., `C:\`)
5. **Compiler availability** - assume Windows primary, but don't hardcode

```python
# ✅ CORRECT
from pathlib import Path

def get_output_path(base: str) -> Path:
    return Path(base).resolve()  # Works on both platforms

# ❌ INCORRECT
import os

def get_output_path(base: str) -> str:
    return os.path.join("C:\\", base)  # Windows-only
```

---

## Code Review Checklist

Before committing code, verify:

### Architecture

- [ ] Follows layered architecture (no cross-layer violations)
- [ ] Dependencies flow downward (upper → lower layers)
- [ ] No business logic in `interfaces/` or `utils/`
- [ ] Services orchestrate, protocols implement

### Code Quality

- [ ] Type hints on all public functions/methods
- [ ] Docstrings (Google-style) on public APIs
- [ ] Section separators (`# ///////////////////////////////////////////////////////////////`)
- [ ] Imports organized (standard → third-party → local)
- [ ] No `print()` statements (use logger or CLI display)

### Testing

- [ ] Tests added for new functionality
- [ ] Edge cases and error paths tested
- [ ] Appropriate test markers (`@pytest.mark.*`)
- [ ] Mocks used for external dependencies

### Configuration

- [ ] Uses `CompilerConfig` for all configuration
- [ ] Validates input at boundaries
- [ ] No mutable global state

### Error Handling

- [ ] Specific exceptions (not generic `Exception`)
- [ ] Exception chains preserved (`raise ... from ...`)
- [ ] Logged at appropriate level before raising

---

## Performance Guidelines

### Optimization Philosophy

**Rule:** Profile before optimizing. Focus on correctness first.

**Current Performance Characteristics:**

- Compilation time: Dominated by external compilers (PyInstaller, etc.)
- File I/O: Use buffered reads/writes for large files
- Path operations: `pathlib` is sufficient for current scale

**Avoid Premature Optimization:**

- Don't optimize utilities unless profiling shows bottleneck
- Keep code readable over micro-optimizations
- External compiler performance is the limiting factor

---

## Dependencies Management

### Core Dependencies

**Production:**

- `cx_Freeze`, `PyInstaller`, `Nuitka` - Compiler backends
- `InquirerPy` - Interactive CLI
- `Click` - CLI framework
- `requests` - HTTP uploads
- `PyYAML` - Configuration
- `ezplog` - Logging
- `tomli-w` - TOML writing

**Development:**

- `black`, `isort`, `ruff` - Code quality
- `pyright` - Type checking
- `pytest`, `pytest-cov` - Testing
- `bandit` - Security

### Adding Dependencies

**Rules:**

1. **Justify new dependencies** - avoid dependency bloat
2. **Pin versions** - `package>=X.Y,<Z.0`
3. **Update `pyproject.toml`** - both `dependencies` and `dev` sections
4. **Document in docstrings** - if dependency is domain-specific

---

## Version Management

### Versioning Strategy

**Semantic Versioning:** `MAJOR.MINOR.PATCH`

- **MAJOR** - Breaking API changes (e.g., 1.x → 2.0)
- **MINOR** - New features, backward-compatible (e.g., 2.0 → 2.1)
- **PATCH** - Bug fixes, backward-compatible (e.g., 2.1.0 → 2.1.1)

**Current Version:** `2.1.0`

**Update Locations:**

- `pyproject.toml` → `[project] version`
- `ezcompiler/__init__.py` → `__version__`
- Update CHANGELOG.md (when created)

---

## Common Pitfalls to Avoid

### 1. Cross-Layer Violations

```python
# ❌ WRONG - Services importing from interfaces
from ezcompiler.interfaces.python_api import EzCompiler

# ✅ CORRECT - Services only import from protocols/shared/utils
from ezcompiler.protocols.base_compiler import BaseCompiler
```

### 2. Business Logic in Utils

```python
# ❌ WRONG - Business logic in utils
def compile_with_fallback(config: CompilerConfig) -> bool:
    try:
        return PyInstallerCompiler(config).compile()
    except:
        return CxFreezeCompiler(config).compile()

# ✅ CORRECT - Business logic in services
class CompilerService:
    def compile_with_fallback(self, preferred: str) -> bool:
        # Orchestration belongs in services
```

### 3. Mutable Configuration

```python
# ❌ WRONG - Mutating config
def update_version(config: CompilerConfig, version: str):
    config.version = version  # Mutation

# ✅ CORRECT - Create new config
def update_version(config: CompilerConfig, version: str) -> CompilerConfig:
    return CompilerConfig(**{**config.__dict__, "version": version})
```

### 4. Missing Type Hints on Public APIs

```python
# ❌ WRONG - No type hints
def compile_project(config):
    pass

# ✅ CORRECT - Full type hints
def compile_project(config: CompilerConfig) -> bool:
    pass
```

### 5. Generic Exceptions

```python
# ❌ WRONG - Generic exception
raise Exception("Compilation failed")

# ✅ CORRECT - Specific exception
raise CompilationError(f"PyInstaller failed: {error}") from error
```

---

## Further Reading

After understanding this guide, consult:

1. **[core/advanced-cognitive-conduct.md](core/advanced-cognitive-conduct.md)** - Decision-making framework
2. **[languages/python/pyproject-standards.md](languages/python/pyproject-standards.md)** - Configuration standards
3. **[languages/python/python-development-standards.md](languages/python/python-development-standards.md)** - Python best practices
4. **[languages/python/python-formatting-standards.md](languages/python/python-formatting-standards.md)** - Code formatting

---

## Summary

**EzCompiler** is built on:

✅ **Clear Architecture** - Layered design with strict dependency flow
✅ **Configuration-Driven** - Single source of truth (`CompilerConfig`)
✅ **Type Safety** - Comprehensive type hints with Python 3.10+ syntax
✅ **Error Resilience** - Specific exceptions with chain preservation
✅ **Production Quality** - Logging, validation, testing at all layers

**When in doubt:**

1. Follow the layered architecture
2. Inject dependencies, don't create them
3. Use `CompilerConfig` for all configuration
4. Type hint everything public
5. Test critical paths and error cases

---

## Recent Improvements (2026-02-08)

### ✅ Type Hints Correction

**Issue:** Compiler implementations used incorrect type hints (`config: object`)

**Fix:** Updated all compiler `__init__` methods with proper type hints:

```python
# ❌ Before
def __init__(self, config: object) -> None:
    super().__init__(config)  # type: ignore[arg-type]

# ✅ After
def __init__(self, config: CompilerConfig) -> None:
    super().__init__(config)
```

**Impact:**

- Better IDE auto-completion
- Improved type checking with Pyright/mypy
- Removed unnecessary `# type: ignore` comments

**Files Updated:**

- `protocols/cx_freeze_compiler.py`
- `protocols/pyinstaller_compiler.py`
- `protocols/nuitka_compiler.py`

---

### ✅ Validators Refactoring

**Issue:** Monolithic `validation_utils.py` (762 lines, 26 methods in single class)

**Solution:** Modular `validators/` package with domain-specific modules

**New Structure:**

```text
utils/validators/
├── __init__.py              # Re-exports + public API
├── format_validators.py     # Version, email, URL (3 functions)
├── path_validators.py       # File, directory paths (2 functions)
├── type_validators.py       # Boolean, integer, type checking (4 functions)
├── value_validators.py      # Range, length, choice, not-empty (8 functions)
├── schema_validators.py     # Dict schema, config validation (4 functions)
├── domain_validators.py     # Compiler, upload structure (2 functions)
├── string_validators.py     # Sanitize, pattern validation (2 functions)
└── meta_validators.py       # Meta-validation (1 function)
```

**Benefits:**

- ✅ Single Responsibility Principle per module
- ✅ Easier navigation (~80-150 lines per file vs 762)
- ✅ Better testability (tests organized by category)
- ✅ Improved maintainability
- ✅ Backward compatible via `__init__.py` re-exports

**Migration:**

```python
# Old usage (still works via backward compatibility)
from ezcompiler.utils.validators import validate_email

# New direct import (recommended)
from ezcompiler.utils.validators.format_validators import validate_email
```

**Impact:**

- 1 monolithic file → 9 focused modules
- Improved code organization
- Follows project standards (domain-specific utilities)

---

_Last Updated: 2026-02-08_
_Project Version: 2.1.0_
