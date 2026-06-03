# Getting started

Build a working EzCompiler setup and compile your first project in a few minutes.

## 🔧 Prerequisites

- Python >= 3.11
- One compilation backend: `cx-freeze`, `pyinstaller`, or `nuitka`
- PyYAML >= 6.0

## 📝 Steps

### 1. Install EzCompiler

=== "uv"

    ```bash
    uv add ezcompiler
    ```

=== "pip"

    ```bash
    pip install ezcompiler
    ```

### 2. Install a compilation backend

=== "PyInstaller"

    ```bash
    pip install pyinstaller
    ```

=== "Cx_Freeze"

    ```bash
    pip install cx-freeze
    ```

=== "Nuitka"

    ```bash
    pip install nuitka
    ```

### 3. Create a configuration

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",  # (1)!
    include_files={"files": [], "folders": []},
    output_folder="dist",
)
```

1. Path to the main Python entry point of your project.

### 4. Compile and run the full pipeline

```python
ezcompiler = EzCompiler(config)

ezcompiler.compile_project(compiler="PyInstaller")  # (1)!
ezcompiler.zip_compiled_project()                   # (2)!
ezcompiler.upload_to_repo(                          # (3)!
    structure="disk",
    repo_path="./releases",
)
```

1. Compiles the project to the `output_folder`.
2. Creates a ZIP archive of the compiled output.
3. Copies the archive to a local release directory.

??? tip "✅ Success check"
    After `compile_project()` you should see the compiled output in `dist/`.
    After `zip_compiled_project()` a `.zip` archive appears alongside it.

## ✅ What you built

You now have a compiled, archived, and distributed Python project.
EzCompiler orchestrated all three steps — compile, package, upload — through a single typed API.

## ➡️ Next steps

- [How to configure a compiler](guides/configuration.md)
- [How to contribute changes locally](guides/development.md)
- [API reference](api/index.md)
- [CLI reference](cli/index.md)
- [Examples](examples/index.md)
