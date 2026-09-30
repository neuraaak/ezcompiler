# ///////////////////////////////////////////////////////////////
# VERSION_UTILS - Version string helpers
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Version utils - Pure helpers for reasoning about version strings.

No I/O, no logging: these are predicates used by the publication path to
decide how a release is labelled.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import re

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Marqueurs de pre-release. Aligne sur le workflow 02-tag-sync.yml : toute
# divergence ferait qu'un tag marque pre-release par la CI serait publie
# comme stable, ou l'inverse.
_PRERELEASE_RE = re.compile(r"(alpha|beta|rc|dev|a\d+|b\d+)", re.IGNORECASE)

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def is_prerelease(version: str) -> bool:
    """Whether a version string denotes a pre-release.

    Args:
        version: Version string, e.g. ``"1.2.3"`` or ``"1.2.3-rc.1"``.

    Returns:
        bool: True when the version carries a pre-release marker.

    Example:
        >>> is_prerelease("1.2.3")
        False
        >>> is_prerelease("1.2.3-beta")
        True
    """
    return bool(_PRERELEASE_RE.search(version))
