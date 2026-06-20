# ///////////////////////////////////////////////////////////////
# DEPLOY_EXAMPLES - Deploy example files to .tmp/ and .tmp/configs/
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Deploy example configuration files to .tmp/configs/ for testing.

Copies all .example template files from examples/ to .tmp/configs/ at the
project root, stripping the .example extension.

Usage:
    python examples/deploy_examples.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"
TMP_DIR = PROJECT_ROOT / ".tmp"
CONFIGS_DIR = TMP_DIR / "configs"

# Config file suffixes → .tmp/configs/ ; others (main.py, setup.py) → .tmp/
CONFIG_SUFFIXES = {".json", ".yaml", ".yml", ".toml"}

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def deploy_templates() -> None:
    """Copy .example files — configs to .tmp/configs/, scripts to .tmp/."""
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

    for template in EXAMPLES_DIR.glob("*.example"):
        dest_name = template.stem  # removes .example suffix
        # Route by the file's inner extension (.json, .yaml, .py, …)
        inner_suffix = Path(dest_name).suffix
        if inner_suffix in CONFIG_SUFFIXES:
            dest = CONFIGS_DIR / dest_name
            rel = f".tmp/configs/{dest_name}"
        else:
            dest = TMP_DIR / dest_name
            rel = f".tmp/{dest_name}"
        shutil.copy2(template, dest)
        print(f"  {template.name} -> {rel}")


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """Deploy example files to .tmp/ (scripts) and .tmp/configs/ (configs)."""
    print(f"Deploying examples to {TMP_DIR}")
    deploy_templates()
    print("Done.")


if __name__ == "__main__":
    main()
