# Publish to PyPI Workflow

`publish-pypi.yml` builds the package and publishes it to PyPI. It is normally
triggered by `auto-tag.yml` after a new version tag is created, but can also
be run manually.

## Triggers

| Event               | How                                                    |
| ------------------- | ------------------------------------------------------ |
| `workflow_call`     | Called by `auto-tag.yml` with `version` + `tag` inputs |
| `workflow_dispatch` | Manual run from the Actions tab                        |

Manual runs have a `skip_tests` option (default `false`, not recommended).

## Authentication

Publishing uses **OIDC trusted publishing** — no stored secret. The workflow
mints a short-lived token that PyPI trusts directly via the `id-token: write`
permission. The trusted publisher is configured on pypi.org under the
ezcompiler project settings.

## Jobs

```text
validate (build + test) ──► publish (OIDC deploy)
```

### `validate` — Validate & Build

1. Extract version from `pyproject.toml` and compare with the `version` input
   (mismatch → immediate failure)
2. `uv sync --frozen --extra dev`
3. `PYTHONPATH=src uv run lint-imports` — import contracts
4. `uv run pytest` — full suite with coverage (skipped if `skip_tests=true`)
5. `uv build` — produces `dist/*.whl` and `dist/*.tar.gz`
6. `uv run twine check dist/*` — validates the package metadata
7. Wheel smoke-test in an isolated venv
8. Upload `dist/` as a job artifact (retained 1 day)

### `publish` — Publish to PyPI (OIDC)

Runs only if `validate` succeeds. Downloads the artifact built upstream
(no rebuild). Steps:

1. `actions/download-artifact` — retrieves `dist/`
2. `pypa/gh-action-pypi-publish` — publishes via OIDC, no password

The job runs in the `pypi` environment. Configure required reviewers there
in Repository → Settings → Environments if you want a manual gate.

## Concurrency

A `publish` concurrency group with `cancel-in-progress: false` prevents two
simultaneous publish runs. A run in progress is never interrupted.

## Release workflow

```text
1. Bump version in pyproject.toml
2. Commit & push to main
   → auto-tag.yml detects a new version, creates vX.Y.Z tag
   → triggers publish-pypi.yml automatically
3. Verify on https://pypi.org/project/ezcompiler/
```

Manual trigger via gh CLI:

```bash
gh workflow run publish-pypi.yml
```

## Troubleshooting

**Version mismatch** — the `version` input from auto-tag differs from
`pyproject.toml`. Bump the version, commit, and push again.

**OIDC failure** — check that the trusted publisher on pypi.org matches
the repo name, workflow filename (`publish-pypi.yml`), and environment name
(`pypi`) exactly.

**Tests fail** — run `uv run pytest` locally, fix, push. Do not use
`skip_tests=true` to work around failures.
