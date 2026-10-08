# AGENTS.md

Instructions for AI coding agents working on **ezcompiler**. This file is
self-contained — there is no external instruction tree to consult.

## Project

`ezcompiler` is a Python framework that compiles Python projects into Windows
executables, then versions, packages (ZIP), builds a Windows installer, signs a
TUF release and distributes them. It exposes a unified interface over three
compilers (Cx_Freeze, PyInstaller, Nuitka), an Inno Setup installer builder, a
tufup releaser, and generates a client-side updater script.

- **Package:** `ezcompiler` (PyPI), entry point `EzCompiler` facade + `ezcompiler` CLI
- **Python:** >= 3.13 (do **not** target 3.12 or below; uses PEP 695 `type` aliases)
- **Build backend:** hatchling — sources under `src/ezcompiler`
- **Package manager:** uv (`uv.lock` is committed; keep it in sync)
- **Repo:** <https://github.com/neuraaak/ezcompiler>
- **Docs:** <https://neuraaak.github.io/ezcompiler/>

## Environment constraints

- **Target OS is Windows.** Test and reason about behavior on Windows first.
- **Corporate network:** proxy required for external access, limited PyPI reach.
  Don't assume free Internet; prefer offline-friendly approaches and wheels.
  If a task requires a new dependency that may not be available offline, flag
  it explicitly to the user rather than silently adding it to
  `pyproject.toml`. Suggest a wheel-based or vendored alternative where
  possible.

## Architecture — Hexagonal (Ports & Adapters)

```text
interfaces/   ← entry points: CLI (click) + Python API (EzCompiler facade)
services/     ← business orchestration (CompilerService, PipelineService,
                ConfigService, TemplateService, UploaderService, ReleaseService,
                InstallerService, UpdaterService, PublishService, TufService)
adapters/     ← concrete compilers, uploaders, releaser & installer behind
                ports, + factories
shared/       ← domain models (CompilerConfig, InstallerConfig,
                CompilationResult) + exceptions/
utils/        ← technical helpers + validators/
assets/       ← templates and static resources (no upward deps)
_types.py     ← type aliases + the five @runtime_checkable Protocol ports
```

### Ports (`_types.py`)

Five structural contracts that decouple services from concrete adapters:

