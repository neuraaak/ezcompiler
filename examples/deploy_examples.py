# ///////////////////////////////////////////////////////////////
# DEPLOY_EXAMPLES - Deploy example configs to .tmp/ for testing
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Deploy example configuration files to .tmp/ directory for testing.

Copies all .example template files from examples/ to .tmp/ at the
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

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def deploy_templates() -> None:
    """Copy .example files to .tmp/, stripping the .example extension."""
    TMP_DIR.mkdir(exist_ok=True)

    for template in EXAMPLES_DIR.glob("*.example"):
        dest_name = template.stem  # removes .example suffix
        dest = TMP_DIR / dest_name
        shutil.copy2(template, dest)
        print(f"  {template.name} -> .tmp/{dest_name}")


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """Deploy example files to .tmp/ directory."""
    print(f"Deploying examples to {TMP_DIR}")
    deploy_templates()
    print("Done.")


if __name__ == "__main__":
    main()
