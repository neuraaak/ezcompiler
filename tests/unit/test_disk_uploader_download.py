from ezcompiler.adapters._disk_uploader import DiskUploader


def test_download_copies_remote_tree(tmp_path):
    remote = tmp_path / "remote"
    (remote / "metadata").mkdir(parents=True)
    (remote / "metadata" / "root.json").write_text("{}")
    (remote / "targets").mkdir()
    (remote / "targets" / "App-1.0.tar.gz").write_bytes(b"data")

    local = tmp_path / "local"
    DiskUploader().download(str(remote), local)

    assert (local / "metadata" / "root.json").read_text() == "{}"
    assert (local / "targets" / "App-1.0.tar.gz").read_bytes() == b"data"


def test_download_missing_remote_is_noop(tmp_path):
    local = tmp_path / "local"
    DiskUploader().download(str(tmp_path / "does-not-exist"), local)
    assert not any(local.rglob("*")) if local.exists() else True
