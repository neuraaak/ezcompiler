from pathlib import Path
from unittest.mock import patch

from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared import CompilerConfig


def _config(
    tmp_path: Path, release_destination: str = "disk", release_endpoint: str = ""
) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        repo_destination="r2",
        repo_endpoint="updates/myapp",
        release_destination=release_destination,
        release_endpoint=release_endpoint,
        tuf_enabled=True,
        tuf_repo_dir=tmp_path / "repo",
    )
    (tmp_path / "repo" / "metadata").mkdir(parents=True)
    return cfg


@patch("ezcompiler.interfaces.python_api.UploaderService")
def test_upload_r2_pushes_tuf_tree(mock_us, tmp_path):
    cfg = _config(tmp_path)
    compiler = EzCompiler(cfg)
    compiler.upload()

    assert mock_us.upload_release.called
    call = mock_us.upload_release.call_args
    assert call.kwargs["config"] is cfg
    assert Path(call.kwargs["repo_dir"]) == tmp_path / "repo"
    assert call.kwargs["release_root"] is None  # r2 repo → pas de zip


@patch("ezcompiler.services.pipeline_service.PipelineService.assemble_release_dir")
@patch("ezcompiler.interfaces.python_api.UploaderService")
def test_upload_r2_release_destination_assembles_release_root(
    mock_us, mock_assemble, tmp_path
):
    cfg = _config(tmp_path, release_destination="r2", release_endpoint="releases/myapp")
    fake_release = tmp_path / "release"
    mock_assemble.return_value = fake_release
    compiler = EzCompiler(cfg)
    compiler.upload()

    mock_assemble.assert_called_once()
    call = mock_us.upload_release.call_args
    assert call.kwargs["release_root"] == fake_release
