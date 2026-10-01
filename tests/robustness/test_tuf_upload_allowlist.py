from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ezcompiler.services.publish_service import PublishService
from ezcompiler.services.uploader_service import UploaderService
from ezcompiler.shared import CompilerConfig
from ezcompiler.shared.exceptions import UploadError


def _cfg(tmp_path: Path, repo_dir: Path, **kwargs: Any) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_enabled=True,
        tuf_repo_dir=repo_dir,
        **kwargs,
    )


def _files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


@pytest.mark.robustness
def test_publish_update_should_never_upload_the_default_keystore(
    make_tuf_tree, tmp_path: Path
) -> None:
    repo_dir, keys_dir = make_tuf_tree(["1.0.0", "1.0.1"], keys_in_repo=True)
    assert keys_dir == repo_dir / "keystore"
    assert any(keys_dir.iterdir())
    (repo_dir / "withdrawn.json").write_text('{"withdrawn": []}\n', encoding="utf-8")
    remote = tmp_path / "remote"
    cfg = _cfg(tmp_path, repo_dir, repo_destination="disk", repo_endpoint=str(remote))

    PublishService.publish_update(cfg)

    published = _files(remote / "update")
    assert not [f for f in published if f.startswith("keystore")]
    key_bytes = {p.read_bytes() for p in keys_dir.iterdir() if p.is_file()}
    leaked = [f for f in published if (remote / "update" / f).read_bytes() in key_bytes]
    assert leaked == [], f"private key leaked: {leaked}"
    # Même disposition distante pour les fichiers publics.
    expected = {
        f
        for f in _files(repo_dir)
        if f.startswith(("metadata/", "targets/")) or f == "withdrawn.json"
    }
    assert published == expected
    assert "metadata/root.json" in published


@pytest.mark.robustness
@pytest.mark.parametrize(
    ("repo_destination", "repo_endpoint"),
    [
        ("disk", "remote"),
        ("server", "https://updates.example.com"),
        ("r2", "bucket/chan"),
    ],
)
def test_upload_tuf_repo_should_stage_only_public_files_for_every_backend(
    make_tuf_tree, monkeypatch, tmp_path: Path, repo_destination, repo_endpoint
) -> None:
    repo_dir, _ = make_tuf_tree(["1.0.0"], keys_in_repo=True)
    cfg = _cfg(
        tmp_path,
        repo_dir,
        repo_destination=repo_destination,
        repo_endpoint=repo_endpoint,
        repo_public_url="https://pub.example.com",
    )
    seen: list[set[str]] = []
    monkeypatch.setattr(
        UploaderService,
        "upload",
        staticmethod(lambda **kw: seen.append(_files(kw["source_path"]))),
    )

    UploaderService.upload_tuf_repo(cfg, repo_dir, repo_destination, None, None)

    assert len(seen) == 1
    assert seen[0], "nothing staged"
    assert all(f.startswith(("metadata/", "targets/")) for f in seen[0])


@pytest.mark.robustness
def test_upload_tuf_repo_should_refuse_a_tree_without_metadata(
    monkeypatch, tmp_path: Path
) -> None:
    repo_dir = tmp_path / "repo"
    (repo_dir / "keystore").mkdir(parents=True)
    cfg = _cfg(tmp_path, repo_dir, repo_destination="disk", repo_endpoint="remote")
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        UploaderService, "upload", staticmethod(lambda **kw: calls.append(kw))
    )

    with pytest.raises(UploadError, match="metadata"):
        UploaderService.upload_tuf_repo(cfg, repo_dir, "disk", None, None)
    assert calls == []
