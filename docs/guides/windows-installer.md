# How to build a Windows installer

Package a compiled bundle into a first-deployment `setup.exe` with Inno Setup.

## 🔧 Prerequisites

- A working compiler configuration (see [Configuration](configuration.md)).
- [Inno Setup 6](https://jrsoftware.org/isdl.php) installed on the build machine.
  Make `ISCC.exe` available on `PATH`, use its default Program Files installation,
  or set `installer.iscc_path` explicitly.

Jinja2 is a runtime dependency of ezcompiler and renders generated installer
scripts. Inno Setup remains an external application: no PyPI package or
ezcompiler extra replaces its `ISCC.exe` compiler.

## 📝 Enable the installer

Add a nested installer section to the project's `pyproject.toml`:

```toml
[tool.ezcompiler.installer]
enabled = true
per_user = true
```

For the Python API, pass an `InstallerConfig` to `CompilerConfig`:

```python
from pathlib import Path

from ezplog import Ezpl

from ezcompiler import CompilerConfig, EzCompiler
from ezcompiler.shared import InstallerConfig

Ezpl()  # Initialize logging in the host application.
config = CompilerConfig(
    version="1.0.0",
    project_name="MyApp",
    main_file="main.py",
    include_files={"files": [], "folders": []},
    output_folder=Path("dist/pyinstaller_build"),
    compiler="PyInstaller",
    installer=InstallerConfig(enabled=True, per_user=True),
)
compiler = EzCompiler(config)
compiler.run_pipeline(console=False)
```

The installer stage runs after `zip` and before `release`. This example produces
`dist/installer/MyApp-1.0.0-setup.exe`. Use
`compiler.run_pipeline(skip_installer=True)` to skip it for one run.

The default system-wide installation uses `{autopf}\MyApp` and requires admin
rights. Set `per_user = true` for `%LOCALAPPDATA%\Programs\MyApp` with
`PrivilegesRequired=lowest`. Per-user installation allows a
[tufup updater](secure-updates-tufup.md) running as the logged-in user to replace
application files without elevation.

The CLI can scaffold the enabled section:

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py" --installer-enabled
```

## Choose a script mode

| Mode | Selection | Behavior |
| :--- | :-------- | :------- |
| Ephemeral | Leave `iss_path` unset | Render the bundled Jinja2 template to a temporary UTF-8 BOM `.iss`, compile it, and remove it on success. No script is left in `installer.output_dir`. A failed ISCC invocation retains the script for diagnosis. |
| Generated | Run `ezcompiler generate iss` | Write an editable, committable UTF-8 BOM script, by default `installer/<project_name>.iss`. Generation does not run ISCC or automatically adopt the file. |
| File | Set `iss_path` | Pass the existing `.iss` directly to ISCC. Its contents are authoritative; they are neither re-rendered with Jinja2 nor rewritten. |

Generate and then adopt a script when the typed options are insufficient:

```bash
ezcompiler generate iss
# Or choose another destination:
ezcompiler generate iss --output installer/custom.iss
```

```toml
[tool.ezcompiler.installer]
enabled = true
iss_path = "installer/custom.iss"
```

An existing destination is protected from overwriting. Use
`ezcompiler generate iss --force` when you want to replace it with a fresh render
of the configuration; hand edits will be lost. Generation can run while the
installer stage is disabled and does not require ISCC.

!!! warning "The file wins"
    With `iss_path` set, the script-generation options in the table below do not
    change the file. The pipeline warns by name about non-default ignored
    options. `enabled`, `iss_path`, `output_dir`, and `iscc_path` still control the
    build, and the signing pair still supplies ISCC's `/S` registration; a custom
    script must select the matching `SignTool` itself.

The top-level compiler `icon` supplies `SetupIconFile` and must be a `.ico` when
the installer is enabled. Ephemeral builds resolve it to an absolute path.
Generated scripts preserve a relative icon path and warn that ISCC resolves it
relative to the `.iss` directory, rather than the current working directory.
Adjust the path in the adopted script accordingly.

## Stable identity and build values

The rendered script stores `MyAppName`, `MyAppPublisher`, and a stable `AppId`.
Unless explicitly set, the GUID derives deterministically from `company_name`
and `project_name`, independently of the version or machine. Changing either
name changes that derived identity; set an explicit `app_id` if the product must
keep its identity across a rename. In the script, a literal GUID uses
`AppId={{GUID}`: the opening brace is doubled, the closing brace stays single.

Every build passes five volatile values as ISCC `/D` preprocessor defines:

| Define | Value supplied for the current build | Script consumer |
| :----- | :----------------------------------- | :-------------- |
| `MyAppVersion` | `CompilerConfig.version` | `AppVersion` and the setup filename |
| `VersionInfo` | Numeric four-part version, e.g. `1.2.3.0` from `1.2.3-rc1` | `VersionInfoVersion` |
| `BundleDir` | Absolute compiled bundle directory | `[Files]` source |
| `OutputDir` | Absolute installer output directory | `OutputDir` |
| `MainExe` | Detected executable name at the bundle root | Shortcuts and post-install launch |

The adapter chooses the sole bundle-root `.exe`, otherwise the executable
matching the project name; an unresolved ambiguity is an error.

Generated standalone scripts provide fallback values inside `#ifndef` guards
for those five defines. ezcompiler's build values override the guarded defaults.
Keep these guards and `{#MyAppVersion}` references when editing a committed
script. A hardcoded `AppVersion=1.0.0` or an unconditional
`#define MyAppVersion "1.0.0"` can compile the old version even when the project
configuration has advanced. `VersionInfo` is supplied separately so a release
suffix is never sent to the numeric-only `VersionInfoVersion` directive.

## ⚙️ Installer options

This is the complete reference for the 24 `InstallerConfig` fields. TOML keys
live under `[tool.ezcompiler.installer]`; Python defaults use `None` for unset
paths or optional values. In TOML, omit those keys instead of writing `null`.
Effects describe generated scripts; file mode follows the rule above.

| Option | Default | Effect on the `.iss` or compiler invocation |
| :----- | :------ | :----------------------------------------- |
| `enabled` | `False` | Enable the pipeline's installer stage; emits no directive. |
| `iss_path` | `None` | Use this existing script directly instead of rendering the template. |
| `output_dir` | `None` | Resolve to `output_folder.parent / "installer"`; supply `/DOutputDir` for the script's `OutputDir`. Receives the setup executable. |
| `iscc_path` | `None` | Explicit compiler binary; otherwise discover ISCC on `PATH` or in default Inno Setup 6 Program Files directories. |
| `app_id` | `None` | Stable `AppId`; derive a UUIDv5 from company/project names, or use an explicit `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}` GUID. |
| `publisher_url` | `""` | Emit `AppPublisherURL` when non-empty. |
| `support_url` | `""` | Emit `AppSupportURL` when non-empty. |
| `updates_url` | `""` | Emit `AppUpdatesURL` when non-empty. |
| `architecture` | `"x64"` | Emit `ArchitecturesAllowed` and `ArchitecturesInstallIn64BitMode` with the selected value (`x64`, `x86`, or `arm64`); `auto` omits both and leaves Inno's defaults in effect. |
| `per_user` | `False` | Select `{autopf}\<App>` with `PrivilegesRequired=admin`, or `{localappdata}\Programs\<App>` with `PrivilegesRequired=lowest`. |
| `desktop_icon` | `True` | Emit an optional, initially unchecked `desktopicon` task and its `[Icons]` entry; disabling it omits both. |
| `start_menu_group` | `None` | Set `DefaultGroupName`; default to the project name. A Start Menu shortcut is always emitted. |
| `launch_after_install` | `True` | Emit the `[Run]` launch entry with `postinstall` and `skipifsilent`; disabling it omits that entry. |
| `add_to_path` | `False` | Append `{app}` to the user's `HKCU\Environment\Path` through `[Registry]`; uses `preservestringtype`. A generated `[Code]` block guards against duplicate entries on reinstall and removes the entry again at uninstall (never `uninsdeletevalue`, which would wipe the whole `Path`). Defining your own `CurUninstallStepChanged` in `extra_sections.Code` collides with it. |
| `close_running_app` | `True` | Emit `CloseApplications=force` and `RestartApplications=yes` (an unattended upgrade closes the running app instead of prompting); `False` omits both directives rather than explicitly setting them to `no`. |
| `uninstall_delete` | `[]` | Emit each value verbatim as a `[UninstallDelete]` `Name` with `Type: filesandordirs`; use application-relative entries such as `{app}\cache`. Absolute paths and `..` segments are rejected. |
| `license_file` | `None` | Emit `LicenseFile`; the supplied file must exist when enabled. |
| `languages` | `["english"]` | Emit `[Languages]`: English uses `compiler:Default.isl`, others use bundled language files. Names must be supported, non-empty, and unique, e.g. `["english", "french"]`. |
| `wizard_style` | `"modern"` | Emit `WizardStyle` (`modern` or `classic`). |
| `compression` | `"lzma2/max"` | Emit `Compression`; `SolidCompression=yes` is always emitted. ISCC validates the algorithm. |
| `sign_tool_name` | `None` | Emit `SignTool` and register the command with ISCC's `/S`; must be paired with `sign_tool_command`. |
| `sign_tool_command` | `None` | Supply the command in `/S<name>=<command>`; must be paired with `sign_tool_name`. |
| `extra_setup_directives` | `{}` | Append raw additional `[Setup]` directives; managed directive collisions are rejected case-insensitively. |
| `extra_sections` | `{}` | Append raw lines in additional sections; collisions with managed section names are rejected case-insensitively. |

Shape validation also runs when the stage is disabled. Existing `iss_path` and
`license_file` checks run when enabled. Invalid installer options raise
`ConfigurationError`.

## Extend the generated script

Use the two escape hatches for Inno features outside the typed option set:

```toml
[tool.ezcompiler.installer.extra_setup_directives]
DisableProgramGroupPage = "yes"
SetupLogging = "yes"

[tool.ezcompiler.installer.extra_sections]
Code = [
  "function InitializeSetup(): Boolean;",
  "begin",
  "  Result := True;",
  "end;",
]
```

`extra_setup_directives` contains raw `key=value` lines inside `[Setup]`.
`extra_sections` contains section names without brackets and lists of raw lines.
Both bypass typed-value escaping: write valid Inno syntax yourself, including
quotes and constants. Typed literal values escape only `{` to `{{`; quotes,
newlines, carriage returns, and tabs in those values raise `InstallerRenderError`.

Do not override directives owned by the typed configuration, such as `AppId`,
`AppVersion`, `DefaultDirName`, or `OutputDir`. Managed sections are `Setup`,
`Files`, `Icons`, `Run`, `Tasks`, `Languages`, `Registry`, and `UninstallDelete`.
Collisions with these managed names raise `ConfigurationError` even if that
section would be omitted for the current options. Adopt a generated file when
you need to edit those directives or sections.

## Migration 4.0.0

### Move flat TOML keys into the installer section

The old `installer_enabled`, `installer_iss_path`, `installer_output_dir`, and
`installer_per_user` keys are removed. Flat `installer_*` keys passed through
configuration loading raise an explicit `ConfigurationError` naming the keys
and the required nested section. For example, replace:

```toml
[tool.ezcompiler]
installer_enabled = true
installer_per_user = true
installer_output_dir = "dist/installer"
```

with:

```toml
[tool.ezcompiler.installer]
enabled = true
per_user = true
output_dir = "dist/installer"
```

### Update Python constructors

Removed flat constructor keywords raise Python's `TypeError` for an unexpected
keyword argument. Use `installer=InstallerConfig(enabled=True, per_user=True)`
in `CompilerConfig(...)`; import `InstallerConfig` from `ezcompiler.shared`.

### Regenerate legacy scripts

Custom scripts using `#APP_NAME#`, `#VERSION#`, `#BUNDLE_DIR#`, or other
`#TOKEN#` placeholders are no longer substituted. Generate a replacement with
`ezcompiler generate iss --output installer/v4.iss`, carry your manual changes
over, then set `iss_path` to the replacement.

The generation engine now uses Jinja2 with `<% ... %>` blocks, `<< ... >>`
expressions, and `<# ... #>` comments. These delimiters avoid collisions with
Inno's `{#Define}` and `{{` syntax. The emitted `.iss` contains resolved values
and Inno preprocessor references, not Jinja2 expressions; file-mode scripts are
compiled directly. Save manual edits as UTF-8 with a BOM to retain accented text.

## ✅ Result and errors

The pipeline produces `<project_name>-<version>-setup.exe` in
`installer.output_dir`, or `output_folder.parent / "installer"` by default.
A custom script must use the current output directory and that filename;
otherwise the adapter raises `InstallerBuildError` even if ISCC exits successfully.
When TUF is enabled, the explicit `upload()` step also includes the installer in
the release directory alongside the ZIP; see [Release pipeline](../concepts/about-release-pipeline.md).

| Exception | Raised when |
| :-------- | :---------- |
| `ConfigurationError` | Installer options are invalid, legacy flat keys are loaded, or an enabled configured script/license file does not exist. |
| `TypeError` | Removed flat installer keywords are passed to the Python `CompilerConfig` constructor. |
| `IsccNotFoundError` | ISCC cannot be found and no explicit compiler path was supplied. |
| `InstallerRenderError` | Jinja2 rendering fails or a typed literal value contains unsupported characters. |
| `InstallerBuildError` | ISCC exits unsuccessfully, or its expected setup executable is missing after a successful invocation. An ISCC failure retains the ephemeral script and reports its path. |
| `InstallerConfigError` | The bundle is missing/empty, its main executable cannot be identified, the script is missing at build time, or generation would overwrite an existing file without `--force`. |
| `InstallerTypeError` | An unsupported installer backend was requested. |

Installer exceptions can be imported from `ezcompiler.shared.exceptions`.
They derive from `InstallerError`. Let real compiler failures propagate so the
build cannot silently publish an incomplete result.
