# ///////////////////////////////////////////////////////////////
# EXAMPLES - Example project scaffolding
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Examples module - Provides example project files for EzCompiler.

This module copies example files (.example) from the assets/examples directory
into a .tmp folder at the current working directory, stripping the '.example'
suffix so they can be used directly for compilation testing.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

EXAMPLES_DIR = Path(__file__).parent
EXAMPLE_SUFFIX = ".example"

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def scaffold_examples(target_dir: Path | None = None) -> Path:
    """
    Copy example files to a .tmp directory, removing the '.example' suffix.

    Creates a '.tmp' folder in the given directory (or cwd) if it does not
    already exist, then copies every '*.example' file from assets/examples
    into it with the '.example' extension stripped.

    Args:
        target_dir: Root directory where '.tmp' will be created.
                    Defaults to the current working directory.

    Returns:
        Path: The .tmp directory path containing the copied files.
    """
    root = target_dir or Path.cwd()
    tmp_dir = root / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for source in EXAMPLES_DIR.glob(f"*{EXAMPLE_SUFFIX}"):
        # Strip the .example suffix → "main.py.example" becomes "main.py"
        dest_name = source.name[: -len(EXAMPLE_SUFFIX)]
        dest = tmp_dir / dest_name
        shutil.copy2(source, dest)

    return tmp_dir
