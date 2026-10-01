# Secure Updates with tufup

This guide explains how to integrate **tufup** (Trust Updates for Python) into your ezcompiler build pipeline to produce signed, TUF-compliant update repositories for your compiled applications.

> **Scope.** This guide covers the full loop: packaging a compiled bundle into a signed TUF tree, uploading it, **and** wiring the self-updating client into your app. For background on the pipeline design and publish layout, see [Release pipeline](../concepts/about-release-pipeline.md).

---

## Prerequisites

Install the optional extra:

```bash
pip install ezcompiler[tufup]
```

tufup requires Python ≥ 3.13 and depends on `python-tuf` and `cryptography`.

---

## Step 1 — Initialize signing keys (one-time admin operation)

> **Important.** Key initialization is a deliberate, offline step. Keys are **never** generated automatically during a build.

Use the `ezcompiler` CLI to initialize the key set and the repository skeleton:

```bash
ezcompiler tuf init
```

The paths (`tuf_repo_dir`, `tuf_keys_dir`) are read from the project config file (auto-detected in the current directory). You can also point to a specific config:

```bash
ezcompiler tuf init --config path/to/ezcompiler.config.yaml
```

This creates:

- `./keystore/` — signing keys (root, targets, snapshot, timestamp).
- `./repo/repository/` — the initial signed metadata.

**Security rules for keys:**

- Add `keystore/` to `.gitignore` — never commit private keys.
- Store offline keys (root, targets) on encrypted media; keep online keys (snapshot, timestamp) accessible only from the build machine.

---

## Step 2 — Configure `CompilerConfig`

```python
from pathlib import Path
from ezcompiler import EzCompiler, CompilerConfig

config = CompilerConfig(
    version="2.0.0",
    project_name="MyApp",
    main_file="src/main.py",
    include_files={"files": [], "folders": []},
    output_folder=Path("dist"),
    # Release options
    tuf_enabled=True,                 # turn on the TUF release + updater
    tuf_repo_dir=Path("repo"),        # local TUF repository root
    tuf_keys_dir=Path("keystore"),    # signing keys directory
    # Upload destinations (split: TUF tree vs. installer zip)
    repo_destination="server",        # disk | server | r2 — where the TUF tree lands
    repo_endpoint="https://uploads.example.com/MyApp",   # upload target for the TUF tree
    release_destination="server",     # disk | server — where the installer zip lands
    release_endpoint="https://uploads.example.com/MyApp",
    # Client updater — the URL the compiled app polls for updates
    repo_public_url="https://updates.example.com/MyApp",
)
```

> **Destinations.** The TUF tree and the installer ZIP are uploaded **separately**:
> `repo_destination`/`repo_endpoint` control the signed TUF tree, `release_destination`/`release_endpoint`
> control the distributable ZIP. An `*_endpoint` is required whenever its `*_destination` is not `"disk"`
> (for `disk` it is a local path). For `r2`, the endpoint is `"bucket/prefix"`.
>
> **`repo_public_url`** is the public URL the compiled client application polls for updates. It is required when `tuf_enabled=True` and `repo_destination` is not `"disk"`. This value is written into the generated `settings.py` so the end-user app knows where to fetch update metadata.

---

## Step 3 — Compile, then release

```python
compiler = EzCompiler(config)

# 1. Compile the project as usual.
compiler.compile_project()

# 2. Package the compiled output into a signed TUF repository.
#    bundle_dir is the compiled application directory (onedir output).
repository_path = compiler.release(bundle_dir=Path("dist/MyApp"))

print(f"Signed repository written to: {repository_path}")
```

`release()` calls `tufup.repo.Repository.add_bundle()` + `publish_changes()` and returns the path to the local `repository/` tree.

---

## Step 4 — Build via the pipeline, then publish

The build pipeline runs the stages `compile → zip → release`. When `tuf_enabled`
is set, `run_pipeline()` builds the signed TUF tree locally — it does **not**
transfer anything. Publication is a separate, explicit CLI step:

