# API reference

Public API documentation for the **EzCompiler** framework, organized by layer.

## 📦 Modules

| Module                      | Description                                                                                 |
| :-------------------------- | :------------------------------------------------------------------------------------------ |
| [Interfaces](interfaces.md) | `EzCompiler` facade and `CLIInterface` — public entry points                                |
| [Services](services.md)     | `CompilerService`, `ConfigService`, `PipelineService`, `TemplateService`, `UploaderService` |
| [Adapters](adapters.md)     | Compiler and uploader concrete implementations                                              |
| [Shared](shared.md)         | `CompilerConfig`, `CompilationResult`, exception hierarchy                                  |
| [Types](types.md)           | Public type aliases — `FilePath`, `CompilerName`, `UploadTarget`, `IncludeFiles`, `JsonMap` |
| [Utils](utils.md)           | File, config, template, zip utilities and 9 validator modules                               |

## 🔍 Full reference

The exhaustive symbol listing (all classes, methods, and attributes generated from source docstrings) is available in [API auto-reference](reference/index.md).

## Import paths

```python
# Top-level public API
from ezcompiler import EzCompiler, CompilerConfig

# By layer
from ezcompiler.interfaces import EzCompiler
from ezcompiler.shared import CompilerConfig
from ezcompiler.services import CompilerService
from ezcompiler.adapters import CompilerFactory, UploaderFactory
```

!!! note "Visibility conventions"
    Concrete adapter classes (compilers, uploaders) are internal and accessed through their respective factories. Only `EzCompiler`, `CompilerConfig`, and the public type aliases in `types` are part of the stable public API.
