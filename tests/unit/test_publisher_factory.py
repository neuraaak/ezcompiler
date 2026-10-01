from __future__ import annotations

import pytest

from ezcompiler._types import PublisherPort
from ezcompiler.adapters import PublisherFactory
from ezcompiler.shared.exceptions import PublisherTypeError


def test_should_create_a_github_publisher() -> None:
    pub = PublisherFactory.create_publisher("github")
    assert isinstance(pub, PublisherPort)
    assert "GitHub" in pub.get_publisher_name()


def test_should_be_case_insensitive() -> None:
    assert isinstance(PublisherFactory.create_publisher("GitHub"), PublisherPort)


def test_should_forward_config_to_the_publisher() -> None:
    pub = PublisherFactory.create_publisher("github", {"repo": "o/r"})
    assert pub.config["repo"] == "o/r"


def test_should_reject_an_unknown_type() -> None:
    with pytest.raises(PublisherTypeError, match="nope"):
        PublisherFactory.create_publisher("nope")


def test_should_reject_gitlab_until_it_is_implemented() -> None:
    """GitLab est hors perimetre v4.1.0 : echouer clairement, pas silencieusement."""
    with pytest.raises(PublisherTypeError, match="gitlab"):
        PublisherFactory.create_publisher("gitlab")


def test_should_list_supported_types() -> None:
    assert PublisherFactory.get_supported_types() == ["github"]


def test_concrete_publishers_are_not_exported_from_adapters() -> None:
    import ezcompiler.adapters as adapters

    assert "GitHubPublisher" not in adapters.__all__
    assert "PublisherFactory" in adapters.__all__