```python
compiler.run_pipeline(console=False)   # compile → zip → release (local only)
```

```bash
ezcompiler publish update    # TUF tree — recap + confirmation
ezcompiler publish release   # installer + ZIP (recap + confirmation on GitHub)
```

The two commands perform **two independent transfers**, mirrored by the client's update URL:

| Artifact      | Destination                                | Landing path                  |
| :------------ | :----------------------------------------- | :---------------------------- |
| TUF tree      | `repo_destination` / `repo_endpoint`       | `<repo_endpoint>/update/`     |
| Installer ZIP | `release_destination` / `release_endpoint` | `<release_endpoint>/release/` |

For `r2`, each tree is uploaded straight to its bucket prefix (no `/update/`
or `/release/` subdir). The `/update/` suffix is what the
generated client polls — keep `repo_public_url` pointing at the same root
(the client appends `/update` itself for `disk` and `server`).

`publish release` can also create a GitHub Release (`release_destination = "github"`);
see the [CLI reference](../cli/index.md#publish-release).

!!! warning "Deprecated"
    `compiler.upload()`, `ezcompiler upload` and
    `compiler.release(bundle_dir, publish=True)` are deprecated and will be removed
    in v5: use the `ezcompiler publish` commands. The calls still work but warn.

---

## Metadata expiration (irregularly-updated projects)

TUF metadata carries an expiration date **per role**. tufup's defaults are short
for the online roles — `root=365`, `targets=7`, `snapshot=7`, `timestamp=1` (days).
Once `timestamp`/`snapshot` expire, clients refuse to trust the repository **even
if no new version was published**. For a project you release irregularly, that
silently breaks updates between releases.

Two native tufup mechanisms address this:

**1. Longer lifetimes via config.** Set `tuf_expiration_days` to raise the per-role
lifetime (unset roles fall back to tufup defaults). It is applied on `tuf init`
and every release:

```python
config = CompilerConfig(
    ...,
    tuf_enabled=True,
    tuf_expiration_days={"timestamp": 30, "snapshot": 30, "targets": 90},
)
```

**2. Keep-alive re-sign.** Re-sign the metadata to push the expiration forward
without cutting a new release — run this periodically (e.g. a scheduled job):

```bash
ezcompiler tuf refresh                          # targets/snapshot/timestamp
ezcompiler tuf refresh --role timestamp --days 60
```

```python
compiler.refresh_release_expiration(days=60)
```

Both require the signing keys (`tuf init`). After a refresh, re-run
`ezcompiler publish update` so the freshly-signed metadata reaches the clients.

---

## Withdraw a broken version

When the latest published version turns out to be broken, withdraw it from the signed tree, then ship a mandatory fix:

```bash
ezcompiler tuf remove-latest           # withdraw 1.2.3 from the local tree, re-sign
ezcompiler publish update              # republish the tree without 1.2.3
ezcompiler compile --required          # build 1.2.4, mandatory
ezcompiler publish update              # clients on 1.2.3 move to 1.2.4
```

`ezcompiler tuf status` shows the versions, their flags, the role expirations and the withdrawn versions before and after.

Clients never downgrade: withdrawing stops the version from reaching clients that do not have it yet; clients that installed it leave it only through a higher version, which `--required` makes mandatory.

Only the latest version can be withdrawn. The archive and patch stay on the remote storage, unusable because no signed metadata references them.

`withdrawn.json` at the repository root records withdrawn versions; ezcompiler refuses to release a version that is not above them. It is published with the tree and ignored by clients. The rule also applies from the Python API (`EzCompiler.release(..., required=True)`, `run_pipeline(..., required=True)`).

---

## Step 5: Generate client updater files

Once the TUF repository is initialized and the config contains a valid `repo_public_url`, generate the client-side bootstrap files:

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
    tuf_repo_dir=Path("repo"),
    tuf_keys_dir=Path("keystore"),
    repo_public_url="https://updates.example.com/MyApp",
)

compiler = EzCompiler(config)
generated = compiler.generate_updater(output_dir=Path("src/updater"))
# Returns a list of generated paths: [update.py, settings.py, root.json]
for path in generated:
    print(f"Generated: {path}")
