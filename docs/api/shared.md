# Shared Layer

Configuration dataclasses and exception hierarchy for **EzCompiler**.

The shared layer contains data structures and exceptions used across all layers of the framework.

---

## Configuration

### CompilerConfig

Main configuration dataclass containing all compilation settings.

::: ezcompiler.shared.compiler_config.CompilerConfig

---

## Exceptions

### Base Exceptions

#### EzCompilerError

Base exception class for all EzCompiler errors.

::: ezcompiler.shared.exceptions.utils.base.EzCompilerError

---

### Service Exceptions

Exceptions raised by service layer components.

#### CompilationError

Exception raised when compilation fails.

::: ezcompiler.shared.exceptions.services.service_exceptions.CompilationError

---

#### ConfigurationError

Exception raised when configuration is invalid.

::: ezcompiler.shared.exceptions.services.service_exceptions.ConfigurationError

---

#### TemplateServiceError

Exception raised when template processing fails.

::: ezcompiler.shared.exceptions.services.service_exceptions.TemplateServiceError

---

#### UploaderServiceError

Exception raised when upload operations fail.

::: ezcompiler.shared.exceptions.services.service_exceptions.UploaderServiceError

---

#### CompilerServiceError

Exception raised when compiler service operations fail.

::: ezcompiler.shared.exceptions.services.service_exceptions.CompilerServiceError

---

### Utils Exceptions

Exceptions raised by utility modules.

#### ValidationError

Exception raised when validation fails.

::: ezcompiler.shared.exceptions.utils.validation_exceptions.ValidationError

---

#### FileError

Exception raised when file operations fail.

::: ezcompiler.shared.exceptions.utils.file_exceptions.FileError

---

#### ConfigError

Exception raised when configuration parsing fails.

::: ezcompiler.shared.exceptions.utils.config_exceptions.ConfigError

---

#### ZipError

Exception raised when ZIP operations fail.

::: ezcompiler.shared.exceptions.utils.zip_exceptions.ZipError

---

#### TemplateProcessingError

Exception raised when template operations fail.

::: ezcompiler.shared.exceptions.utils.template_exceptions.TemplateProcessingError

---

#### UploadError

Exception raised when uploader operations fail.

::: ezcompiler.shared.exceptions.utils.uploader_exceptions.UploadError

---

#### CompilerError

Exception raised when compiler operations fail.

::: ezcompiler.shared.exceptions.utils.compiler_exceptions.CompilerError
