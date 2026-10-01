from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.services.publish_service import PublishService
from ezcompiler.shared.exceptions import PublishError, PublisherTypeError, ReleaseError


def _make_config(tmp_path: Path, **kwargs: Any) -> CompilerConfig:
    """Meme construction que _cfg dans test_python_api_upload.py."""
    main = tmp_path / "main.py"
    if not main.exists():
        main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
        **kwargs,
    )


# ------------------------------------------------
# resolve_publisher — le coeur du chantier
# ------------------------------------------------


@pytest.mark.parametrize("dest", ["disk", "server", "r2"])
def test_should_not_resolve_a_publisher_for_file_destinations(tmp_path, dest) -> None:
    cfg = _make_config(tmp_path, release_destination=dest, release_endpoint="x/y")
    assert PublishService.resolve_publisher(cfg) is None


def test_should_resolve_a_publisher_for_github(tmp_path) -> None:
    cfg = _make_config(tmp_path, release_destination="github")
    pub = PublishService.resolve_publisher(cfg)
    assert pub is not None
    assert "GitHub" in pub.get_publisher_name()


def test_should_pass_the_endpoint_as_the_repo(tmp_path) -> None:
    cfg = _make_config(
        tmp_path, release_destination="github", release_endpoint="neuraaak/ezcompiler"
    )
    pub = PublishService.resolve_publisher(cfg)
    assert pub.config["repo"] == "neuraaak/ezcompiler"


def test_should_honour_the_destination_override(tmp_path) -> None:
    cfg = _make_config(tmp_path, release_destination="disk")
    assert PublishService.resolve_publisher(cfg, "github") is not None


# ------------------------------------------------
# publish_release — routage effectif
# ------------------------------------------------


def test_should_route_github_to_the_publisher(tmp_path) -> None:
    cfg = _make_config(tmp_path, release_destination="github")
    asset = tmp_path / "App-1.0.0.zip"
    asset.write_bytes(b"x")
    fake = MagicMock()
    fake.publish.return_value = "https://github.com/o/r/releases/tag/v1.0.0"

    with patch.object(PublishService, "resolve_publisher", return_value=fake):
        url = PublishService.publish_release(
            cfg, [asset], tag="v1.0.0", title="App 1.0.0"
        )

    assert url == "https://github.com/o/r/releases/tag/v1.0.0"
    fake.publish.assert_called_once()
    assert fake.publish.call_args.kwargs["tag"] == "v1.0.0"


def test_should_route_disk_to_the_uploader_unchanged(tmp_path) -> None:
    cfg = _make_config(
        tmp_path, release_destination="disk", release_endpoint=str(tmp_path / "out")
    )
    asset = tmp_path / "App-1.0.0.zip"
    asset.write_bytes(b"x")

    with (
        patch(
            "ezcompiler.services.publish_service.UploaderService.upload_release_zip"
        ) as upload,
        patch(
            "ezcompiler.services.publish_service.PipelineService.assemble_release_dir",
            return_value=tmp_path / "release",
        ),
    ):
        url = PublishService.publish_release(
            cfg, [asset], tag="v1.0.0", title="App 1.0.0"
        )

    assert url is None
    upload.assert_called_once()


def test_should_preserve_the_release_subdir_on_the_file_path(tmp_path) -> None:
    """Le chemin fichiers delegue a l'existant : <dest>/release/ est conserve."""
    cfg = _make_config(
        tmp_path, release_destination="disk", release_endpoint=str(tmp_path / "out")
    )
    asset = tmp_path / "App-1.0.0.zip"
    asset.write_bytes(b"x")

    with (
        patch(
            "ezcompiler.services.publish_service.UploaderService.upload_release_zip"
        ) as upload,
        patch(
            "ezcompiler.services.publish_service.PipelineService.assemble_release_dir",
            return_value=tmp_path / "release",
        ),
    ):
        PublishService.publish_release(cfg, [asset], tag="v1.0.0", title="T")

    # Signature : (config, release_root, rel_dest, destination, upload_config)
    assert upload.call_args.args[2] == "disk"


def test_should_forward_every_publication_flag(tmp_path) -> None:
    cfg = _make_config(tmp_path, release_destination="github")
    asset = tmp_path / "a.zip"
    asset.write_bytes(b"x")
    fake = MagicMock()
    fake.publish.return_value = "u"

    with patch.object(PublishService, "resolve_publisher", return_value=fake):
        PublishService.publish_release(
            cfg,
            [asset],
            tag="v1.0.0rc1",
            title="T",
            notes="notes litterales",
            prerelease=True,
            draft=True,
        )

    kwargs = fake.publish.call_args.kwargs
    assert kwargs["notes"] == "notes litterales"
    assert kwargs["prerelease"] is True
    assert kwargs["draft"] is True


