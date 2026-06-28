import json
from unittest.mock import MagicMock, patch

from ezcompiler.adapters._server_uploader import ServerUploader


def _resp(status, *, content=b"", text=""):
    r = MagicMock()
    r.status_code = status
    r.ok = status == 200
    r.content = content
    r.text = text
    return r


@patch("ezcompiler.adapters._server_uploader.requests.get")
def test_download_metadata_driven(mock_get, tmp_path):
    targets_doc = {"signed": {"targets": {"App-1.0.tar.gz": {}}}}

    def route(url, **_):
        if url.endswith("metadata/timestamp.json"):
            return _resp(200, content=b"{}")
        if url.endswith("metadata/snapshot.json"):
            return _resp(200, content=b"{}")
        if url.endswith("metadata/root.json"):
            return _resp(200, content=b"{}")
        if url.endswith("metadata/targets.json"):
            return _resp(200, content=json.dumps(targets_doc).encode())
        if url.endswith("targets/App-1.0.tar.gz"):
            return _resp(200, content=b"BUNDLE")
        return _resp(404)

    mock_get.side_effect = route
    local = tmp_path / "local"
    ServerUploader({"server_url": "https://updates.example.com"}).download(
        "https://updates.example.com", local
    )

    assert (local / "metadata" / "targets.json").exists()
    assert (local / "targets" / "App-1.0.tar.gz").read_bytes() == b"BUNDLE"


@patch("ezcompiler.adapters._server_uploader.requests.get")
def test_download_first_run_noop(mock_get, tmp_path):
    mock_get.return_value = _resp(404)
    local = tmp_path / "local"
    ServerUploader({"server_url": "https://updates.example.com"}).download(
        "https://updates.example.com", local
    )
    assert not (local / "metadata").exists() or not any((local / "metadata").iterdir())
