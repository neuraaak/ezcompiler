# Release pipeline

This page explains the design rationale and layout of EzCompiler's release pipeline. For step-by-step instructions, see the [Secure Updates with tufup](../guides/secure-updates-tufup.md) guide.

---

## Pipeline order

The build pipeline stages execute in a fixed order:

```text
compile → zip → release
```

`release` always runs after the compiled bundle is zipped: the signed TUF tree is built locally from the output. `run_pipeline()` stops here — it never transfers anything. Uploading is a **separate, explicit step** (`compiler.upload()` / `ezcompiler upload`), which keeps a partial or unsigned tree from ever being published.

---

## Upload layout

When `tuf_enabled=True`, `upload()` transfers two artifacts to independent destinations:

```text
<repo_endpoint>/update/    # TUF tree: signed metadata/ + targets/
<release_endpoint>/release/  # distributable ZIP archive
```

The TUF tree (`repo_destination`/`repo_endpoint`) and the installer ZIP (`release_destination`/`release_endpoint`) are decoupled so each can target a different backend (`disk`, `server`, or `r2` for the TUF tree). For `r2`, the TUF tree is written straight to the bucket prefix and the ZIP is skipped.

---

## Client side

The tufup *client* — checking for updates, downloading, and applying them inside the end-user application — **is** covered by ezcompiler: use `generate_updater()` to scaffold the bootstrap files, then call `update.main()` at startup. See the [Secure Updates with tufup](../guides/secure-updates-tufup.md) guide. For advanced client behavior, refer to the [tufup documentation](https://dennisvang.github.io/tufup/).
