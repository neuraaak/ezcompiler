# How to contribute changes locally

Set up a local development workflow for implementing and validating changes in EzCompiler.

## 🔧 Prerequisites

- Python 3.11+
- Git
- A local clone of the repository

## 📝 Steps

### 1. Create your environment and install dependencies

=== "uv workflow"

    ```bash
    uv sync --extra dev --extra docs --extra test
    ```

=== "pip editable install"

    ```bash
    python -m venv .venv
    . .venv/Scripts/activate
    pip install -e ".[dev,docs,test]"
    ```

### 2. Apply formatting and linting checks

```bash
ruff format src tests
ruff check src tests
```

### 3. Run type checking

```bash
ty check src/ezcompiler/
```

### 4. Verify layer dependency contracts

```bash
PYTHONPATH=src lint-imports
```

### 5. Run the test suite

```bash
pytest tests/
```

### 6. Build the documentation in strict mode

```bash
mkdocs build --strict
```

## ✅ Quality gate checklist

- [ ] `ruff format` and `ruff check` complete without errors.
- [ ] `ty check` completes with expected diagnostics only.
- [ ] `lint-imports` reports no contract violations.
- [ ] `pytest` passes for all impacted modules.
- [ ] `mkdocs build --strict` succeeds with no warnings.
- [ ] Any changed docs remain copy-paste runnable.

## ✅ Result

Your local environment is ready for safe contributions with formatting, typing,
architecture contract validation, tests, and documentation checks all passing.
