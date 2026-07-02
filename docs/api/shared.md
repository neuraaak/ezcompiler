# Shared layer

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

### Base exceptions

#### EzCompilerError

Base exception class for all EzCompiler errors.

```python
from ezcompiler.shared.exceptions import EzCompilerError
```

::: ezcompiler.shared.exceptions.EzCompilerError

---

### Service exceptions

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

### Utils exceptions

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

---

### Installer exceptions

Exceptions raised by installer packaging (Inno Setup).

```python
from ezcompiler.shared.exceptions import (
    InstallerError,
    InstallerTypeError,
    InstallerBuildError,
    InstallerConfigError,
    IsccNotFoundError,
)
```

#### InstallerError

Base exception for installer packaging errors.

::: ezcompiler.shared.exceptions.InstallerError

---

#### InstallerTypeError

Exception raised when the requested installer type is not supported.

::: ezcompiler.shared.exceptions.InstallerTypeError

---

#### IsccNotFoundError

Exception raised when the Inno Setup compiler (`ISCC.exe`) cannot be located.

::: ezcompiler.shared.exceptions.IsccNotFoundError

---

#### InstallerBuildError

Exception raised when running `ISCC.exe` against the `.iss` script fails.

::: ezcompiler.shared.exceptions.InstallerBuildError

---

#### InstallerConfigError

Exception raised when installer configuration is invalid or incomplete.

::: ezcompiler.shared.exceptions.InstallerConfigError

---

### Release exceptions

Exceptions raised by secure-release (TUF/tufup) operations.

```python
from ezcompiler.shared.exceptions import (
    ReleaseError,
    ReleaserTypeError,
    BundleBuildError,
    SigningKeyError,
    ReleaseConfigError,
)
```

#### ReleaseError

Base exception for secure-release operation errors.

::: ezcompiler.shared.exceptions.ReleaseError

---

#### ReleaserTypeError

Exception raised when the requested releaser type is not supported.

::: ezcompiler.shared.exceptions.ReleaserTypeError

---

#### BundleBuildError

Exception raised when building the release bundle archive fails.

::: ezcompiler.shared.exceptions.BundleBuildError

---

#### SigningKeyError

Exception raised when signing keys are missing, invalid, or inaccessible.

::: ezcompiler.shared.exceptions.SigningKeyError

---

#### ReleaseConfigError

Exception raised when release configuration is invalid or incomplete.

::: ezcompiler.shared.exceptions.ReleaseConfigError