```

This produces three files in `output_dir` (defaults to the project root):

| File          | Description                                                    |
| :------------ | :------------------------------------------------------------- |
| `update.py`   | Client update logic — checks for and applies updates via tufup |
| `settings.py` | Update settings, including `repo_public_url`                   |
| `root.json`   | Copy of the TUF root metadata, bundled with the app            |

By default (`patch_config=True`), `generate_updater()` adds the three generated files to `include_files` so they are bundled into the compiled app. Because it mutates the config, **call it before `run_pipeline()`**:

```python
if config.tuf_enabled:
    compiler.generate_updater()   # must precede run_pipeline()
compiler.run_pipeline()
```

Via CLI:

```bash
ezcompiler updater generate --output-dir src/updater
```

---

## Step 6 — Wire the updater into your app

Call `update.main()` at the very top of your app's entry point. It checks the
repository once, and if a newer version is available it downloads and applies it,
then exits so tufup can swap the files and relaunch. It never blocks startup: a
failed check is reported and ignored.

```python
# main.py
try:
    import update  # generated by generate_updater(), bundled at compile time

    update.main()
except ImportError:
    pass  # updater files absent in dev — app still runs
```

The generated client is bundler-agnostic (PyInstaller, cx_Freeze, Nuitka) and
resolves its own install directory from the running executable. The TUF
metadata/target cache, however, is kept separate from that install directory —
under `%LOCALAPPDATA%\<app>\tuf` on Windows (`XDG_CACHE_HOME` or `~/.cache`
otherwise) — since the install directory may not be writable without
elevation (see [per-user installs](windows-installer.md) if you also ship a
Windows installer).

On Windows, applying an update relaunches the app automatically once the
files are swapped, matching the existing macOS behavior.

!!! tip "Calling the updater from a GUI thread"
    `update.main()` and `check_and_apply()` assume the main thread: tufup's
    installer ends the process with `sys.exit(0)` once the swap script is
    launched, which only terminates the calling thread if called from
    elsewhere (e.g. a pywebview worker thread). Call `update.apply_and_quit()`
    instead from a non-main thread — it wraps `check_and_apply()` and forces
    the whole process to exit via `os._exit(0)`.

!!! tip "Disk-served repositories work client-side"
    When `repo_destination="disk"`, the client reads updates over a `file://` URL
    via a built-in file fetcher — useful for offline, LAN, or test installs, with
    no HTTP server required. HTTP(S) via `repo_public_url` remains the norm for
    production.

!!! warning "Rebuild after changing the destination"
    `UPDATE_URL` is baked into the compiled `settings.py`. Changing
    `repo_destination`/`repo_public_url` requires regenerating the client and
    recompiling — an already-shipped executable keeps its original URL.

---

## Error handling

| Exception                | Raised when                                  |
| ------------------------ | -------------------------------------------- |
| `ReleaseError`           | General release failure (wraps tufup errors) |
| `SigningKeyError`        | `keys_dir` is missing or inaccessible        |
| `BundleBuildError`       | `bundle_dir` is missing or empty             |
| `ReleaserTypeError`      | Unknown releaser backend requested           |
| `UpdaterError`           | General updater generation failure           |
| `UpdaterConfigError`     | `repo_public_url` missing or config invalid  |
| `UpdaterGenerationError` | File generation or copy failure              |

```python
from ezcompiler import ReleaseError
from ezcompiler.shared.exceptions import SigningKeyError

try:
    compiler.release(bundle_dir=Path("dist/MyApp"))
except SigningKeyError:
    print("Initialize keys first — see Step 1.")
except ReleaseError as e:
    print(f"Release failed: {e}")
```

---

## Going further

The generated client covers the common check-download-apply loop. For advanced
scenarios — custom pre-release channels, patch (delta) updates, or bespoke
confirmation UI — see the [tufup documentation](https://dennisvang.github.io/tufup/)
and adapt the generated `update.py` to your needs.
