from pathlib import Path
from unittest.mock import patch

from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared import CompilerConfig


def _config(tmp_path: Path) -> CompilerConfig:
    main = tmp_path / "main.py"
    main.write_text("# main", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.0",
        project_name="App",
        main_file=str(main),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        upload_structure="r2",
        r2_bucket="updates",
        r2_remote_prefix="myapp",
        update_repo_url="https://x.r2.dev/myapp",
    )
    cfg.release_needed = True
    cfg.tufup_repo_dir = tmp_path / "repo"
    (tmp_path / "repo" / "metadata").mkdir(parents=True)
    return cfg


@patch("ezcompiler.interfaces.python_api.UploaderService")
def test_upload_r2_pushes_tuf_tree(mock_us, tmp_path):
    cfg = _config(tmp_path)
    compiler = EzCompiler(cfg)
    compiler.upload()

    # l'arbre TUF natif (repo_dir) est poussé, pas le dossier plat
    assert mock_us.upload.called
    call = mock_us.upload.call_args
    assert call.kwargs["upload_type"] == "r2"
    assert Path(call.kwargs["source_path"]) == tmp_path / "repo"
    assert call.kwargs["destination"] == "myapp"
    assert call.kwargs["upload_config"] == {"bucket": "updates"}
