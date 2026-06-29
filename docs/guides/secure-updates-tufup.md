# Secure Updates with tufup

This guide explains how to integrate **tufup** (Trust Updates for Python) into your ezcompiler build pipeline to produce signed, TUF-compliant update repositories for your compiled applications.

> **Scope.** This guide covers the *publish side* only: packaging a compiled bundle into a signed `repository/` tree and optionally transferring it to a server. For background on the pipeline design and publish layout, see [Release pipeline](../concepts/about-release-pipeline.md). The *client side* — update checking and applying inside the end-user app — is outside the scope of this guide.

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
ezcompiler release init
```

The paths (`tufup_repo_dir`, `tufup_keys_dir`) are read from the project config file (auto-detected in the current directory). You can also point to a specific config:

```bash
ezcompiler release init --config path/to/ezcompiler.config.yaml
```

Alternatively, call it from your setup script (one-time, before the first build):

```bash
python setup.py --init
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
    release_needed=True,
    release_type="tufup",             # only supported backend
    tufup_repo_dir=Path("repo"),      # local TUF repository root
    tufup_keys_dir=Path("keystore"),  # signing keys directory
    update_repo_url="https://updates.example.com/MyApp",  # remote (optional)
    # Client updater — required when tuf_enabled=True and repo_destination != "disk"
    repo_public_url="https://updates.example.com/MyApp",
)
```

> **`repo_public_url`** is the public URL the compiled client application will poll for updates. It is required when `tuf_enabled=True` and `repo_destination` is not `"disk"`. This value is written into the generated `settings.py` so the end-user app knows where to fetch update metadata.

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

## Step 4 — Publish via the pipeline (recommended)

The build pipeline runs the stages in order `compile → zip → release → upload`.
When `release_needed` is set, `run_pipeline()` builds the signed TUF tree, then the
**upload stage** transfers a single publish root to `update_repo_url`:

```text
publish/
├── downloads/<App>.zip   # le zip distribuable
└── repository/           # l'arbre TUF (metadata + targets)
```

```python
compiler.run_pipeline(console=False)
```

`update_repo_url` is the **unified upload destination** under which both
`downloads/` (zip) and `repository/` (TUF tree) land. When empty, the destination
falls back to `upload.repo_path` (disk) or `upload.server_url` (server). The
transfer backend is `config.upload_structure` (`"disk"` or `"server"`); the server
uploader walks the tree recursively and POSTs each file at its relative path.

!!! warning "Déprécié"
    `compiler.release(bundle_dir, publish=True)` est déprécié : le transfert distant
    est désormais assuré par le stage upload de `run_pipeline`. L'appel émet un
    `DeprecationWarning` mais continue de fonctionner.

You can also call `ReleaseService` directly for more control:

```python
from ezcompiler.services.release_service import ReleaseService

ReleaseService.release_and_publish(
    bundle_dir=Path("dist/MyApp"),
    app_name="MyApp",
    version="2.0.0",
    repo_dir=Path("repo"),
    publish=True,
    upload_type="server",
    destination="https://updates.example.com/MyApp",
    releaser_config={"keys_dir": Path("keystore")},
)
```

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
    tufup_repo_dir=Path("repo"),
    tufup_keys_dir=Path("keystore"),
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

By default (`patch_config=True`), `generate_updater()` also writes `repo_public_url` back to the project config file if it was not already present.

Via CLI:

```bash
ezcompiler updater generate --output-dir src/updater
```

---

## Error handling

| Exception                | Raised when                                  |
| ------------------------ | -------------------------------------------- |
| `ReleaseError`           | General release failure (wraps tufup errors) |
| `SigningKeyError`        | `keys_dir` is missing or inaccessible        |
| `BundleBuildError`       | `bundle_dir` is missing or empty             |
| `ReleaserTypeError`      | Unknown `release_type` value                 |
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

## Out of scope

The tufup *client* (checking for updates, downloading, and applying patches inside the end-user app) must be wired into the compiled application itself. Use [`generate_updater()`](#step-5-generate-client-updater-files) to scaffold the bootstrap files, then refer to the [tufup documentation](https://dennisvang.github.io/tufup/) for the full client-side integration.
