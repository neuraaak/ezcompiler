# ///////////////////////////////////////////////////////////////
# _RELEASE_PREFLIGHT - Pre-publication recap of a release
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Value object describing a release before it is published.

``PublishService.preflight_release()`` runs every cheap check (CLI present
and authenticated, tag free, artifacts staged) and returns this recap. The
interfaces layer only displays it and asks for confirmation: it never holds
a ``PublisherPort`` nor decides the publisher/uploader routing.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass, field
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ReleasePreflight:
    """What a release publication would do, once every check has passed.

    Attributes:
        destination: Resolved release destination (``github``, ``disk``, …).
        is_platform: True when the destination is a release platform, so the
            publication is irreversible and must be confirmed.
        publisher_name: Human-readable publisher name, platform path only.
        repo: Target ``owner/repo``, or ``None`` when inferred by the CLI.
        assets: Artifacts that would be attached, platform path only.
    """

    destination: str
    is_platform: bool
    publisher_name: str | None = None
    repo: str | None = None
    assets: tuple[Path, ...] = field(default_factory=tuple)
