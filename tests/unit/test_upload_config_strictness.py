from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ezcompiler.adapters._disk_uploader import DiskUploader
from ezcompiler.adapters._server_uploader import ServerUploader
from ezcompiler.services.uploader_service import UploaderService
from ezcompiler.shared.exceptions import UploadError


@pytest.mark.uploader
def test_should_reject_a_misspelled_key_when_configuring_the_server_uploader() -> None:
    """Otherwise a misspelled `cert` disables mTLS without a word."""
    with pytest.raises(UploadError, match="certt"):
        ServerUploader(
            {
                "server_url": "https://updates.example.com",
                "verifyssl": False,
                "certt": "/p/c.pem",
                "timeoutt": 1,
            }
        )


@pytest.mark.uploader
def test_should_reject_a_misspelled_key_when_configuring_the_disk_uploader() -> None:
    with pytest.raises(UploadError, match="overwrit"):
        DiskUploader({"destination_path": "D:/out", "overwrit": True})


@pytest.mark.uploader
def test_should_accept_the_keys_injected_by_the_service_when_uploading_to_disk(
    tmp_path: Path,
) -> None:
    uploader = DiskUploader({"destination_path": str(tmp_path), "overwrite": True})
    assert uploader._config["overwrite"] is True


@pytest.mark.uploader
def test_should_not_mutate_the_caller_config_when_uploading_twice(
    monkeypatch, tmp_path: Path
) -> None:
    """Deux uploads successifs partagent le dict de l'appelant : une mutation
    in place would make the second inherit the first's destination_path."""
    seen: list[dict[str, Any]] = []

    class _Spy:
        def __init__(self, config: dict[str, Any] | None = None) -> None:
            seen.append(dict(config or {}))

        def upload(self, source_path: Path, destination: str) -> None:
            return None

        def get_uploader_name(self) -> str:
            return "Spy"

    monkeypatch.setattr(
        "ezcompiler.adapters.UploaderFactory.create_uploader",
        staticmethod(lambda _type, config: _Spy(config)),
    )
    source = tmp_path / "a.zip"
    source.write_bytes(b"x")
    shared = {"overwrite": True}

    UploaderService.upload(
        source_path=source,
        upload_type="disk",
        destination="D:/out",
        upload_config=shared,
    )
    UploaderService.upload(
        source_path=source,
        upload_type="server",
        destination="https://updates.example.com",
        upload_config=shared,
    )

    assert shared == {"overwrite": True}
    assert "destination_path" not in seen[1]
