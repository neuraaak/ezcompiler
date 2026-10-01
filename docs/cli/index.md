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
| `publish update`    | Publish the signed TUF update tree (asks for confirmation)              |
| `publish release`   | Publish the installer and ZIP (GitHub: recap + confirmation)            |
| `tuf init`          | Initialize TUF signing keys and repository skeleton                     |
| `tuf refresh`       | Re-sign TUF metadata to extend expiration without a new release         |
| `tuf status`        | Show the local TUF tree: versions, flags, expirations, withdrawn versions |
| `tuf remove-latest` | Withdraw the latest version from the local tree                         |
| `upload`            | **Deprecated** — use `publish update` then `publish release`            |
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
| `--required`                 | No       | `False` | Mark this version as mandatory for TUF clients. Requires the TUF release stage (`tuf_enabled`, no `--skip-release`). |

!!! note "Pipeline stages"
    `compile` runs `version → compile → zip`, plus the installer and TUF release stages when enabled in the config (same behaviour as the Python API's `run_pipeline()`). Publication is a separate step: run `ezcompiler publish update` and `ezcompiler publish release` afterwards.

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

### `publish update`

Publish the signed TUF update tree to `<repo_endpoint>/update/`. Before transferring anything, the command prints a recap — backend, destination, the version that becomes current, file count — and asks for confirmation. The version is read from the signed tree (`metadata/targets.json`), not from the config; when the two differ, the recap warns.

This is the less reversible of the two publications: TUF metadata versions are monotonic and installed clients update on their own. A published tree cannot be rolled back, only superseded by a higher version. After `ezcompiler tuf remove-latest`, the recap explains that the config version was withdrawn and that clients already running it stay on it until a higher version; the command can then publish a tree emptied of versions.

```bash
ezcompiler publish update
ezcompiler publish update --repo-destination r2 --yes
```

| Option               | Required | Default | Description                                                         |
| :------------------- | :------- | :------ | :------------------------------------------------------------------ |
| `--config`           | No       | —       | Config file path (YAML, JSON)                                       |
| `--pyproject`        | No       | —       | Explicit `pyproject.toml` path                                      |
| `--repo-destination` | No       | —       | Backend for the TUF tree: `disk`, `server`, `r2` (overrides config) |
| `--destination`      | No       | —       | Destination override                                                |
| `--yes`, `-y`        | No       | off     | Skip the confirmation prompt                                        |

The command fails before the recap when no signed tree exists in the TUF repository directory: run the build pipeline first.

---

### `publish release`

Publish the installer `setup.exe` (when `installer.enabled`) and the ZIP. The path depends on `release_destination`:

- **`github`** — creates a GitHub Release through the [`gh` CLI](https://cli.github.com/), with the artifacts attached; the ZIP is attached under its versioned name, `<Project>-<version>.zip`. `release_endpoint` is the `owner/repo`; when empty, `gh` infers the repository from the current git remote, and the recap says so. `--destination` is rejected on this path. When `installer.enabled` is true, a missing `setup.exe` stops the command instead of publishing an incomplete release. Requires `gh` on the `PATH` and an authenticated session (`gh auth login`, or `GH_TOKEN` in the environment). No credential goes through the configuration or the command line. Every check (`gh` installed and authenticated, existing tag, artifacts, notes file) runs before the recap; the release is never overwritten — an existing tag stops the command.
- **`disk`, `server`, `r2`** — copies the release directory to `<release_endpoint>/release/`, as `ezcompiler upload` did (the ZIP keeps its unversioned name, and whatever artifacts exist are copied), without a recap or confirmation prompt. `--tag`, `--title`, `--notes`, `--notes-file`, `--draft` and `--prerelease` do not apply there; the command warns when they are given. It fails when no artifact was built.

`gitlab` is not supported yet: selecting it fails with an explicit error.

**Server credentials.** The `server` backend (for `publish update` and `publish release`) reads its credentials from the environment, never from the command line: `EZCOMPILER_SERVER_USERNAME` and `EZCOMPILER_SERVER_PASSWORD` (basic auth), or `EZCOMPILER_SERVER_API_KEY` (bearer token). A value set explicitly in the uploader configuration takes precedence.

```bash
ezcompiler publish release
ezcompiler publish release --yes --notes-file CHANGELOG.md
```

| Option                              | Required | Default                      | Description                                                       |
| :---------------------------------- | :------- | :--------------------------- | :---------------------------------------------------------------- |
| `--config`                          | No       | —                            | Config file path (YAML, JSON)                                     |
| `--pyproject`                       | No       | —                            | Explicit `pyproject.toml` path                                    |
| `--release-destination`             | No       | —                            | `disk`, `server`, `r2`, `github`, `gitlab` (overrides config)     |
| `--destination`                     | No       | —                            | Destination override (file backends)                              |
| `--tag`                             | No       | `v<version>`                 | Release tag                                                       |
| `--title`                           | No       | `<project> v<version>`       | Release title                                                     |
| `--notes`                           | No       | generated                    | Literal release body (exclusive with `--notes-file`)              |
| `--notes-file`                      | No       | —                            | File holding the release body (exclusive with `--notes`)          |
| `--prerelease` / `--no-prerelease`  | No       | derived from the version     | Force the pre-release flag (`1.2.0rc1` is a pre-release)          |
| `--draft`                           | No       | off                          | Create the release unpublished                                    |
| `--yes`, `-y`                       | No       | off                          | Skip the confirmation prompt                                      |

---

### `upload`

!!! warning "Deprecated"
    `ezcompiler upload` is deprecated and will be removed in v5. Use `ezcompiler publish update` then `ezcompiler publish release`, which ask for confirmation before any irreversible publication (the TUF tree, and GitHub releases). `EzCompiler.upload()` is deprecated likewise.

A non-interactive shortcut: it runs `publish update --yes` when `tuf_enabled` is true, then `publish release --yes`, passing its options through. If the TUF tree fails to publish, the release is not attempted. It refuses a platform release destination (`github`, `gitlab`) and points to `publish release`, so a GitHub release is never created without a confirmation prompt.

Two behaviours changed from the old implementation:

- an `r2` TUF tree no longer skips a `disk` release: both are published;
- with `tuf_enabled` false, the build goes through `publish release`: the release directory (ZIP + installer) lands in `<release_endpoint>/release/` with the release backend, instead of the bare ZIP in `repo_endpoint` with the repo backend. It fails when nothing was built, instead of publishing an empty directory.

```bash
ezcompiler upload --config ezcompiler.yaml
```

| Option                  | Required | Default | Description                                                                  |
| :---------------------- | :------- | :------ | :--------------------------------------------------------------------------- |
| `--config`              | No       | —       | Config file path (YAML, JSON)                                                |
| `--pyproject`           | No       | —       | Explicit `pyproject.toml` path                                               |
| `--repo-destination`    | No       | —       | Backend for the TUF tree: `disk`, `server`, `r2` (overrides config)          |
| `--release-destination` | No       | —       | Backend for the release directory: `disk`, `server`, `r2` (overrides config) |
| `--destination`         | No       | —       | Passed to both `publish update` and `publish release`                        |

---

### `tuf init`

Initialize TUF signing keys and the repository skeleton. Run once per project, before the first `ezcompiler compile` with `tuf_enabled = true`. Safe to re-run: skips silently when keys already exist.

Formerly `ezcompiler release init`, which still works as a hidden, deprecated alias until v5.

```bash
ezcompiler tuf init
```

| Option     | Required | Default | Description                                    |
| :--------- | :------- | :------ | :--------------------------------------------- |
| `--config` | No       | —       | Path to config file (auto-detected if omitted) |

---

### `tuf refresh`

Re-sign the short-lived TUF roles to extend their expiration without publishing a new version. Formerly `ezcompiler release refresh` (deprecated alias until v5).

```bash
ezcompiler tuf refresh --role timestamp --days 60
```

| Option     | Required | Default                           | Description                                    |
| :--------- | :------- | :-------------------------------- | :--------------------------------------------- |
| `--config` | No       | —                                 | Path to config file (auto-detected if omitted) |
| `--role`   | No       | `targets`, `snapshot`, `timestamp` | TUF role to refresh (repeatable)               |
| `--days`   | No       | config `tuf_expiration_days`      | Expiration in days from now                    |

---

### `tuf status`

Show the local TUF tree (`tuf_repo_dir`) without touching tufup or the signing keys: signed versions from the most recent to the oldest (with the `obligatoire` and `patch` flags), the expiration of each role, and the versions withdrawn by `tuf remove-latest`. A role expiring in less than 7 days is flagged with a warning that names the command to run (`ezcompiler tuf refresh`, or `ezcompiler tuf refresh --role root` for root); an expired role is reported as an error. Read-only.

Exits with code 1 when the tree is not initialized (`metadata/root.json` missing) or unreadable.

```bash
ezcompiler tuf status
```

| Option        | Required | Default | Description                    |
| :------------ | :------- | :------ | :----------------------------- |
| `--config`    | No       | —       | Config file path (YAML, JSON)  |
| `--pyproject` | No       | —       | Explicit `pyproject.toml` path |

---

### `tuf remove-latest`

Withdraw the latest version from the local TUF tree and re-sign it. Before changing anything, the command prints a recap — the version withdrawn, the local files removed (archive and patch), the version that becomes the latest — and asks for confirmation. Removing the only version is allowed, with a warning: the republished tree then offers no version at all.

Only the latest version can be withdrawn. The version is recorded in `withdrawn.json` at the root of the TUF repository directory, and a new release must be higher than every withdrawn version. The command then points to the next steps: `ezcompiler compile --required` with a higher version, then `ezcompiler publish update`. It needs the signing keys; it fails when there is nothing to withdraw.

```bash
ezcompiler tuf remove-latest
ezcompiler tuf remove-latest --yes
```

| Option        | Required | Default | Description                    |
| :------------ | :------- | :------ | :----------------------------- |
| `--config`    | No       | —       | Config file path (YAML, JSON)  |
| `--pyproject` | No       | —       | Explicit `pyproject.toml` path |
| `--yes`, `-y` | No       | off     | Skip the confirmation prompt   |

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
ezcompiler tuf init

# Publish the TUF update tree, then the release
ezcompiler publish update
ezcompiler publish release --notes-file CHANGELOG.md
```
