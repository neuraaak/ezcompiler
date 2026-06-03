# How to configure a compiler

Select and configure a compilation backend for an EzCompiler project.

## 🔧 Prerequisites

- EzCompiler installed (`uv add ezcompiler` or `pip install ezcompiler`)
- Target backend installed: `cx-freeze`, `pyinstaller`, or `nuitka`
- A `main.py` (or equivalent) entry point for your project

## 📝 Steps

1. Create a `CompilerConfig` with the required fields.

    ```python
    from ezcompiler import EzCompiler, CompilerConfig

    config = CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder="dist",
        compiler="PyInstaller",
    )
    ```

2. Pass the config to `EzCompiler` and compile.

    ```python
    ezcompiler = EzCompiler(config)
    ezcompiler.compile_project()
    ```

3. Add compiler-specific options when needed.

    ```python
    config = CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file="main.py",
        include_files={"files": ["icon.ico"], "folders": ["assets"]},
        output_folder="dist",
        compiler="PyInstaller",
        packages=["requests", "pandas"],
        excludes=["debugpy", "pytest"],
        compiler_options={"onefile": True, "windowed": False},
    )
    ```

    ??? note "Why pass packages and excludes?"
        Compilation backends do not auto-discover every transitive dependency.
        Listing `packages` ensures they are bundled; `excludes` reduces binary size
        by stripping development-only tools.

4. Load configuration from a YAML or JSON file instead of inline code.

    === "YAML"

        ```yaml
        # ezcompiler.yaml
        version: "1.0.0"
        project_name: "MyApp"
        main_file: "main.py"
        output_folder: "dist"
        compiler: "PyInstaller"
        packages:
          - "requests"
        excludes:
          - "debugpy"
        include_files:
          files: ["config.yaml"]
          folders: ["assets"]
        compiler_options:
          onefile: true
        ```

    === "Python"

        ```python
        import yaml
        from ezcompiler import EzCompiler, CompilerConfig

        with open("ezcompiler.yaml") as f:
            config = CompilerConfig.from_dict(yaml.safe_load(f))

        EzCompiler(config).compile_project()
        ```

## ⚙️ Variations

Choose the backend that matches your distribution requirements.

=== "PyInstaller — single file"

    ```python
    config = CompilerConfig(
        ...,
        compiler="PyInstaller",
        compiler_options={"onefile": True, "windowed": False},
    )
    ```

=== "Cx_Freeze — directory build"

    ```python
    config = CompilerConfig(
        ...,
        compiler="Cx_Freeze",
        compiler_options={
            "zip_include_packages": ["*"],
            "zip_exclude_packages": ["test"],
            "include_msvcr": True,
            "optimize": 2,
        },
    )
    ```

=== "Nuitka — native compilation"

    ```python
    config = CompilerConfig(
        ...,
        compiler="Nuitka",
        compiler_options={"onefile": True, "show-progress": True},
    )
    ```

## ✅ Result

Your project compiles to the `output_folder` using the configured backend.
Explicit `packages`, `excludes`, and `compiler_options` give you full control
over binary size and distribution structure.
