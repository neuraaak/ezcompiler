# Release pipeline

This page explains the design rationale and layout of EzCompiler's release pipeline. For step-by-step instructions, see the [Secure Updates with tufup](../guides/secure-updates-tufup.md) guide.

---

## Pipeline order

The build pipeline stages execute in a fixed order:

```text
compile → zip → installer → release
```

`installer` runs when `installer.enabled=True`, producing a Windows `setup.exe` via Inno Setup — see the [Windows Installer](../guides/windows-installer.md) guide. By default, its `.iss` script is ephemeral: it is written in a temporary directory and removed after a successful ISCC invocation, rather than left in `installer.output_dir`. A failed invocation retains it for diagnosis. Generate and adopt a script through `installer.iss_path` when a persistent, editable file is needed. `release` always runs after: the signed TUF tree is built locally from the output. `run_pipeline()` stops here — it never transfers anything. Publishing is a **separate, explicit step** (`ezcompiler publish update` / `ezcompiler publish release`), which keeps a partial or unsigned tree from ever being published.

---

## Local vs published

The pipeline produces and signs **locally**; the CLI **publishes**. Nothing irreversible happens until an operator runs a `publish` command, and both commands print a recap and ask for confirmation first (`--yes` skips it for automation).

The two publications are not equivalent, which is why they are two commands rather than one:

|                     | `publish update` (TUF tree)                                                                                                 | `publish release` (installer + ZIP)                  |
| :------------------ | :-------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------- |
| Reversibility       | **None** — metadata versions are monotonic and clients refuse a lower version (anti-rollback). You supersede, never revert. | Yes — a file in a folder or bucket, overwritable.    |
| Consumer            | Installed clients that **update on their own**, with no human action.                                                       | Manual download.                                     |
| Effect of a bad push | Existing installations migrate by themselves.                                                                              | Nothing until someone downloads it.                  |

The confirmation lives in the CLI only. A Python method must never read stdin, so the Python publication paths (`EzCompiler.upload()`, `release(publish=True)`) cannot offer that guard: they are deprecated and will be removed in v5.

---

## Publication layout

When `tuf_enabled=True`, the two publications target independent destinations:

```text
<repo_endpoint>/update/      # TUF tree: signed metadata/ + targets/
<release_endpoint>/release/  # distributable ZIP archive + setup.exe (if installer.enabled)
```

The TUF tree (`repo_destination`/`repo_endpoint`) and the release directory (`release_destination`/`release_endpoint`) are decoupled so each can target a different backend (`disk`, `server`, or `r2` for the TUF tree). The release can also go to a **GitHub Release** (`release_destination = "github"`, `release_endpoint = "owner/repo"`), created through the `gh` CLI; the TUF tree never can, because it must be served over HTTP on stable paths. For `r2`, the TUF tree is written straight to the bucket prefix and the release directory is skipped — including the installer.

---

## Client side

The tufup *client* — checking for updates, downloading, and applying them inside the end-user application — **is** covered by ezcompiler: use `generate_updater()` to scaffold the bootstrap files, then call `update.main()` at startup. See the [Secure Updates with tufup](../guides/secure-updates-tufup.md) guide. For advanced client behavior, refer to the [tufup documentation](https://dennisvang.github.io/tufup/).
