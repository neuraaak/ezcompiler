# Deploy Documentation Workflow

`docs.yml` builds and deploys the MkDocs Material documentation to GitHub Pages
(`https://neuraaak.github.io/ezcompiler/`). It is normally called by `auto-tag.yml`
after a successful publish, but can also be run manually.

## Triggers

| Event               | How                                             |
| ------------------- | ----------------------------------------------- |
| `workflow_call`     | Called by `auto-tag.yml` after publish succeeds |
| `workflow_dispatch` | Manual run from the Actions tab                 |

## Job: `deploy`

Single job, runs on `ubuntu-24.04`. Steps in order:

| Step               | Command / Action                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Checkout           | Full history (`fetch-depth: 0`) required for git-cliff                                           |
| Install            | `uv sync --frozen` with `docs` and `test` extras                                                 |
| Tests              | `uv run pytest` with coverage — produces `htmlcov/` and `coverage.xml` (job fails if tests fail) |
| Import contracts   | `PYTHONPATH=src uv run lint-imports`                                                             |
| Architecture graph | Runs `.scripts/dev/generate_architecture_graph.py` if present                                    |
| Changelog          | `git-cliff` writes `docs/changelog.md` from conventional commits                                 |
| Deploy             | `uv run mkdocs gh-deploy --force` pushes to `gh-pages`                                           |

## Concurrency

A dedicated `deploy-docs` concurrency group with `cancel-in-progress: false`
ensures that a docs deployment in progress is never interrupted mid-push.

## Permissions

`contents: write` is required so mkdocs can push to the `gh-pages` branch.

## GitHub Pages setup

Pages must be configured to serve from the `gh-pages` branch:

```text
Repository → Settings → Pages → Source: Deploy from a branch → gh-pages / root
```

`mkdocs gh-deploy` creates and updates this branch automatically.

## Local preview

```bash
uv sync --extra docs
uv run mkdocs serve
# Open http://127.0.0.1:8000
```

Strict build (fails on warnings):

```bash
uv run mkdocs build --strict
```

## Manual trigger

```bash
gh workflow run docs.yml
```

## Troubleshooting

**Tests fail** — coverage generation fails if tests are broken. Fix the tests
and re-run. Do not add `|| true` to mask failures.

**mkdocstrings "Module not found"** — verify the module path in `docs/api/*.md`
matches the installed package. Run `uv run python -c "import ezcompiler"` to
confirm the package is importable.

**Permission denied on gh-pages** — check that `contents: write` is present and
that no branch-protection rule blocks force-pushes to `gh-pages`.

**Changelog not updating** — ensure `cliff.toml` exists at the repo root and
that commits follow the conventional commit format.
