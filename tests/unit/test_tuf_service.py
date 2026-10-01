from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.services.tuf_service import TufService
from ezcompiler.shared import TufVersion
from ezcompiler.shared.exceptions import ReleaseError


def _cfg(tmp_path: Path, **kwargs: Any) -> CompilerConfig:
    main_file = tmp_path / "main.py"
    if not main_file.exists():
        main_file.write_text("# m", encoding="utf-8")
    kwargs.setdefault("version", "1.0.0")
    return CompilerConfig(
        project_name="App",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
        **kwargs,
    )


# withdrawn.json ------------------------------------------------------


def test_withdrawn_versions_should_be_empty_without_file(tmp_path: Path) -> None:
    assert TufService.withdrawn_versions(tmp_path) == []


def test_record_withdrawn_should_append_with_timestamp(tmp_path: Path) -> None:
    now = datetime(2026, 10, 1, 10, 0, tzinfo=UTC)
    TufService.record_withdrawn(tmp_path, "1.0.1", now=now)
    TufService.record_withdrawn(tmp_path, "1.0.0", now=now)

    doc = json.loads((tmp_path / "withdrawn.json").read_text("utf-8"))
    assert doc == {
        "withdrawn": [
            {"version": "1.0.1", "withdrawn_at": "2026-10-01T10:00:00Z"},
            {"version": "1.0.0", "withdrawn_at": "2026-10-01T10:00:00Z"},
        ]
    }
    assert TufService.withdrawn_versions(tmp_path) == ["1.0.1", "1.0.0"]


@pytest.mark.parametrize(
    "content",
    ["{not json", '{"withdrawn": "1.0.0"}', '{"withdrawn": [{"v": "1"}]}', "[]"],
)
def test_withdrawn_versions_should_refuse_a_malformed_file(
    tmp_path: Path, content: str
) -> None:
    (tmp_path / "withdrawn.json").write_text(content, encoding="utf-8")

    with pytest.raises(ReleaseError, match="withdrawn.json"):
        TufService.withdrawn_versions(tmp_path)


# ensure_releasable ---------------------------------------------------


@pytest.mark.parametrize("version", ["1.0.1", "1.0.0", "1.0.1-rc.1", "1.0.1rc2"])
def test_ensure_releasable_should_refuse_a_version_not_above_withdrawn(
    tmp_path: Path, version: str
) -> None:
    TufService.record_withdrawn(tmp_path, "1.0.1")

    with pytest.raises(ReleaseError, match="1.0.1 a été retirée"):
        TufService.ensure_releasable(tmp_path, version)


def test_ensure_releasable_should_compare_by_pep440_meaning(tmp_path: Path) -> None:
    TufService.record_withdrawn(tmp_path, "1.2.3-rc.1")

    with pytest.raises(ReleaseError):
        TufService.ensure_releasable(tmp_path, "1.2.3rc1")
    TufService.ensure_releasable(tmp_path, "1.2.3")  # supérieure : acceptée


def test_ensure_releasable_should_accept_a_higher_version(tmp_path: Path) -> None:
    TufService.record_withdrawn(tmp_path, "1.0.1")
    TufService.record_withdrawn(tmp_path, "1.0.0")

    TufService.ensure_releasable(tmp_path, "1.0.2")


def test_ensure_releasable_should_accept_anything_without_withdrawal(
    tmp_path: Path,
) -> None:
    TufService.ensure_releasable(tmp_path, "0.0.1")


def test_ensure_releasable_should_only_block_the_same_non_pep440_string(
    tmp_path: Path,
) -> None:
    TufService.record_withdrawn(tmp_path, "build-42")

    with pytest.raises(ReleaseError):
        TufService.ensure_releasable(tmp_path, "build-42")
    TufService.ensure_releasable(tmp_path, "build-43")


# remove_latest -------------------------------------------------------


def test_remove_latest_should_record_the_removed_version(
    make_tuf_tree, tmp_path: Path
) -> None:
    make_tuf_tree(["1.0.0", "1.0.1"])
    cfg = _cfg(tmp_path)

    removed = TufService.remove_latest(cfg)

    assert removed == "1.0.1"
    assert TufService.withdrawn_versions(tmp_path / "repo") == ["1.0.1"]


def test_remove_latest_should_not_record_on_failure(
    make_tuf_tree, tmp_path: Path
) -> None:
    make_tuf_tree([])
    cfg = _cfg(tmp_path)

    with pytest.raises(ReleaseError):
        TufService.remove_latest(cfg)

    assert TufService.withdrawn_versions(tmp_path / "repo") == []


# status --------------------------------------------------------------


def test_status_should_list_versions_flags_and_expirations(
    make_tuf_tree, tmp_path: Path
) -> None:
    make_tuf_tree(["1.0.0", "1.0.2", "1.0.10"], required=("1.0.10",))
    TufService.record_withdrawn(tmp_path / "repo", "0.9.0")

    status = TufService.status(_cfg(tmp_path))

    assert status.repo_dir == tmp_path / "repo"
    assert status.versions == (
        TufVersion("1.0.10", required=True, has_patch=True),
        TufVersion("1.0.2", required=False, has_patch=True),
        TufVersion("1.0.0", required=False, has_patch=False),
    )
    assert list(status.expirations) == ["root", "targets", "snapshot", "timestamp"]
    assert all(d.tzinfo is not None for d in status.expirations.values())
    assert status.withdrawn == ("0.9.0",)


