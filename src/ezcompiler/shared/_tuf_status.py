# ///////////////////////////////////////////////////////////////
# _TUF_STATUS - Snapshot of the local TUF tree
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Value objects describing the local signed TUF tree."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class TufVersion:
    """One application version signed in the tree."""

    version: str
    required: bool
    has_patch: bool


@dataclass(frozen=True)
class TufStatus:
    """State of the local tree, as clients would see it once published."""

    repo_dir: Path
    versions: tuple[TufVersion, ...]
    expirations: dict[str, datetime]
    withdrawn: tuple[str, ...]
