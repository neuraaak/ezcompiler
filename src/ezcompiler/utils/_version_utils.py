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

# Pre-release markers as components, not as substrings.
_PRERELEASE_RE = re.compile(
    r"(?<![a-z])(?:alpha|beta|rc|dev|a\d+|b\d+)(?![a-z])", re.IGNORECASE
)

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
    version_without_local_metadata = version.partition("+")[0]
    return bool(_PRERELEASE_RE.search(version_without_local_metadata))
