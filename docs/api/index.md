# API reference

Curated index of the public **EzCompiler** API, organized by layer.

## 📦 Modules

| Component  | Description                                          | Page                        |
| :--------- | :--------------------------------------------------- | :-------------------------- |
| Interfaces | `EzCompiler` facade and `CLIInterface` entry points  | [Interfaces](interfaces.md) |
| Services   | Compiler, config, pipeline, template, upload logic   | [Services](services.md)     |
| Adapters   | Compiler and uploader factories and implementations  | [Adapters](adapters.md)     |
| Shared     | `CompilerConfig`, `CompilationResult`, exceptions    | [Shared](shared.md)         |
| Types      | `FilePath`, `CompilerName`, `UploadTarget`, etc.     | [Types](types.md)           |
| Utils      | File, config, template, zip utilities and validators | [Utils](utils.md)           |

## 🔍 Full reference

For the complete auto-generated API dump from docstrings, open [API auto-reference](reference/index.md).

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
