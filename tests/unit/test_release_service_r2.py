from unittest.mock import MagicMock, patch

from ezcompiler.services.release_service import ReleaseService


@patch("ezcompiler.services.release_service.UploaderService")
@patch("ezcompiler.services.release_service.ReleaserFactory")
def test_pull_before_downloads_then_releases(mock_rf, mock_us, tmp_path):
    repo = tmp_path / "repo"
    releaser = MagicMock()
    releaser.release.return_value = repo
    mock_rf.create_releaser.return_value = releaser

    ReleaseService.release_and_publish(
        bundle_dir=tmp_path / "bundle",
        app_name="App",
        version="1.0",
        repo_dir=repo,
        publish=True,
        pull_before=True,
        upload_type="r2",
        destination="myapp",
        upload_config={"bucket": "updates"},
    )

    assert mock_us.download.called
    assert releaser.release.called
    assert mock_us.upload.called
