# Utils Layer

Utility functions, file operations, and validation modules for **EzCompiler**.

The utils layer provides reusable utilities for file management, configuration parsing, template processing, ZIP operations, and comprehensive validation.

!!! note "Public imports"
    All utility classes are re-exported from `ezcompiler.utils`. Always import
    from the package root, never from the underscore-prefixed private modules.

    ```python
    from ezcompiler.utils import (
        FileUtils,
        ConfigUtils,
        TemplateProcessor,
        CompilerUtils,
        UploaderUtils,
        ZipUtils,
    )
    ```

---

## File Utilities

Utilities for file and directory operations.

::: ezcompiler.utils.FileUtils

---

## Configuration Utilities

Utilities for parsing and validating configuration files (YAML/JSON).

::: ezcompiler.utils.ConfigUtils

---

## Template Utilities

Utilities for template processing and variable substitution.

::: ezcompiler.utils.TemplateProcessor

---

## Compiler Utilities

Utilities for compiler-specific operations.

::: ezcompiler.utils.CompilerUtils

---

## Uploader Utilities

Utilities for upload operations.

::: ezcompiler.utils.UploaderUtils

---

## ZIP Utilities

Utilities for creating and managing ZIP archives.

::: ezcompiler.utils.ZipUtils

---

## Validators

Comprehensive validation package with 9 specialized modules.

### Domain Validators

Validators for domain-specific entities (URLs, emails, etc.).

::: ezcompiler.utils.validators.domain_validators

---

### Format Validators

Validators for data format validation.

::: ezcompiler.utils.validators.format_validators

---

### Meta Validators

Meta-validators for composite and conditional validation.

::: ezcompiler.utils.validators.meta_validators

---

### Path Validators

Validators for file and directory paths.

::: ezcompiler.utils.validators.path_validators

---

### Schema Validators

Validators for structured data schemas.

::: ezcompiler.utils.validators.schema_validators

---

### String Validators

Validators for string format and content.

::: ezcompiler.utils.validators.string_validators

---

### Type Validators

Validators for Python type checking and validation.

::: ezcompiler.utils.validators.type_validators

---

### Value Validators

Validators for value ranges and constraints.

::: ezcompiler.utils.validators.value_validators
