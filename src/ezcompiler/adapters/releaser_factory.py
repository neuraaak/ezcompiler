# ///////////////////////////////////////////////////////////////
# RELEASER_FACTORY - Factory for releaser instances
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Releaser factory - Centralized creation of releaser instances by type."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from typing import Any

from .._types import ReleaserPort
from ..shared.exceptions import ReleaserTypeError
from ._tufup_releaser import TufupReleaser

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ReleaserFactory:
    """Factory class for creating releaser instances."""

    # ------------------------------------------------
    # FACTORY METHODS
    # ------------------------------------------------

    @staticmethod
    def create_releaser(
        release_type: str, config: dict[str, Any] | None = None
    ) -> ReleaserPort:
        """Create a releaser instance for the given type.

        Args:
            release_type: Type of releaser ("tufup")
            config: Configuration dictionary for the releaser

        Returns:
            ReleaserPort: Configured releaser instance (satisfies the Port)

        Raises:
            ReleaserTypeError: If release type is not supported
        """
        normalized = release_type.lower()
        if normalized == "tufup":
            return TufupReleaser(config)
        raise ReleaserTypeError(f"Unsupported release type: {release_type}")

    @staticmethod
    def get_supported_types() -> list[str]:
        """Return the list of supported release backend names."""
        return ["tufup"]
