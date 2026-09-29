# CLI reference

Command-line interface for **EzCompiler** — project initialization, file generation, and build automation.

## 💻 Usage

```bash
ezcompiler [OPTIONS] COMMAND [ARGS]...
```

## ⚙️ Global options

| Option      | Short | Description               |
| :---------- | :---- | :------------------------ |
| `--version` |       | Show the version and exit |
| `--help`    |       | Show help and exit        |
| `--verbose` |       | Enable verbose output     |
| `--quiet`   |       | Suppress non-error output |

## 📋 Commands

| Command             | Description                                                             |
| :------------------ | :---------------------------------------------------------------------- |
| `init`              | Initialize a new project interactively                                  |
| `compile`           | Compile the project (version → compile → zip)                           |
| `generate config`   | Generate a configuration file                                           |
| `generate build`    | Generate a `build.py` script from a configuration file                  |
| `generate iss`      | Generate an editable Inno Setup script from the configuration           |
| `generate version`  | Generate a Windows version information file                             |
| `generate template` | Generate a template file with optional mockup data                      |
| `upload`            | Upload the TUF tree and/or the release directory to their destination   |
| `release init`      | Initialize TUF signing keys and repository skeleton                     |
| `updater generate`  | Generate client updater files (`update.py`, `settings.py`, `root.json`) |

---

### `init`

Initialize a new EzCompiler project with interactive prompts.

```bash
ezcompiler init
```

Guides through: project name, main script, output directory, compiler selection, dependencies, and files to include.

---

### `compile`

Compile the project. Auto-discovers configuration from `pyproject.toml`, `ezcompiler.yaml`, or `ezcompiler.json`; CLI options override config file values.

```bash
ezcompiler compile --compiler PyInstaller --no-console
```

| Option                       | Required | Default | Description                                                               |
| :--------------------------- | :------- | :------ | :------------------------------------------------------------------------ |
| `--config`                   | No       | —       | Config file path (YAML, JSON)                                             |
| `--pyproject`                | No       | —       | Explicit `pyproject.toml` path                                            |
| `--compiler`                 | No       | —       | Compiler to use: `Cx_Freeze`, `PyInstaller`, `Nuitka` (overrides config)  |
| `--console` / `--no-console` | No       | —       | Show console window (overrides config)                                    |
| `--output-folder`            | No       | —       | Output folder (overrides config)                                          |
| `--debug`                    | No       | `False` | Enable debug mode                                                         |
| `--no-zip`                   | No       | `False` | Skip ZIP archive creation                                                 |
| `--skip-installer`           | No       | `False` | Skip the Inno Setup installer stage even if the installer is enabled      |
| `--skip-release`             | No       | `False` | Skip the TUF release stage even if `tuf_enabled=True`                     |
| `--skip-build`               | No       | `False` | Skip version + compile; resume from the existing build in `output_folder` |