# ------------------------------------------------
# publish_update
# ------------------------------------------------


def test_should_upload_the_tuf_tree_to_the_update_subdir(tmp_path) -> None:
    cfg = _make_config(
        tmp_path, repo_destination="disk", release_endpoint="", tuf_enabled=True
    )
    with patch("ezcompiler.services.publish_service.UploaderService.upload") as upload:
        PublishService.publish_update(cfg)
    assert "update" in str(upload.call_args.kwargs["destination"])


def test_publish_update_never_resolves_a_publisher(tmp_path) -> None:
    """Un arbre TUF exige des chemins HTTP stables : jamais d'assets de release."""
    cfg = _make_config(tmp_path, repo_destination="disk", tuf_enabled=True)
    with (
        patch("ezcompiler.services.publish_service.UploaderService.upload"),
        patch.object(PublishService, "resolve_publisher") as resolve,
    ):
        PublishService.publish_update(cfg)
    resolve.assert_not_called()


# ------------------------------------------------
# Garde-fous (revue tasks 6-7)
# ------------------------------------------------


def test_should_refuse_gitlab_explicitly(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path, release_destination="disk")
    with pytest.raises(PublisherTypeError, match="gitlab"):
        PublishService.resolve_publisher(cfg, "gitlab")


def test_should_refuse_a_file_endpoint_overridden_to_github(tmp_path: Path) -> None:
    """-rld github sur une config r2 : le bucket ne doit pas partir en --repo."""
    cfg = _make_config(tmp_path, release_destination="r2", release_endpoint="bkt/pre/x")
    with pytest.raises(PublishError, match="owner/repo"):
        PublishService.resolve_publisher(cfg, "github")


def test_should_refuse_an_empty_asset_list_on_the_platform_path(
    tmp_path: Path,
) -> None:
    cfg = _make_config(tmp_path, release_destination="github")
    fake = MagicMock()
    with (
        patch.object(PublishService, "resolve_publisher", return_value=fake),
        pytest.raises(PublishError, match="[Aa]ucun"),
    ):
        PublishService.publish_release(cfg, [], tag="v1.0.0", title="T")
    fake.publish.assert_not_called()


def test_should_publish_with_the_publisher_given_by_the_caller(
    tmp_path: Path,
) -> None:
    cfg = _make_config(tmp_path, release_destination="github")
    asset = tmp_path / "a.zip"
    asset.write_bytes(b"x")
    given = MagicMock()
    given.publish.return_value = "u"
    with patch.object(PublishService, "resolve_publisher") as resolve:
        PublishService.publish_release(
            cfg, [asset], tag="v1.0.0", title="T", publisher=given
        )
    resolve.assert_not_called()
    given.publish.assert_called_once()


# ------------------------------------------------
# read_tree_version
# ------------------------------------------------


def _write_targets(tmp_path: Path, names: list[str]) -> None:
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    doc = {"signed": {"targets": {n: {} for n in names}}}
    (meta / "targets.json").write_text(json.dumps(doc), encoding="utf-8")


def test_tree_version_is_the_highest_signed_archive(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path)
    _write_targets(
        tmp_path,
        [
            "App-1.9.0.tar.gz",
            "App-1.10.0.tar.gz",
            "App-1.10.0.patch",
            "Other-9.0.tar.gz",
        ],
    )
    assert PublishService.read_tree_version(cfg) == "1.10.0"


def test_tree_version_requires_signed_targets(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path)
    (tmp_path / "repo" / "metadata").mkdir(parents=True)
    (tmp_path / "repo" / "metadata" / "root.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ReleaseError, match="pipeline"):
        PublishService.read_tree_version(cfg)


def test_tree_version_requires_an_archive_of_the_project(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path)
    _write_targets(tmp_path, ["Other-1.0.0.tar.gz"])
    with pytest.raises(ReleaseError, match="App"):
        PublishService.read_tree_version(cfg)


def test_tree_version_rejects_unreadable_metadata(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path)
    meta = tmp_path / "repo" / "metadata"
    meta.mkdir(parents=True)
    (meta / "targets.json").write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ReleaseError, match="illisible"):
        PublishService.read_tree_version(cfg)
