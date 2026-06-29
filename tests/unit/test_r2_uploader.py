from unittest.mock import MagicMock, patch

import pytest

from ezcompiler.shared.exceptions import UploadError

ENV = {
    "R2_ENDPOINT": "https://acc.r2.cloudflarestorage.com",
    "R2_ACCESS_KEY_ID": "AKIA_TEST",
    "R2_SECRET_ACCESS_KEY": "secret_test",
}


def _make(monkeypatch, client):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    boto3 = MagicMock()
    boto3.client.return_value = client
    with patch.dict("sys.modules", {"boto3": boto3}):
        from ezcompiler.adapters._r2_uploader import R2Uploader

        return R2Uploader({"bucket": "updates"})


def test_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv("R2_ACCESS_KEY_ID", raising=False)
    monkeypatch.setenv("R2_ENDPOINT", ENV["R2_ENDPOINT"])
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", ENV["R2_SECRET_ACCESS_KEY"])
    boto3 = MagicMock()
    with patch.dict("sys.modules", {"boto3": boto3}):
        from ezcompiler.adapters._r2_uploader import R2Uploader

        with pytest.raises(UploadError, match="R2_ACCESS_KEY_ID"):
            R2Uploader({"bucket": "updates"})


def test_upload_directory_puts_each_file(monkeypatch, tmp_path):
    client = MagicMock()
    uploader = _make(monkeypatch, client)

    src = tmp_path / "repo"
    (src / "metadata").mkdir(parents=True)
    (src / "metadata" / "root.json").write_text("{}")
    (src / "targets").mkdir()
    (src / "targets" / "App-1.0.tar.gz").write_bytes(b"x")

    uploader.upload(src, "chan")

    keys = {c.kwargs["Key"] for c in client.upload_file.call_args_list}
    assert "chan/metadata/root.json" in keys
    assert "chan/targets/App-1.0.tar.gz" in keys


def test_download_lists_and_fetches(monkeypatch, tmp_path):
    client = MagicMock()
    client.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "chan/metadata/root.json"}]}
    ]
    uploader = _make(monkeypatch, client)

    local = tmp_path / "local"
    uploader.download("chan", local)

    client.download_file.assert_called_once()
    assert client.download_file.call_args.kwargs["Key"] == "chan/metadata/root.json"
