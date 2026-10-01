from __future__ import annotations

import pytest

from ezcompiler.adapters._server_uploader import ServerUploader

_URL = "https://uploads.example.com"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "EZCOMPILER_SERVER_USERNAME",
        "EZCOMPILER_SERVER_PASSWORD",
        "EZCOMPILER_SERVER_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_should_read_basic_auth_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La CLI ne passe jamais de secret en argument : l'env le fournit."""
    monkeypatch.setenv("EZCOMPILER_SERVER_USERNAME", "deploy")
    monkeypatch.setenv("EZCOMPILER_SERVER_PASSWORD", "s3cret")
    uploader = ServerUploader({"server_url": _URL})
    assert uploader._prepare_auth() == ("deploy", "s3cret")


def test_should_read_the_api_key_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EZCOMPILER_SERVER_API_KEY", "tok")
    uploader = ServerUploader({"server_url": _URL})
    assert uploader._prepare_headers()["Authorization"] == "Bearer tok"


def test_explicit_config_wins_over_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EZCOMPILER_SERVER_USERNAME", "from-env")
    monkeypatch.setenv("EZCOMPILER_SERVER_PASSWORD", "from-env")
    uploader = ServerUploader(
        {"server_url": _URL, "username": "explicit", "password": "pw"}
    )
    assert uploader._prepare_auth() == ("explicit", "pw")


def test_no_credentials_means_no_auth() -> None:
    uploader = ServerUploader({"server_url": _URL})
    assert uploader._prepare_auth() is None
    assert "Authorization" not in uploader._prepare_headers()
