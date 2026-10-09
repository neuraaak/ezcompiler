from __future__ import annotations

import tomllib
from pathlib import Path


def test_tufup_extra_declared() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    extras = data["project"]["optional-dependencies"]
    assert "tufup" in extras
    assert any(dep.startswith("tufup") for dep in extras["tufup"])


def test_should_keep_dev_tooling_out_of_the_published_extras() -> None:
    """`pip install ezcompiler[dev]` must not be a valid command: the dev
    tooling lives in [dependency-groups] (PEP 735), which is not published."""
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    extras = data["project"]["optional-dependencies"]
    groups = data["dependency-groups"]
    assert not {"dev", "test", "docs"} & set(extras)
    assert {"dev", "test", "docs"} <= set(groups)


def test_tufup_adapter_excluded_from_coverage() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    omit = data["tool"]["coverage"]["run"]["omit"]
    assert any("_tufup_releaser.py" in entry for entry in omit)
