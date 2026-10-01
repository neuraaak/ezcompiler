from __future__ import annotations

import json
from pathlib import Path

import pytest

from ezcompiler.adapters._tufup_releaser import TufupReleaser
from ezcompiler.shared.exceptions import ReleaseError, SigningKeyError


def _signed_targets(repo_dir: Path) -> dict:
    doc = json.loads((repo_dir / "metadata" / "targets.json").read_text("utf-8"))
    return doc["signed"]


def test_release_should_mark_the_archive_required(make_tuf_tree) -> None:
    repo_dir, _ = make_tuf_tree(["1.0.0", "1.0.1"], required=("1.0.1",))

    targets = _signed_targets(repo_dir)["targets"]

    assert targets["App-1.0.1.tar.gz"]["custom"]["tufup"]["required"] is True
    assert targets["App-1.0.0.tar.gz"]["custom"]["tufup"]["required"] is False


def test_remove_latest_should_drop_archive_and_patch_and_resign(
    make_tuf_tree,
) -> None:
    repo_dir, keys_dir = make_tuf_tree(["1.0.0", "1.0.1"])
    version_before = _signed_targets(repo_dir)["version"]

    removed = TufupReleaser({"keys_dir": keys_dir}).remove_latest(
        "App", repo_dir, keys_dir
    )

    signed = _signed_targets(repo_dir)
    assert removed == "1.0.1"
    assert sorted(signed["targets"]) == ["App-1.0.0.tar.gz"]
    assert signed["version"] == version_before + 1
    on_disk = sorted(p.name for p in (repo_dir / "targets").iterdir())
    assert on_disk == ["App-1.0.0.tar.gz"]


def test_remove_latest_should_return_the_raw_version_spelling(
    make_tuf_tree,
) -> None:
    repo_dir, keys_dir = make_tuf_tree(["1.0.0", "1.0.1-rc.1"])

    removed = TufupReleaser({"keys_dir": keys_dir}).remove_latest(
        "App", repo_dir, keys_dir
    )

    assert removed == "1.0.1-rc.1"


def test_remove_latest_should_allow_removing_the_only_version(
    make_tuf_tree,
) -> None:
    repo_dir, keys_dir = make_tuf_tree(["1.0.0"])

    removed = TufupReleaser({"keys_dir": keys_dir}).remove_latest(
        "App", repo_dir, keys_dir
    )

    assert removed == "1.0.0"
    assert _signed_targets(repo_dir)["targets"] == {}


def test_remove_latest_should_fail_when_nothing_to_remove(make_tuf_tree) -> None:
    repo_dir, keys_dir = make_tuf_tree([])

    with pytest.raises(ReleaseError, match="Aucune version à retirer"):
        TufupReleaser({"keys_dir": keys_dir}).remove_latest("App", repo_dir, keys_dir)


def test_remove_latest_should_fail_without_keys(tmp_path: Path) -> None:
    with pytest.raises(SigningKeyError):
        TufupReleaser().remove_latest("App", tmp_path / "repo", tmp_path / "absent")


def test_remove_latest_should_fail_on_uninitialized_repo(tmp_path: Path) -> None:
    keys_dir = tmp_path / "keystore"
    keys_dir.mkdir()

    with pytest.raises(ReleaseError, match="not initialized"):
        TufupReleaser().remove_latest("App", tmp_path / "repo", keys_dir)
