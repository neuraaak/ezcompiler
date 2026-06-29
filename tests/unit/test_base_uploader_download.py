from pathlib import Path

import pytest

from ezcompiler.adapters.base_uploader import BaseUploader
from ezcompiler.shared.exceptions import UploadError


class _DummyUploader(BaseUploader):
    def upload(self, source_path: Path, destination: str) -> None:
        pass

    def get_uploader_name(self) -> str:
        return "Dummy"


def test_download_default_raises_upload_error(tmp_path):
    uploader = _DummyUploader()
    with pytest.raises(UploadError, match="does not support download"):
        uploader.download("remote/prefix", tmp_path)