| Port            | Key methods                                                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CompilerPort`  | `compile()`, `get_compiler_name()`, `zip_needed`, `config`                                                                                                     |
| `UploaderPort`  | `upload(source_path, destination)`, `get_uploader_name()`                                                                                                      |
| `ReleaserPort`  | `release(bundle_dir, app_name, version, repo_dir, *, patch, required)`, `init_keys(...)`, `remove_latest(app_name, repo_dir, keys_dir)`, `get_releaser_name()` |
| `InstallerPort` | `build(bundle_dir, app_name, version, output_dir, *, company_name, icon, main_file)`, `get_installer_name()`                                                   |
| `PublisherPort` | `exists(tag)`, `publish(assets, *, tag, title, notes, prerelease, draft)`, `get_publisher_name()`                                                              |

`TufService` reads the local TUF tree without tufup (`status()` returns a
`TufStatus` of `TufVersion` entries and role expirations, from `metadata/*.json`),
owns `<tuf_repo_dir>/withdrawn.json` (`withdrawn_versions`, `record_withdrawn`,
`remove_latest` via `ReleaserPort.remove_latest`) and holds the shared tree
helpers `read_tree_version` / `same_version`. `ReleaseService` calls
`TufService.ensure_releasable()` before any release: a version not strictly
above every withdrawn version raises `ReleaseError`, from the CLI and the Python
API alike. The `ezcompiler tuf` group (`init`, `refresh`, `status`,
`remove-latest`) only prints and confirms; `release init` / `release refresh`
remain as hidden deprecated aliases.

Concrete implementations live in `adapters/` with a `_` prefix (`_cx_freeze_compiler.py`, `_disk_uploader.py`, `_tufup_releaser.py`, `_innosetup_installer.py`). Always go through the factories — never instantiate adapters directly.

### Pipeline flow

`run_pipeline()` (the primary production path) executes stages in order, each
one conditional (`PipelineService.build_stages()`):

```text
version → compile → zip → installer → release
```

**Publication is not a pipeline stage.** `run_pipeline()` stops after building
the local TUF tree; publication is a separate, deliberate CLI step:
`ezcompiler publish update` (TUF tree) and `ezcompiler publish release`
(installer + zip). `publish update` and a `github` release show a recap and
ask for confirmation (`--yes` skips it); a release to `disk|server|r2` is
copied without a prompt, as before. This is pinned by `test_run_pipeline_does_not_upload`, and
the deprecation message of `release(publish=True)` names that sequence.
`EzCompiler.upload()` and `ezcompiler upload` still work but are **deprecated**
(removal in v5). `ezcompiler upload` delegates to `publish update` (when
`tuf_enabled`) then `publish release`, both with an implicit `--yes`, and refuses
a platform release destination (`test_cli_upload.py`). The publisher/uploader
routing (`github` → `PublisherPort`, `disk|server|r2` → `UploaderPort`) lives in
`PublishService` only: `interfaces/` never holds a `PublisherPort`. The CLI calls
`PublishService.preflight_release()`, which runs every local check (CLI present
and authenticated, tag free, artifacts staged) and returns a `ReleasePreflight`
value object to display; `publish_release()` then resolves the publisher itself
and takes no `publisher` argument. The same capability is exposed on the Python
API: `EzCompiler.publish_update()`, `preflight_release()` and
`publish_release()` (the confirmation prompt stays CLI-only). Both publication
branches resolve their artifacts through
`PipelineService.resolve_publishable_assets()`, so an enabled-but-missing
installer, or nothing built at all, fails for **every** destination instead of
being published silently on `disk|server|r2`.

`PipelineService.assemble_release_dir()` builds a flat `dist/release/` directory holding **only the zip and, when enabled, the installer `.exe`** — never TUF metadata (see `test_assemble_release_dir_contains_only_zip`). `PipelineService.stage_versioned_assets()` resolves those same artifacts and copies the zip under its versioned name, which is what the publication path consumes. The working TUF repo (`tuf_repository/`) stays structured for incremental patches and is published separately by `ezcompiler publish update`.

Config loading: `ConfigService.build_compiler_config()` only assembles the
layers and delegates to **`CompilerConfig.from_dict()`**
(`shared/_compiler_config.py`) — that is where the flattening lives, so that is
the file to edit. It flattens `compilation`, `upload`, `release` and `advanced`
into kwargs, pops the per-compiler sections (`[tool.ezcompiler.pyinstaller]`
etc., only the selected one is applied), and turns the `installer` block into an
`InstallerConfig` sub-object rather than flattening it. A new config block
**must** be handled there or `CompilerConfig.__init__()` raises an
unexpected-keyword error. The flattening is **strict**: `SECTION_SCHEMA` declares
the keys each section accepts, and `_flatten_sections()` refuses a key placed in
the wrong section (naming the right one) or declared both at the root and in a
section — the merge order no longer decides which value wins. A new key must be
added to `SECTION_SCHEMA` as well as to the dataclass. Removed keys are listed
once in `REMOVED_KEYS`, and `tuf_keys_dir` is refused when it resolves inside
`<tuf_repo_dir>/metadata` or `/targets`, which are published.

**Import contracts are enforced in CI by import-linter** (`[tool.importlinter]`
in `pyproject.toml`). The layer flow is strictly:

`interfaces → services → adapters → utils → shared`

`_types` and `assets` must never import from upper layers. Before adding an
import across layers, confirm it respects these contracts:

```bash
PYTHONPATH=src lint-imports
```

(import-linter 2.x needs the package importable; install editable or set
`PYTHONPATH=src`.)

If a needed import would violate layer contracts, do not introduce it.
Instead, propose a refactor that keeps the dependency within contract (e.g.
move logic to the correct layer) and explain the constraint to the user
before proceeding.

## Code conventions

- **Symbol visibility (enforced since v2.3.4):**
    - Internal concrete modules are `_`-prefixed: `_cx_freeze_compiler.py`,
      `_disk_uploader.py`, etc.
    - Internal instance attributes / methods are `_`-prefixed (`_config`,
      `_validate_config`); expose reads via `@property`.
    - Concrete adapters are kept out of `adapters/__init__.py` `__all__` —
      callers go through the **factories** (`CompilerFactory`,
      `uploader_factory`), never instantiate concretes directly.
- **Public API** is whatever is re-exported in `src/ezcompiler/__init__.py`
  `__all__`. Keep that surface deliberate and minimal.
- **Section separators** in source files use the project banner style:
  `# ///////////////////////////////////////////////////////////////`
- **Naming:** `*Service` (orchestration), `*Port` (structural contracts in
  `_types.py`), `Base*` (shared-implementation ABCs in `adapters/` — **not** the
  ports, see Working notes), `*Config`, `*Error`, `_*_utils.py`,
  `_*_service.py`.
- **Docstrings:** Google style.
- **Logging:** uses `ezplog` in **lib_mode** — the library stays passive until
  the host application initializes logging. Never use `print()` in library
  code. Level rules by layer: `interfaces/` — all levels; `services/` — INFO,
  WARNING, ERROR; `utils/` — DEBUG, ERROR only.
- **Prefer** `pathlib` over `os.path`, f-strings, full type hints. No hard-coded
  credentials or absolute paths; no committed commented-out code.

## Toolchain

| Task          | Command                                                          |
| ------------- | ---------------------------------------------------------------- |
| Install (dev) | `uv sync --all-extras --group dev --group docs` (PEP 735 groups) |
| Lint          | `ruff check .`                                                   |
| Format        | `ruff format .` (check: `ruff format --check .`)                 |
| Type check    | `ty check src/ezcompiler/` (the gate; pyright serves the IDE)    |
| Import rules  | `PYTHONPATH=src lint-imports`                                    |
| Security      | `bandit -r src/ezcompiler -ll` + `pip-audit` (both CI gates)     |
| Tests         | `pytest` (CI adds `--cov=src/ezcompiler --cov-fail-under=70`)    |

- **ruff** rules: `E W F I B C4 UP S T20 ARG PIE SIM`, line length 88,
  double quotes. See `[tool.ruff]` for per-file ignores.
- **Coverage:** branch coverage, audit target 80% — measured at 82.85% over 999
  tests as of 2026-10-08. The `--cov-fail-under=70` gate lives in the CI command,
  **not** in `addopts`: a partial local run (one file, a `-k` filter, a marker)
  must not exit 1. See the exclusions note below before assuming a module is
  omitted.
- **Dev tooling is in `[dependency-groups]`** (PEP 735), not in
  `[project.optional-dependencies]`: `pip install ezcompiler[dev]` is no longer
  valid and only the product extras (`cx-freeze`, `pyinstaller`, `nuitka`,
  `all-compilers`, `tufup`, `r2`) are published. Use `--group dev|test|docs`.
- **CI** runs the test matrix on `ubuntu-24.04` **and** `windows-latest` with
  `--all-extras`, and sets `EZCOMPILER_REQUIRE_EXTRAS=1` so a missing optional
  extra fails the collection instead of skipping the TUF/R2 tests silently.
  `bandit` and `pip-audit` run in a dedicated `security` job, and `bandit` is
  also a pre-commit hook. One `pip-audit` ignore is documented in the workflow:
  `GHSA-qp9x-wp8f-qgjj` (python-tuf 4.0.0) cannot be fixed here because
  tufup 0.10.0 pins `tuf==4.0.*`; drop the ignore when tufup relaxes that bound.
- **`T201`, `S101` and `S603` are no longer ignored globally** in `[tool.ruff]`,
  and `B101` is no longer skipped by bandit — the AGENTS.md rules "never
  `print()` in library code" and "no invariant `assert` in production" are
  enforceable again. Exemptions live in `per-file-ignores` (`tests/**`,
  `examples/**`, `.scripts/**`, `src/ezcompiler/interfaces/**`) or in a targeted
  `# noqa` on the subprocess call concerned.
- **Test markers** available: `slow`, `integration`, `unit`, `cli`, `compiler`,
  `uploader`, `robustness`, `requires_iscc` (needs a real `ISCC.exe` /
  Inno Setup 6 on the machine), `requires_gh` (needs a real, authenticated
  `gh` CLI).
- **Test runner wrapper** (`tests/run_tests.py`) provides options: `--type
  unit|integration|robustness|all`, `--coverage`, `--fast`, `--parallel`,
  `--marker <name>`, `--verbose`. Use `pytest` directly for a single file or
  `-k` keyword filter.
- **Coverage exclusions** (TUF signing / interactive TTY):
  `_tufup_releaser.py`, `cli_interface.py`. The compiler adapters are
  **measured**, including `_nuitka_compiler.py` and `_pyinstaller_compiler.py`
  — their command-line construction is testable code (see
  `_cx_freeze_compiler.py`, which extracts `_run_setup_subprocess()` as a
  mockable seam). Extracting the same seam in the other two is the cheapest
  honest route to the 80% target.

## Testing approach

- Write pytest tests for new functionality; cover happy path **and** edge cases.
- Descriptive names: `test_should_<behavior>_when_<condition>`.
- Run the relevant suite before considering a change done.
- Do not let overall branch coverage drop below its current measured value;
  the CI gate is 70% and the audit target is 80% — prefer adding tests that
  move toward 80%.

## Commits

STOP: Do not stage, commit, or push anything unless the user explicitly
requests it.

Conventional, atomic commits — one purpose per commit, self-contained, reversible.

```text
<type>: <imperative, <=50 chars, no trailing period>

<optional body — explain WHY, wrap ~72 cols>
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `build`, `perf`,
`chore`.

Stage by name, never blanket-add secrets or build artifacts. Branch off `main`
first if needed.

## Documentation

MkDocs Material, organized per the Diátaxis model (`mkdocs.yml`, `docs/`).
API reference uses mkdocstrings — the `api/reference/index.md` page is a
navigation index only (no `:::` directives there, to avoid duplicate primary
URLs). Update docs when changing public behavior or the API surface.

## Working notes

- Match the surrounding code's style, comment density, and idioms.
- Review existing similar code before introducing new patterns.
- Known technical-debt items are no longer tracked as in-code markers (the
  former `[AUDIT Px]` TODOs are gone). **The standing backlog is empty:** branch
  coverage reached the 80% audit target on 2026-10-08 (82.57%). Extracting a
  mockable subprocess seam in `_nuitka_compiler.py` and `_pyinstaller_compiler.py`,
  as `_cx_freeze_compiler.py` already does, remains the cheapest way to raise it
  further, but it is no longer required to clear the target.
- **Two former backlog items are settled; do not reopen them.**
    - *"Migrate the `Base*` ABCs to `Protocol` ports"* — **won't do, the premise
      is wrong.** The two serve different jobs and are meant to coexist: the
      ports are structural contracts at the service boundary
      (`CompilerService` types `_compiler_instance` as `CompilerPort`), while
      the ABCs carry shared implementation the concretes inherit
      (`BaseCompiler` has 2 abstract methods against 6 concrete helpers —
      `_validate_config`, `_prepare_output_directory`, `_extract_error_summary`,
      `_get_include_files_data`, plus `__init__` and the `config`/`zip_needed`
      properties). A `Protocol` provides no implementation, so "migrating"
      would mean duplicating those helpers across every adapter. Current state
      is the target state.
    - *"Drop `from __future__ import annotations`"* — **blocked on Python 3.13,
      not a cleanup.** 8 of the 78 modules pair it with a `TYPE_CHECKING` block,
      and on 3.13 annotations are still evaluated eagerly without it. Verified
      by removing it from two modules: `import ezcompiler` dies on
      `NameError: name 'RepoDestination' is not defined` at
      `_compiler_config.py:135`. For `_types.py` ↔ `shared._compiler_config` the
      `TYPE_CHECKING` guard is also what breaks a real import cycle, so it
      cannot be resolved by moving the import to runtime. This becomes a safe
      mechanical change only once the floor moves to Python 3.14 (PEP 649,
      lazy annotations); until then the import is load-bearing.
- **Type checking has one gate: `ty`** (pre-commit hook + `01-ci`). `pyright` is
  kept in `[tool.pyright]` and in the `dev` extra because it powers Pylance in
  the editor, but it is no longer run in CI: it analysed the same 80 files as
  `ty`, with the same scope and the same result. Don't re-add it as a gate;
  don't remove its config either, editor diagnostics depend on it.
- General coding-assistant capabilities apply, but these project instructions
  take precedence.
