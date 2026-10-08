# ///////////////////////////////////////////////////////////////
# PUBLISHER_FACTORY - Factory for creating publisher instances
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Publisher factory - Factory for creating release publisher instances.

Callers go through this factory rather than instantiating concrete
publishers, which stay private to the adapters package.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Local imports
from .._types import PublisherPort
from ..shared.exceptions import PublisherTypeError
from ._github_publisher import GitHubPublisher

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# GitLab is deliberately absent: the `glab` flags are not verified
# first-hand. An explicit refusal beats an adapter that guesses.
_SUPPORTED: tuple[str, ...] = ("github",)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class PublisherFactory:
    """
    Factory class for creating release publisher instances.

    Example:
        >>> publisher = PublisherFactory.create_publisher("github", {"repo": "o/r"})
        >>> PublisherFactory.get_supported_types()
        ['github']
    """

    # ////////////////////////////////////////////////
    # FACTORY METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def create_publisher(
        publish_type: str, config: dict[str, Any] | None = None
    ) -> PublisherPort:
        """
        Create a publisher instance based on the specified type.

        Args:
            publish_type: Platform name ("github").
            config: Configuration dictionary for the publisher (default: None).

        Returns:
            PublisherPort: Configured publisher instance (satisfies the Port).

        Raises:
            PublisherTypeError: If the platform is not supported.
        """
        publish_type = publish_type.lower()

        if publish_type == "github":
            return GitHubPublisher(config)

        if publish_type == "gitlab":
            raise PublisherTypeError(
                "'gitlab' publication is not implemented yet. "
                "Utiliser release_destination='github', ou une destination "
                "de fichiers ('disk', 'server', 'r2')."
            )

        raise PublisherTypeError(
            f"Unsupported publication platform: '{publish_type}'. "
            f"Supported: {', '.join(_SUPPORTED)}."
        )

    @staticmethod
    def get_supported_types() -> list[str]:
        """
        Get the list of supported publication platforms.

        Returns:
            list[str]: Supported platform names.
        """
        return list(_SUPPORTED)
