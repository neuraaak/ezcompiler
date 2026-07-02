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
| `generate setup`    | Generate a `setup.py` from a configuration file                         |
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

| Option                       | Required | Default | Description                                                                      |
| :--------------------------- | :------- | :------ | :------------------------------------------------------------------------------- |
| `--config`                   | No       | —       | Config file path (YAML, JSON)                                                    |
| `--pyproject`                | No       | —       | Explicit `pyproject.toml` path                                                   |
| `--compiler`                 | No       | —       | Compiler to use: `Cx_Freeze`, `PyInstaller`, `Nuitka` (overrides config)         |
| `--console` / `--no-console` | No       | —       | Show console window (overrides config)                                           |
| `--output-folder`            | No       | —       | Output folder (overrides config)                                                 |
| `--debug`                    | No       | `False` | Enable debug mode                                                                |
| `--no-zip`                   | No       | `False` | Skip ZIP archive creation                                                        |

!!! note "Version and zip only"
    `compile` runs the `version → compile → zip` stages only. The installer and TUF release stages are not part of this command — use the Python API's `run_pipeline()` for the full pipeline, then `ezcompiler upload` to publish.

---

### `generate config`

Create a configuration file.

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py"
```

| Option                | Required | Default             | Description                                 |
| :-------------------- | :------- | :------------------ | :------------------------------------------ |
| `--project-name`      | Yes      | —                   | Project name                                |
| `--main-file`         | Yes      | —                   | Main Python file                            |
| `--version`           | No       | `"1.0.0"`           | Project version                             |
| `--output`            | No       | `"ezcompiler.yaml"` | Output file path                            |
| `--format`            | No       | `yaml`              | Output format (`yaml` or `json`)            |
| `--installer-enabled` | No       | `False`             | Enable the Inno Setup installer build stage |

---

### `generate setup`

Generate a `setup.py` from a configuration file.

```bash
ezcompiler generate setup --config ezcompiler.yaml
```

| Option     | Required | Default      | Description                |
| :--------- | :------- | :----------- | :------------------------- |
| `--config` | Yes      | —            | Path to configuration file |
| `--output` | No       | `"setup.py"` | Output file path           |

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

| Option                  | Required | Default | Description                                                            |
| :---------------------- | :------- | :------ | :--------------------------------------------------------------------- |
| `--config`              | No       | —       | Config file path (YAML, JSON)                                          |
| `--pyproject`           | No       | —       | Explicit `pyproject.toml` path                                         |
| `--repo-destination`    | No       | —       | Backend for the TUF tree: `disk`, `server`, `r2` (overrides config)    |
| `--release-destination` | No       | —       | Backend for the release directory: `disk`, `server` (overrides config) |
| `--destination`         | No       | —       | Common override applied to both `repo` and `release` destinations      |

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

# Generate setup.py
ezcompiler generate setup --config ezcompiler.yaml

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
