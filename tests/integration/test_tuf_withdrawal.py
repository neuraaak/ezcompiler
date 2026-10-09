from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.cli_interface import main
from ezcompiler.services.release_service import ReleaseService
from ezcompiler.services.tuf_service import TufService
from ezcompiler.shared.exceptions import ReleaseError

pytestmark = pytest.mark.integration


def _release(tmp_path: Path, version: str, *, required: bool = False) -> None:
    bundle = tmp_path / f"fix-bundle-{version}"
    bundle.mkdir()
    (bundle / "app.exe").write_bytes(version.encode() * 1000)
    ReleaseService.release_and_publish(
        bundle_dir=bundle,
        app_name="App",
        version=version,
        repo_dir=tmp_path / "repo",
        releaser_config={"keys_dir": tmp_path / "keystore"},
        required=required,
    )


def test_withdraw_then_ship_a_required_fix(make_tuf_tree, tmp_path: Path) -> None:
    make_tuf_tree(["1.0.0", "1.0.1"])
    main_file = tmp_path / "main.py"
    main_file.write_text("# m", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.1",
        project_name="App",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
    )

    with patch(
        "ezcompiler.interfaces.cli_interface.ConfigService.build_compiler_config",
        return_value=cfg,
    ):
        result = CliRunner().invoke(main, ["tuf", "remove-latest", "--yes"])
    assert result.exit_code == 0, result.output

    with pytest.raises(ReleaseError, match="withdrawn"):
        _release(tmp_path, "1.0.1")

    _release(tmp_path, "1.0.2", required=True)

    status = TufService.status(cfg)
    assert [v.version for v in status.versions] == ["1.0.2", "1.0.0"]
    assert status.versions[0].required is True
    assert status.withdrawn == ("1.0.1",)
    targets = json.loads(
        (tmp_path / "repo" / "metadata" / "targets.json").read_text("utf-8")
    )["signed"]["targets"]
    assert "App-1.0.1.tar.gz" not in targets
    assert targets["App-1.0.2.tar.gz"]["custom"]["tufup"]["required"] is True


def _targets(tmp_path: Path) -> dict:
    return json.loads(
        (tmp_path / "repo" / "metadata" / "targets.json").read_text("utf-8")
    )["signed"]["targets"]


def test_first_release_after_a_withdrawal_should_ship_the_full_archive_only(
    make_tuf_tree, tmp_path: Path
) -> None:
    """A client on 1.0.1 (withdrawn) cannot apply a 1.0.0->1.0.2 patch."""
    make_tuf_tree(["1.0.0", "1.0.1"])
    assert "App-1.0.1.patch" in _targets(tmp_path)  # release normale : patch
    main_file = tmp_path / "main.py"
    main_file.write_text("# m", encoding="utf-8")
    cfg = CompilerConfig(
        version="1.0.1",
        project_name="App",
        main_file=str(main_file),
        include_files={"files": [], "folders": []},
        output_folder=tmp_path / "dist",
        tuf_repo_dir=tmp_path / "repo",
        tuf_keys_dir=tmp_path / "keystore",
    )
    assert TufService.remove_latest(cfg) == "1.0.1"

    _release(tmp_path, "1.0.2")

    targets = _targets(tmp_path)
    assert "App-1.0.2.tar.gz" in targets
    assert "App-1.0.2.patch" not in targets
    assert not (tmp_path / "repo" / "targets" / "App-1.0.2.patch").exists()

    # Once the withdrawn version is left behind, patches resume.
    _release(tmp_path, "1.0.3")
    assert "App-1.0.3.patch" in _targets(tmp_path)