!!! note "Pipeline stages"
    `compile` runs `version → compile → zip`, plus the installer and TUF release stages when enabled in the config (same behaviour as the Python API's `run_pipeline()`). Upload is a separate step: run `ezcompiler upload` afterwards.

!!! tip "Resuming after a build"
    If the project was already compiled, `ezcompiler compile --skip-build` reuses the existing `output_folder` and only runs the remaining stages (zip, installer and TUF release when enabled). It fails if `output_folder` is missing or empty.

---

### `generate config`

Create a configuration file.

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py"
```

| Option                | Required | Default             | Description                                              |
| :-------------------- | :------- | :------------------ | :------------------------------------------------------- |
| `--project-name`      | Yes      | —                   | Project name                                             |
| `--main-file`         | Yes      | —                   | Main Python file                                         |
| `--version`           | No       | `"1.0.0"`           | Project version                                          |
| `--output`            | No       | `"ezcompiler.yaml"` | Output file path                                         |
| `--format`            | No       | `yaml`              | Output format (`yaml`, `json`, or `pyproject`)           |
| `--installer-enabled` | No       | `False`             | Enable the Inno Setup installer build stage              |
| `--repo-public-url`   | No       | —                   | Public base URL for the TUF repo (required for `r2`/TUF) |

---

### `generate iss`

Generate an editable Inno Setup script from the project configuration.

Auto-discovers `pyproject.toml`, `ezcompiler.yaml`, or `ezcompiler.json`. The
generated script is standalone and committable: the five volatile build values
arrive at compile time through ISCC `/D` defines, so nothing release-specific is
baked in. Once `installer.iss_path` points at a script, generation options are
ignored and the file itself is the source of truth.

```bash
ezcompiler generate iss
ezcompiler generate iss --output installer/MyApp.iss --force
```

| Option     | Required | Default                        | Description                  |
| :--------- | :------- | :----------------------------- | :--------------------------- |
| `--output` | No       | `installer/<project_name>.iss` | Script path                  |
| `--force`  | No       | `False`                        | Overwrite an existing script |

!!! warning "Relative `icon` and `license_file`"

    ISCC resolves both against the `.iss` file's own directory, not the current
    working directory. Generation warns when either is relative.

---

### `generate build`

Generate a `build.py` script from a configuration file.

The script drives the full pipeline — version file, compilation, ZIP,
installer, release — and is meant to be committed and run directly. It
initializes `Ezpl` itself, since EzCompiler produces no output until the host
application does. The installer stage runs when `installer.enabled` is true in
the configuration; nothing in the script needs to change to turn it on.

```bash
ezcompiler generate build --config ezcompiler.yaml
ezcompiler generate build --from-pyproject pyproject.toml --output scripts
```

| Option     | Required | Default | Description                                  |
| :--------- | :------- | :------ | :------------------------------------------- |
| `--config` | No       | —       | Path to configuration file (YAML or JSON)    |
| `--output` | No       | `"."`   | Output **directory**; the file is `build.py` |

---

### `generate version`

Generate a Windows version information file.

```bash
ezcompiler generate version --config ezcompiler.yaml
```

| Option     | Required | Default         | Description                |
| :--------- | :------- | :-------------- | :------------------------- |
| `--config` | Yes      | —               | Path to configuration file |
| `--output` | No       | `"version.txt"` | Output file path           |

---

### `generate template`

Generate a template file with optional mockup data.

```bash
ezcompiler generate template --type config --mockup
```

| Option     | Required | Description                                    |
| :--------- | :------- | :--------------------------------------------- |
| `--type`   | Yes      | Template type: `config`, `setup`, or `version` |
| `--mockup` | No       | Include sample data                            |
| `--output` | No       | Output file path                               |

### `upload`

Upload the TUF tree and/or the release directory (ZIP + installer `setup.exe`) to their destination. Auto-detects the flow from `tuf_enabled`: TUF tree → `<dest>/update/`, release directory → `<dest>/release/`. Destination and backends fall back to the config when not provided.

```bash
ezcompiler upload --config ezcompiler.yaml
```

| Option                  | Required | Default | Description                                                                  |
| :---------------------- | :------- | :------ | :--------------------------------------------------------------------------- |
| `--config`              | No       | —       | Config file path (YAML, JSON)                                                |
| `--pyproject`           | No       | —       | Explicit `pyproject.toml` path                                               |
| `--repo-destination`    | No       | —       | Backend for the TUF tree: `disk`, `server`, `r2` (overrides config)          |
| `--release-destination` | No       | —       | Backend for the release directory: `disk`, `server`, `r2` (overrides config) |
| `--destination`         | No       | —       | Common override applied to both `repo` and `release` destinations            |

---

### `release init`

Initialize TUF signing keys and the repository skeleton. Run once per project, before the first `ezcompiler compile` with `tuf_enabled = true`. Safe to re-run: skips silently when keys already exist.

```bash
ezcompiler release init
```

| Option     | Required | Default | Description                                    |
| :--------- | :------- | :------ | :--------------------------------------------- |
| `--config` | No       | —       | Path to config file (auto-detected if omitted) |

---

### `updater generate`

Generate the client updater files (`update.py`, `settings.py`) and copy `root.json` from the local TUF repository into the output directory.

```bash
ezcompiler updater generate
```

| Option         | Required | Default | Description                                     |
| :------------- | :------- | :------ | :---------------------------------------------- |
| `--config`     | No       | —       | Path to configuration file                      |
| `--output-dir` | No       | —       | Output directory for generated files            |
| `--no-patch`   | No       | —       | Skip patching the config with `repo_public_url` |

---

## 🧪 Examples

```bash
# Show version
ezcompiler --version

# Initialize project interactively
ezcompiler init

# Generate a YAML configuration
ezcompiler generate config --project-name "MyApp" --main-file "main.py" --version "2.0.0"

# Generate build.py
ezcompiler generate build --config ezcompiler.yaml

# Generate version information file
ezcompiler generate version --config ezcompiler.yaml --output version_info.txt

# Generate config template with sample data
ezcompiler generate template --type config --mockup

# Compile the project
ezcompiler compile --compiler PyInstaller

# Initialize TUF signing keys (one-time)
ezcompiler release init

# Upload the TUF tree and release directory
ezcompiler upload --repo-destination server --release-destination server \
    --destination https://uploads.example.com/MyApp
```
