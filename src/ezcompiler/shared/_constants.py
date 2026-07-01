# ///////////////////////////////////////////////////////////////
# CONSTANTS - Shared release/upload layout constants
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Shared layout constants for the release/update flow.

The upload side (UploaderService) writes the TUF tree under UPDATE_SUBDIR
and the installer zip under RELEASE_SUBDIR; the client side
(UpdaterService) reads the TUF tree from UPDATE_SUBDIR. Keeping these names
in one place prevents the two sides from drifting apart.
"""

from __future__ import annotations

# Subdirectory holding the signed TUF tree (metadata + targets).
UPDATE_SUBDIR = "update"

# Subdirectory holding the distributable installer zip.
RELEASE_SUBDIR = "release"
