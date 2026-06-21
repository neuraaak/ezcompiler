from __future__ import annotations

from pathlib import Path

from ezcompiler.adapters._server_uploader import ServerUploader


def _server(monkeypatch, captured):
    up = ServerUploader({"server_url": "https://srv.example.com"})

    def _fake_perform(_self, source_path: Path, destination: str) -> None:
        captured.append((Path(source_path).name, destination))

    monkeypatch.setattr(ServerUploader, "_perform_upload", _fake_perform)
    return up


def test_directory_upload_posts_each_file_with_relative_path(monkeypatch, tmp_path):
    root = tmp_path / "publish"
    (root / "repository" / "metadata").mkdir(parents=True)
    (root / "repository" / "metadata" / "timestamp.json").write_text("{}", "utf-8")
    (root / "downloads").mkdir()
    (root / "downloads" / "App.zip").write_bytes(b"zip")

    captured: list[tuple[str, str]] = []
    _server(monkeypatch, captured).upload(root, "ignored")

    dests = sorted(d for _, d in captured)
    assert "downloads/App.zip" in dests
    assert "repository/metadata/timestamp.json" in dests


def test_single_file_upload_unchanged(monkeypatch, tmp_path):
    f = tmp_path / "App.zip"
    f.write_bytes(b"zip")
    captured: list[tuple[str, str]] = []
    _server(monkeypatch, captured).upload(f, "App.zip")
    assert captured == [("App.zip", "App.zip")]
