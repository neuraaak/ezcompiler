from __future__ import annotations

from pathlib import Path

import pytest

from ezcompiler.services.release_service import ReleaseService


class _RepoBuildingReleaser:
    """Writes a realistic repository/ tree and a sibling keystore/ with keys."""

    def release(self, bundle_dir, app_name, version, repo_dir, *, patch=True) -> Path:
        repo = repo_dir / "repository"
        (repo / "metadata").mkdir(parents=True, exist_ok=True)
        (repo / "targets").mkdir(parents=True, exist_ok=True)
        (repo / "metadata" / "root.json").write_text("{}", encoding="utf-8")
        keystore = repo_dir / "keystore"
        keystore.mkdir(parents=True, exist_ok=True)
        (keystore / "root").write_text("PRIVATE-KEY", encoding="utf-8")
        return repo

    def get_releaser_name(self) -> str:
        return "fake"


@pytest.mark.robustness
def test_published_tree_contains_no_private_key(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ezcompiler.services.release_service.ReleaserFactory.create_releaser",
        lambda *_a, **_k: _RepoBuildingReleaser(),
    )
    captured: dict = {}
    monkeypatch.setattr(
        "ezcompiler.services.release_service.UploaderService.upload",
        lambda **kwargs: captured.update(kwargs),
        raising=False,
    )

    ReleaseService().release_and_publish(
        bundle_dir=tmp_path / "bundle",
        app_name="MyApp",
        version="1.0.0",
        repo_dir=tmp_path / "repo",
        publish=True,
        upload_type="disk",
        destination=str(tmp_path / "remote"),
    )

    published_root: Path = captured["source_path"]
    assert published_root.name == "repository"
    leaked = [
        p
        for p in published_root.rglob("*")
        if p.is_file()
        and "PRIVATE-KEY" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert leaked == [], f"private key leaked into published tree: {leaked}"
