from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.services.publish_service import PublishService
from ezcompiler.shared import ReleasePreflight
from ezcompiler.shared.exceptions import ConfigurationError


@pytest.fixture()
def cfg(tmp_path: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    return CompilerConfig(
        version="2.0.0",
        project_name="MyApp",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
        release_destination="github",
        release_endpoint="owner/repo",
    )


def test_should_delegate_to_the_service_when_publishing_the_update_tree(
    cfg: CompilerConfig,
) -> None:
    with patch.object(PublishService, "publish_update") as publish:
        EzCompiler(cfg).publish_update(destination="D:/out")
    publish.assert_called_once()
    assert publish.call_args.kwargs["destination"] == "D:/out"


def test_should_default_the_tag_to_the_config_version_when_publishing(
    cfg: CompilerConfig, tmp_path: Path
) -> None:
    asset = tmp_path / "MyApp-2.0.0.zip"
    asset.write_bytes(b"x")
    recap = ReleasePreflight(
        destination="github",
        is_platform=True,
        publisher_name="GitHub Releases (gh)",
        repo="owner/repo",
        assets=(asset,),
    )
    with (
        patch.object(PublishService, "preflight_release", return_value=recap),
        patch.object(
            PublishService, "publish_release", return_value="https://u"
        ) as publish,
    ):
        url = EzCompiler(cfg).publish_release()

    assert url == "https://u"
    assert publish.call_args.kwargs["tag"] == "v2.0.0"
    assert publish.call_args.kwargs["title"] == "MyApp v2.0.0"
    assert publish.call_args.args[1] == [asset]


def test_should_return_the_recap_when_preflighting_from_the_python_api(
    cfg: CompilerConfig,
) -> None:
    publisher = MagicMock()
    publisher.exists.return_value = False
    publisher.get_publisher_name.return_value = "GitHub Releases (gh)"
    with (
        patch.object(PublishService, "resolve_publisher", return_value=publisher),
        patch(
            "ezcompiler.services.publish_service.PipelineService.stage_versioned_assets",
            return_value=[],
        ),
    ):
        recap = EzCompiler(cfg).preflight_release()

    assert recap.is_platform is True
    assert recap.repo == "owner/repo"


def test_should_refuse_to_publish_when_the_project_is_not_initialized() -> None:
    with pytest.raises(ConfigurationError):
        EzCompiler().publish_release()
