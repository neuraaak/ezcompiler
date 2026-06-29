# AGENTS.md

Instructions for AI coding agents working on **ezcompiler**. This file is
self-contained — there is no external instruction tree to consult.

## Project

`ezcompiler` is a Python framework that compiles Python projects into Windows
executables, then versions, packages (ZIP) and distributes them. It exposes a
unified interface over three compilers (Cx_Freeze, PyInstaller, Nuitka).

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
                ConfigService, TemplateService, UploaderService, ReleaseService)
adapters/     ← concrete compilers, uploaders & releaser behind ports, + factories
shared/       ← domain models (CompilerConfig, CompilationResult) + exceptions/
utils/        ← technical helpers + validators/
assets/       ← templates and static resources (no upward deps)
types.py      ← type aliases + the three @runtime_checkable Protocol ports
```

### Ports (`types.py`)

Three structural contracts that decouple services from concrete adapters:

| Port           | Key methods                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `CompilerPort` | `compile()`, `get_compiler_name()`, `zip_needed`, `config`                                  |
| `UploaderPort` | `upload(source_path, destination)`, `get_uploader_name()`                                   |
| `ReleaserPort` | `release(bundle_dir, app_name, version, repo_dir)`, `init_keys(...)`, `get_releaser_name()` |

Concrete implementations live in `adapters/` with a `_` prefix (`_cx_freeze_compiler.py`, `_disk_uploader.py`, `_tufup_releaser.py`). Always go through the factories — never instantiate adapters directly.

### Pipeline flow

`run_pipeline()` (the primary production path) executes stages in order:

```text
compile → zip → release → upload
```

When both release and upload are active, `PipelineService.assemble_release_dir()` builds a **flat** `dist/release/` directory (signed TUF `metadata/*` + `targets/*` plus the unsigned zip asset, no sub-folders — GitHub-release style), then uploads it as a single `upload()` call. The working TUF repo (`tuf_repository/`) stays structured for incremental patches; only the published folder is flattened. `EzCompiler.release(publish=True)` is **deprecated** — the pipeline handles the full sequence.

Config loading: `ConfigService` flattens nested blocks (`compilation`, `upload`, `release`, `advanced`) before passing kwargs to `CompilerConfig.__init__()`. A new config block **must** be added to the flatten step in `from_dict()` or it will raise an unexpected-keyword error.

**Import contracts are enforced in CI by import-linter** (`[tool.importlinter]`
in `pyproject.toml`). The layer flow is strictly:

`interfaces → services → adapters → utils → shared`

`types` and `assets` must never import from upper layers. Before adding an
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
- **Naming:** `*Service`, `Base*` (ports), `*Config`, `*Error`,
  `_*_utils.py`, `_*_service.py`.
- **Docstrings:** Google style.
- **Logging:** uses `ezplog` in **lib_mode** — the library stays passive until
  the host application initializes logging. Never use `print()` in library
  code. Level rules by layer: `interfaces/` — all levels; `services/` — INFO,
  WARNING, ERROR; `utils/` — DEBUG, ERROR only.
- **Prefer** `pathlib` over `os.path`, f-strings, full type hints. No hard-coded
  credentials or absolute paths; no committed commented-out code.

## Toolchain

| Task          | Command                                                     |
| ------------- | ----------------------------------------------------------- |
| Install (dev) | `uv pip install -e ".[dev]"` (or `pip install -e ".[dev]"`) |
| Lint          | `ruff check .`                                              |
| Format        | `ruff format .` (check: `ruff format --check .`)            |
| Type check    | `ty check src/ezcompiler/` and `pyright src/ezcompiler/`    |
| Import rules  | `PYTHONPATH=src lint-imports`                               |
| Security      | `bandit -r src/ezcompiler`                                  |
| Tests         | `pytest`                                                    |

- **ruff** rules: `E W F I B C4 UP S T20 ARG PIE SIM`, line length 88,
  double quotes. See `[tool.ruff]` for per-file ignores.
- **Coverage:** branch coverage, `--cov-fail-under=60` (audit target is 80%).
  Some subprocess/TTY modules are omitted from coverage (see
  `[tool.coverage.run] omit`).
- **Test markers** available: `slow`, `integration`, `unit`, `cli`, `compiler`,
  `uploader`, `robustness`.
- **Test runner wrapper** (`tests/run_tests.py`) provides options: `--type
  unit|integration|robustness|all`, `--coverage`, `--fast`, `--parallel`,
  `--marker <name>`, `--verbose`. Use `pytest` directly for a single file or
  `-k` keyword filter.
- **Coverage exclusions** (subprocess/TTY — not unit-testable):
  `_nuitka_compiler.py`, `_pyinstaller_compiler.py`, `_tufup_releaser.py`,
  `cli_interface.py`.

## Testing approach

- Write pytest tests for new functionality; cover happy path **and** edge cases.
- Descriptive names: `test_should_<behavior>_when_<condition>`.
- Run the relevant suite before considering a change done.
- Do not let overall branch coverage drop below its current measured value;
  the CI gate is 60% and the audit target is 80% — prefer adding tests that
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
- Known technical-debt items are tracked as `[AUDIT Px]` TODO markers in the
  code (e.g. raising coverage, typing `compiler_instance`, merging exception
  hierarchies, migrating `Base*` ABCs to `Protocol` ports, dropping
  `from __future__ import annotations`, choosing one type checker). Treat those
  as the backlog; don't silently undo them.
- General coding-assistant capabilities apply, but these project instructions
  take precedence.
