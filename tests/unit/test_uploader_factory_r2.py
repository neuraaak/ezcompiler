from unittest.mock import MagicMock, patch

from ezcompiler.adapters.uploader_factory import UploaderFactory


def test_r2_in_supported_types():
    assert "r2" in UploaderFactory.get_supported_types()


def test_create_r2_uploader(monkeypatch):
    monkeypatch.setenv("R2_ENDPOINT", "https://acc.r2.cloudflarestorage.com")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "k")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "s")
    with patch.dict("sys.modules", {"boto3": MagicMock()}):
        uploader = UploaderFactory.create_uploader("r2", {"bucket": "updates"})
    assert uploader.get_uploader_name() == "R2 Uploader"
