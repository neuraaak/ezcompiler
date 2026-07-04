# How to build a Windows installer

Package a compiled bundle into a first-deployment `setup.exe` with Inno Setup, so end users get a standard Windows installer instead of a raw ZIP.

## 🔧 Prerequisites

- A working `CompilerConfig` that already compiles your project (see [How to configure a compiler](configuration.md))
- [Inno Setup 6](https://jrsoftware.org/isdl.php) installed, with `ISCC.exe` on `PATH` (or in its default `Program Files` location)

!!! note "No PyPI dependency"
    The installer stage shells out to `ISCC.exe` — there is no `pip install ezcompiler[...]` extra to add. Only the Inno Setup compiler itself needs to be installed on the build machine.

## 📝 Steps

1. Enable the installer stage in your config.

    ```python
    from pathlib import Path
    from ezcompiler import EzCompiler, CompilerConfig

    config = CompilerConfig(
        version="1.0.0",
        project_name="MyApp",
        main_file="main.py",
        include_files={"files": [], "folders": []},
        output_folder=Path("dist/pyinstaller_build"),
        compiler="PyInstaller",
        installer_enabled=True,
    )
    ```

2. Run the build pipeline. The installer stage runs automatically after `zip` when `installer_enabled=True`.

    ```python
    compiler = EzCompiler(config)
    compiler.run_pipeline(console=False)
    ```

    This produces `dist/installer/MyApp-1.0.0-setup.exe` by default — see the config reference below to change the location.

3. Point at a custom `.iss` script if the generated one doesn't fit your needs.

    ```python
    config = CompilerConfig(
        ...,
        installer_enabled=True,
        installer_iss_path=Path("installer/custom.iss"),
    )
    ```

    Your script can reuse the same `#PLACEHOLDER#` tokens as the built-in template (`#APP_NAME#`, `#VERSION#`, `#COMPANY_NAME#`, `#BUNDLE_DIR#`, `#OUTPUT_DIR#`, `#ICON_LINE#`, `#MAIN_EXE#`, `#DEFAULT_DIR#`, `#PRIVILEGES_REQUIRED#`).

4. Skip the installer for a single run without touching the config.

    ```python
    compiler.run_pipeline(skip_installer=True)
    ```

5. Install per-user instead of system-wide if the app also uses [TUF secure updates](secure-updates-tufup.md).

    ```python
    config = CompilerConfig(
        ...,
        installer_enabled=True,
        installer_per_user=True,
    )
    ```

    By default the installer targets `{autopf}\<App>` (Program Files) and requires admin rights (`PrivilegesRequired=admin`). A tufup auto-update runs as the logged-in user and cannot elevate to overwrite files there. Set `installer_per_user=True` to install into `%LOCALAPPDATA%\Programs\<App>` instead, with `PrivilegesRequired=lowest` — no elevation needed to install, and none needed later for auto-update to replace files in place.

## ⚙️ Config reference

| Field                  | Default                              | Description                                                                                                                                                |
| :--------------------- | :----------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `installer_enabled`    | `False`                              | Turn on the installer build stage                                                                                                                          |
| `installer_output_dir` | `output_folder.parent / "installer"` | Directory receiving the generated `.iss` and the compiled `setup.exe`                                                                                      |
| `installer_iss_path`   | `None` (built-in template)           | Path to a custom `.iss` script, overriding the bundled one                                                                                                 |
| `installer_per_user`   | `False`                              | Install to `%LOCALAPPDATA%\Programs` with `PrivilegesRequired=lowest` instead of Program Files with admin rights — required for tufup in-place auto-update |

## 💻 CLI

Enable the stage from the `generate config` command:

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py" --installer-enabled
```

## ✅ Result

`run_pipeline()` produces `{project_name}-{version}-setup.exe` in `installer_output_dir`. When `tuf_enabled=True`, `upload()` also copies it into the assembled `release/` directory alongside the ZIP, so it ships with the rest of the release artifacts — see [Release pipeline](../concepts/about-release-pipeline.md).

## Error handling

| Exception              | Raised when                                                          |
| :--------------------- | :------------------------------------------------------------------- |
| `IsccNotFoundError`    | `ISCC.exe` is not on `PATH` or in a default install dir              |
| `InstallerBuildError`  | `ISCC.exe` exits with a non-zero status                              |
| `InstallerConfigError` | `bundle_dir` is missing/empty, or `installer_iss_path` doesn't exist |
| `InstallerTypeError`   | An unsupported `installer_type` was requested                        |

```python
from ezcompiler.shared.exceptions import IsccNotFoundError, InstallerBuildError

try:
    compiler.run_pipeline()
except IsccNotFoundError:
    print("Install Inno Setup 6 and ensure ISCC.exe is on PATH.")
except InstallerBuildError as e:
    print(f"Installer build failed: {e}")
```
