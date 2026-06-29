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
| `generate config`   | Generate a configuration file                                           |
| `generate setup`    | Generate a `setup.py` from a configuration file                         |
| `generate version`  | Generate a Windows version information file                             |
| `generate template` | Generate a template file with optional mockup data                      |
| `updater generate`  | Generate client updater files (`update.py`, `settings.py`, `root.json`) |

---

### `init`

Initialize a new EzCompiler project with interactive prompts.

```bash
ezcompiler init
```

Guides through: project name, main script, output directory, compiler selection, dependencies, and files to include.

---

### `generate config`

Create a configuration file.

```bash
ezcompiler generate config --project-name "MyApp" --main-file "main.py"
```

| Option           | Required | Default             | Description                      |
| :--------------- | :------- | :------------------ | :------------------------------- |
| `--project-name` | Yes      | —                   | Project name                     |
| `--main-file`    | Yes      | —                   | Main Python file                 |
| `--version`      | No       | `"1.0.0"`           | Project version                  |
| `--output`       | No       | `"ezcompiler.yaml"` | Output file path                 |
| `--format`       | No       | `yaml`              | Output format (`yaml` or `json`) |

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
```