def test_status_should_ignore_other_projects_archives(tmp_path: Path) -> None:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    for role in ("root", "targets", "snapshot", "timestamp"):
        signed: dict[str, Any] = {"expires": "2030-01-01T00:00:00Z"}
        if role == "targets":
            signed["targets"] = {"Other-2.0.0.tar.gz": {}, "App-1.0.0.tar.gz": {}}
        (meta / f"{role}.json").write_text(
            json.dumps({"signed": signed}), encoding="utf-8"
        )

    status = TufService.status(_cfg(tmp_path))

    assert [v.version for v in status.versions] == ["1.0.0"]
    assert status.versions[0].required is False  # pas de bloc custom


def test_status_should_refuse_an_uninitialized_tree(tmp_path: Path) -> None:
    with pytest.raises(ReleaseError, match="tuf init"):
        TufService.status(_cfg(tmp_path))


def test_status_should_refuse_an_unreadable_metadata_file(tmp_path: Path) -> None:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    (meta / "root.json").write_text("{broken", encoding="utf-8")

    with pytest.raises(ReleaseError, match="root.json"):
        TufService.status(_cfg(tmp_path))


# ------------------------------------------------
# read_tree_version
# ------------------------------------------------


def _write_targets(tmp_path: Path, names: list[str]) -> None:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    doc = {"signed": {"targets": {n: {} for n in names}}}
    (meta / "targets.json").write_text(json.dumps(doc), encoding="utf-8")


def test_tree_version_is_the_highest_signed_archive(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    _write_targets(
        tmp_path,
        [
            "App-1.9.0.tar.gz",
            "App-1.10.0.tar.gz",
            "App-1.10.0.patch",
            "Other-9.0.tar.gz",
        ],
    )
    assert TufService.read_tree_version(cfg) == "1.10.0"


def test_tree_version_requires_signed_targets(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    (tmp_path / "repo" / "metadata").mkdir(parents=True)
    (tmp_path / "repo" / "metadata" / "root.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ReleaseError, match="pipeline"):
        TufService.read_tree_version(cfg)


def test_tree_version_requires_an_archive_of_the_project(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    _write_targets(tmp_path, ["Other-1.0.0.tar.gz"])
    with pytest.raises(ReleaseError, match="App"):
        TufService.read_tree_version(cfg)


def test_tree_version_rejects_unreadable_metadata(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    (meta / "targets.json").write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ReleaseError, match="illisible"):
        TufService.read_tree_version(cfg)


@pytest.mark.parametrize("version", ["1.2.3-rc.1", "1.0.0-beta", "2.0.0"])
def test_tree_version_keeps_the_spelling_tufup_used(
    tmp_path: Path, version: str
) -> None:
    """tufup nomme l'archive avec la chaine brute : pas de forme normalisee."""
    cfg = _cfg(tmp_path)
    _write_targets(tmp_path, [f"App-{version}.tar.gz"])
    tree = TufService.read_tree_version(cfg)
    assert tree == version
    assert TufService.same_version(tree, version)


def test_same_version_compares_meaning_not_spelling() -> None:
    assert TufService.same_version("1.2.3-rc.1", "1.2.3rc1")
    assert not TufService.same_version("1.2.3", "1.2.4")
    assert TufService.same_version("not-pep440", "not-pep440")
    assert not TufService.same_version("not-pep440", "other")


def test_read_tree_version_should_return_none_for_an_emptied_tree_when_allowed(
    make_tuf_tree, tmp_path: Path
) -> None:
    make_tuf_tree(["1.0.0"])
    cfg = _cfg(tmp_path)
    TufService.remove_latest(cfg)

    assert TufService.read_tree_version(cfg, allow_empty=True) is None
    with pytest.raises(ReleaseError, match="aucune archive"):
        TufService.read_tree_version(cfg)


# needs_full_archive --------------------------------------------------


def _withdraw(tmp_path: Path, *versions: str) -> None:
    for version in versions:
        TufService.record_withdrawn(tmp_path / "repo", version)


@pytest.mark.parametrize(
    ("archives", "withdrawn", "expected"),
    [
        (["App-1.0.0.tar.gz"], [], False),
        (["App-1.0.0.tar.gz"], ["1.0.1"], True),
        (["App-1.0.0.tar.gz", "App-1.0.2.tar.gz"], ["1.0.1"], False),
        (["App-1.0.0.tar.gz"], ["0.9.0", "1.0.1rc1"], True),
        (["App-1.0.1.tar.gz"], ["1.0.1-rc.1"], False),
        ([], ["1.0.0"], True),
    ],
)
def test_needs_full_archive_when_a_withdrawn_version_is_above_the_tree(
    tmp_path: Path, archives: list[str], withdrawn: list[str], expected: bool
) -> None:
    _write_targets(tmp_path, archives)
    _withdraw(tmp_path, *withdrawn)
    assert TufService.needs_full_archive(tmp_path / "repo", "App") is expected


def test_needs_full_archive_should_be_false_without_metadata(tmp_path: Path) -> None:
    assert TufService.needs_full_archive(tmp_path / "repo", "App") is False
