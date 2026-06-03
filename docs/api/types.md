# Types

Public type aliases for **EzCompiler**, importable directly from the top-level package.

All aliases defined here are re-exported via `ezcompiler.__init__` and appear in `__all__`,
so they are part of the stable public API.

---

## Overview

The `types` module centralizes common type aliases used throughout the library.
Import them when you want to annotate your own code that calls EzCompiler APIs,
or when building extensions on top of the framework.

```python
from ezcompiler import FilePath, CompilerName, UploadTarget, IncludeFiles, JsonMap
```

They can also be imported from the submodule directly:

```python
from ezcompiler.types import FilePath, IncludeFiles
```

---

## Path types

### FilePath

```python
FilePath: TypeAlias = str | Path
```

Accepted wherever a file system path is expected (configuration fields, template loaders,
file utility functions). Both a plain string and a `pathlib.Path` object are valid.

```python
from pathlib import Path
from ezcompiler import FilePath, CompilerConfig

def load_config(path: FilePath) -> CompilerConfig:
    ...
```

---

## Compiler types

### CompilerName

```python
CompilerName: TypeAlias = str
```

Narrows the `compiler` parameter to the set of recognized backend names.

Valid values: `"auto"`, `"Cx_Freeze"`, `"PyInstaller"`, `"Nuitka"`

```python
from ezcompiler import CompilerName, EzCompiler, CompilerConfig

def build(compiler: CompilerName) -> None:
    config = CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
    )
    EzCompiler(config).compile_project(compiler=compiler)
```

### UploadTarget

```python
UploadTarget: TypeAlias = str
```

Narrows the `structure` parameter of upload operations.

Valid values: `"disk"`, `"server"`

```python
from ezcompiler import UploadTarget

def upload(target: UploadTarget, destination: str) -> None:
    ...
```

---

## Configuration types

### IncludeFiles

```python
IncludeFiles: TypeAlias = dict[str, list[str]]
```

Expected shape for the `include_files` field of `CompilerConfig`:

```python
{
    "files": ["path/to/config.yaml", "path/to/data.dll"],
    "folders": ["path/to/assets/", "path/to/locale/"],
}
```

Both keys are required. Pass empty lists when no files or folders should be included.

```python
from ezcompiler import IncludeFiles, CompilerConfig

bundle: IncludeFiles = {
    "files": ["settings.yaml"],
    "folders": ["assets"],
}
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files=bundle,
    output_folder="dist",
)
```

### JsonMap

```python
JsonMap: TypeAlias = dict[str, object]
```

Generic mapping for JSON-serializable data. Used internally by configuration parsers,
template renderers, and YAML/JSON loaders. Useful when passing raw config dictionaries.

```python
from ezcompiler import JsonMap

raw: JsonMap = {"version": "1.0.0", "project_name": "MyApp"}
```

---

## API reference

::: ezcompiler.types
    options:
      show_source: false
      members:
        - FilePath
        - CompilerName
        - UploadTarget
        - IncludeFiles
        - JsonMap
