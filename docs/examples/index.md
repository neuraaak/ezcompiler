# Examples

Runnable code examples for common EzCompiler scenarios.

!!! tip
    All examples assume the package is installed: `pip install ezcompiler`

---

## 🚀 Basic compilation

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="HelloWorld",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="PyInstaller")
```

## 💡 Configuration from YAML

```python
from ezcompiler import EzCompiler, CompilerConfig
import yaml

with open("ezcompiler.yaml") as f:
    config_dict = yaml.safe_load(f)

config = CompilerConfig.from_dict(config_dict)
ezcompiler = EzCompiler(config)
ezcompiler.compile_project()
```

YAML file (`ezcompiler.yaml`):

```yaml
version: "1.0.0"
project_name: "MyApp"
main_file: "main.py"
output_folder: "dist"
compiler: "PyInstaller"
packages:
  - "requests"
excludes:
  - "debugpy"
```

## 💡 Cx_Freeze — directory build

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": ["config.yaml"], "folders": ["assets", "data"]},
    output_folder="dist",
    compiler="Cx_Freeze",
    packages=["requests", "pandas"],
    excludes=["debugpy", "pytest"],
    compiler_options={
        "zip_include_packages": ["*"],
        "zip_exclude_packages": ["test"],
        "include_msvcr": True,
        "optimize": 2,
    },
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="Cx_Freeze")
```

## 💡 PyInstaller — single-file executable

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": ["icon.ico"], "folders": ["resources"]},
    output_folder="dist",
    compiler="PyInstaller",
    packages=["numpy", "scipy"],
    excludes=["matplotlib"],
    compiler_options={"onefile": True, "windowed": False, "log-level": "DEBUG"},
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="PyInstaller")
```

## 💡 Nuitka — optimized native compilation

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": ["data"]},
    output_folder="dist",
    compiler="Nuitka",
    packages=["fastapi", "uvicorn"],
    compiler_options={"onefile": True, "show-progress": True},
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="Nuitka")
```

## 💡 Full pipeline — compile, zip, upload to disk

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="ProductionApp",
    main_file="main.py",
    include_files={"files": ["config.yaml", "LICENSE"], "folders": ["assets"]},
    output_folder="dist",
    compiler="PyInstaller",
    packages=["requests", "pandas"],
    excludes=["debugpy", "pytest"],
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="PyInstaller")
ezcompiler.zip_compiled_project()
ezcompiler.upload(destination="./releases", structure="disk")
```

## 💡 Upload to HTTP server

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="2.1.0",
    project_name="WebApp",
    main_file="app.py",
    include_files={"files": [], "folders": ["static", "templates"]},
    output_folder="dist",
    compiler="Cx_Freeze",
    packages=["flask", "sqlalchemy"],
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="Cx_Freeze")
ezcompiler.zip_compiled_project()
ezcompiler.upload(
    destination="https://releases.example.com/upload",
    structure="server",
    upload_config={"username": "deploy_user", "password": "secure_password"},
)
```

## 💡 Error handling

```python
from ezcompiler import EzCompiler, CompilerConfig
from ezcompiler.shared.exceptions import (
    CompilationError,
    ConfigurationError,
    FileOperationError,
    UploadError,
)

config = CompilerConfig(
    version="1.0.0",
    project_name="RobustApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

try:
    ezcompiler = EzCompiler(config)
    ezcompiler.compile_project(compiler="PyInstaller")
    ezcompiler.zip_compiled_project()
    ezcompiler.upload(destination="./releases", structure="disk")
except ConfigurationError as e:
    raise SystemExit(1) from e
except CompilationError as e:
    raise SystemExit(2) from e
except FileOperationError as e:
    raise SystemExit(3) from e
except UploadError as e:
    raise SystemExit(4) from e
```

## 💡 Generate client updater files

```python
from pathlib import Path
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="2.0.0",
    project_name="MyApp",
    main_file="src/main.py",
    include_files={"files": [], "folders": []},
    output_folder=Path("dist"),
    tuf_enabled=True,
    tufup_repo_dir=Path("repo"),
    tufup_keys_dir=Path("keystore"),
    repo_public_url="https://updates.example.com/MyApp",
)

compiler = EzCompiler(config)
generated_files = compiler.generate_updater(output_dir=Path("src/updater"))
for path in generated_files:
    print(f"Generated: {path}")
# update.py, settings.py, root.json
```

## 💡 Template generation

```python
from ezcompiler.services import TemplateService

template_service = TemplateService()
config_content = template_service.process_template(
    template_name="config.yaml",
    variables={"PROJECT_NAME": "MyApp", "VERSION": "1.0.0", "MAIN_FILE": "main.py"},
)

with open("ezcompiler.yaml", "w") as f:
    f.write(config_content)
```
