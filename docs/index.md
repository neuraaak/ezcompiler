# EzCompiler

[![PyPI version](https://img.shields.io/pypi/v/ezcompiler?style=flat&logo=pypi&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![Python versions](https://img.shields.io/pypi/pyversions/ezcompiler?style=flat&logo=python&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![PyPI status](https://img.shields.io/pypi/status/ezcompiler?style=flat&logo=pypi&logoColor=white)](https://pypi.org/project/ezcompiler/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat&logo=github&logoColor=white)](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/neuraaak/ezcompiler/01-ci.yml?style=flat&label=ci&logo=githubactions&logoColor=white)](https://github.com/neuraaak/ezcompiler/actions/workflows/01-ci.yml)
[![Docs](https://img.shields.io/badge/docs-Github%20Pages-blue?style=flat&logo=materialformkdocs&logoColor=white)](https://neuraaak.github.io/ezcompiler/)
[![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9?style=flat&logo=uv&logoColor=white)](https://github.com/astral-sh/uv)
[![linter](https://img.shields.io/badge/linter-ruff-D7FF64?style=flat&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![type checker](https://img.shields.io/badge/type%20checker-ty-261230?style=flat&logo=astral&logoColor=white)](https://github.com/astral-sh/ty)
[![tests](https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://github.com/pytest-dev/pytest)

![EzCompiler Logo](https://raw.githubusercontent.com/neuraaak/ezcompiler/refs/heads/main/docs/assets/logo-min.png)

**EzCompiler** is a Python framework for compiling projects to executables, packaging them as ZIP archives, and distributing them — through a single typed API.

## 🚀 Quick start

=== "uv"

    ```bash
    uv add ezcompiler
    ```

=== "pip"

    ```bash
    pip install ezcompiler
    ```

```python
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder="dist",
)

ezcompiler = EzCompiler(config)
ezcompiler.compile_project(compiler="PyInstaller")  # (1)!
ezcompiler.zip_compiled_project()
ezcompiler.upload(destination="./releases", structure="disk")
```

1. Supported backends: `"PyInstaller"`, `"Cx_Freeze"`, `"Nuitka"`.

## ✨ Key features

- Multi-backend compilation: Cx_Freeze, PyInstaller, and Nuitka.
- ZIP packaging with configurable compression.
- Disk and HTTP server upload backends.
- Template-based generation for config, setup, and version files.
- Complete Python 3.11+ type hints throughout the public API.

## 📚 Documentation

| Section                               | Description                                             |
| :------------------------------------ | :------------------------------------------------------ |
| [Getting Started](getting-started.md) | Tutorial for a working setup in a few minutes.          |
| [User Guides](guides/index.md)        | Task-focused configuration and operational recipes.     |
| [API Reference](api/index.md)         | Curated API map and auto-generated technical reference. |
| [CLI Reference](cli/index.md)         | Command and option reference for the CLI.               |
| [Examples](examples/index.md)         | Copy-paste runnable scenarios.                          |

## 📋 Requirements

- Python >= 3.11
- PyYAML >= 6.0
- cx_Freeze, PyInstaller, or Nuitka (at least one backend)

## ⚖️ License

MIT. See [LICENSE](https://github.com/neuraaak/ezcompiler/blob/main/LICENSE).
