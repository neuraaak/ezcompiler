# Shared Layer

Configuration dataclasses and exception hierarchy for **EzCompiler**.

The shared layer contains data structures and exceptions used across all layers of the framework.

!!! note "Public imports"
    All shared symbols are re-exported from the package roots. Always import from
    `ezcompiler.shared` (or `ezcompiler.shared.exceptions`) — never from the
    underscore-prefixed private modules (e.g. `_compiler_config`).

---

## Configuration

### CompilerConfig

Main configuration dataclass containing all compilation settings.

```python
from ezcompiler.shared import CompilerConfig
```

::: ezcompiler.shared.CompilerConfig

---

### CompilationResult

Result type returned by compilation operations.

```python
from ezcompiler.shared import CompilationResult
```

::: ezcompiler.shared.CompilationResult

---

## Exceptions

### Base Exceptions

#### EzCompilerError

Base exception class for all EzCompiler errors.

```python
from ezcompiler.shared.exceptions import EzCompilerError
```

::: ezcompiler.shared.exceptions.EzCompilerError

---

### Service Exceptions

Exceptions raised by service layer components.

```python
from ezcompiler.shared.exceptions.services import (
    CompilationError,
    ConfigurationError,
    TemplateServiceError,
    UploaderServiceError,
    CompilerServiceError,
)
```

#### CompilationError

Exception raised when compilation fails.

::: ezcompiler.shared.exceptions.services.CompilationError

---

#### ConfigurationError

Exception raised when configuration is invalid.

::: ezcompiler.shared.exceptions.services.ConfigurationError

---

#### TemplateServiceError

Exception raised when template processing fails.

::: ezcompiler.shared.exceptions.services.TemplateServiceError

---

#### UploaderServiceError

Exception raised when upload operations fail.

::: ezcompiler.shared.exceptions.services.UploaderServiceError

---

#### CompilerServiceError

Exception raised when compiler service operations fail.

::: ezcompiler.shared.exceptions.services.CompilerServiceError

---

### Utils Exceptions

Exceptions raised by utility modules. `ConfigError`, `ZipError`, and
`UploadError` are re-exported from `ezcompiler.shared.exceptions`. The
remaining utility-layer exceptions are accessed via
`ezcompiler.shared.exceptions.utils`.

```python
from ezcompiler.shared.exceptions import ConfigError, ZipError, UploadError
from ezcompiler.shared.exceptions.utils import (
    ValidationError,
    FileError,
    TemplateProcessingError,
    CompilerError,
)
```

#### ValidationError

Exception raised when validation fails.

::: ezcompiler.shared.exceptions.utils.ValidationError

---

#### FileError

Exception raised when file operations fail.

::: ezcompiler.shared.exceptions.utils.FileError

---

#### ConfigError

Exception raised when configuration parsing fails.

::: ezcompiler.shared.exceptions.ConfigError

---

#### ZipError

Exception raised when ZIP operations fail.

::: ezcompiler.shared.exceptions.ZipError

---

#### TemplateProcessingError

Exception raised when template operations fail.

::: ezcompiler.shared.exceptions.utils.TemplateProcessingError

---

#### UploadError

Exception raised when uploader operations fail.

::: ezcompiler.shared.exceptions.UploadError

---

#### CompilerError

Exception raised when compiler operations fail.

::: ezcompiler.shared.exceptions.utils.CompilerError
