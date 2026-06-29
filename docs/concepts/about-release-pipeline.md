# Release pipeline

This page explains the design rationale and layout of EzCompiler's release pipeline. For step-by-step instructions, see the [Secure Updates with tufup](../guides/secure-updates-tufup.md) guide.

---

## Pipeline order

The pipeline stages execute in a fixed order:

```text
compile → zip → release → upload
```

`release` always runs before `upload`. The signed TUF repository must exist locally before any transfer to a remote destination can occur. This ordering prevents a partial or unsigned tree from being published.

---

## Publish layout

When `release_needed=True`, the pipeline assembles a flat publish structure under `dist/release/` before uploading:

```text
dist/release/
├── <App>-<version>.zip     # distributable archive
├── metadata/               # TUF signed metadata files
└── targets/                # TUF target files (bundles)
```

Both the distributable ZIP and the TUF tree land under the same root, so a single upload operation to `update_repo_url` transfers the complete release.

---

## Out of scope

The tufup *client* — checking for updates, downloading patches, and applying them inside the end-user application — is not part of ezcompiler's responsibility. Refer to the [tufup documentation](https://dennisvang.github.io/tufup/) for client-side integration, or use `generate_updater()` to scaffold the client bootstrap files.
