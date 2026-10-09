from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ezcompiler import CompilerConfig
from ezcompiler.interfaces.cli_interface import main
from ezcompiler.shared import TufStatus, TufVersion
from ezcompiler.shared.exceptions import ReleaseError

_CLI = "ezcompiler.interfaces.cli_interface"


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


def _status(tmp_path: Path, **overrides: Any) -> TufStatus:
    now = datetime.now(UTC)
    fields: dict[str, Any] = {
        "repo_dir": tmp_path / "repo",
        "versions": (
            TufVersion("1.0.2", required=True, has_patch=True),
            TufVersion("1.0.0", required=False, has_patch=False),
        ),
        "expirations": {
            "root": now + timedelta(days=300),
            "targets": now + timedelta(days=30),
            "snapshot": now + timedelta(days=30),
            "timestamp": now + timedelta(days=30),
        },
        "withdrawn": ("1.0.1",),
    }
    fields.update(overrides)
    return TufStatus(**fields)


def _run(tmp_path: Path, status: TufStatus | Exception, *args: str):
    side = (
        {"side_effect": status}
        if isinstance(status, Exception)
        else {"return_value": status}
    )
    with (
        patch(
            f"{_CLI}.ConfigService.build_compiler_config", return_value=_cfg(tmp_path)
        ),
        patch(f"{_CLI}.TufService.status", **side),
    ):
        return CliRunner().invoke(main, ["tuf", *args])


def _flat(output: str) -> str:
    return " ".join(output.split())


# status --------------------------------------------------------------


def test_status_should_show_versions_flags_and_withdrawals(tmp_path: Path) -> None:
    result = _run(tmp_path, _status(tmp_path), "status")

    out = _flat(result.output)
    assert result.exit_code == 0, result.output
    assert "1.0.2 mandatory patch" in out
    assert out.index("1.0.2") < out.index("1.0.0")
    assert "Withdrawn versions: 1.0.1" in out


def test_status_should_warn_when_a_role_expires_soon(tmp_path: Path) -> None:
    soon = datetime.now(UTC) + timedelta(days=2)
    st = _status(tmp_path)
    st = _status(tmp_path, expirations={**st.expirations, "timestamp": soon})

    result = _run(tmp_path, st, "status")

    assert result.exit_code == 0
    assert "expiring soon" in result.output
    assert "ezcompiler tuf refresh" in _flat(result.output)


def test_status_should_round_days_up_and_not_warn_at_seven_days(
    tmp_path: Path,
) -> None:
    almost_week = datetime.now(UTC) + timedelta(days=7) - timedelta(minutes=1)
    st = _status(tmp_path)
    st = _status(tmp_path, expirations={**st.expirations, "targets": almost_week})

    result = _run(tmp_path, st, "status")

    assert result.exit_code == 0
    assert "(7 d)" in result.output
    assert "expiring soon" not in result.output


def test_status_should_not_warn_on_a_freshly_signed_default_tree(
    make_tuf_tree, tmp_path: Path
) -> None:
    """tufup defaults: targets and snapshot expire after 7 days."""
    make_tuf_tree(["1.0.0"])
    with patch(
        f"{_CLI}.ConfigService.build_compiler_config", return_value=_cfg(tmp_path)
    ):
        result = CliRunner().invoke(main, ["tuf", "status"])

    assert result.exit_code == 0, result.output
    for role in ("targets", "snapshot"):
        line = next(ln for ln in result.output.splitlines() if f" {role} " in ln)
        assert "(7 d)" in line, line
        assert "expiring soon" not in line, line


def test_status_should_flag_an_expired_root_with_its_refresh_command(
    tmp_path: Path,
) -> None:
    past = datetime.now(UTC) - timedelta(days=1)
    st = _status(tmp_path)
    st = _status(tmp_path, expirations={**st.expirations, "root": past})

    result = _run(tmp_path, st, "status")

    assert result.exit_code == 0
    assert "expired" in result.output
    assert "ezcompiler tuf refresh --role root" in _flat(result.output)


def test_status_should_say_when_no_version_remains(tmp_path: Path) -> None:
    result = _run(tmp_path, _status(tmp_path, versions=(), withdrawn=()), "status")

    out = _flat(result.output)
    assert "(none)" in out
    assert "Withdrawn versions: none" in out


def test_status_should_exit_1_on_an_uninitialized_tree(tmp_path: Path) -> None:
    result = _run(tmp_path, ReleaseError("No TUF tree initialized"), "status")

    assert result.exit_code == 1
    assert "No TUF tree initialized" in result.output


# remove-latest -------------------------------------------------------


def _remove(
    tmp_path: Path,
    *args: str,
    status: TufStatus | None = None,
    stdin: str | None = None,
    keys: bool = True,
):
    if keys:
        (tmp_path / "keystore").mkdir(exist_ok=True)
    removed: list[str] = []

    def _fake_remove(_cfg: Any) -> str:
        removed.append("called")
        return "1.0.2"

    with (
        patch(
            f"{_CLI}.ConfigService.build_compiler_config", return_value=_cfg(tmp_path)
        ),
        patch(f"{_CLI}.TufService.status", return_value=status or _status(tmp_path)),
        patch(f"{_CLI}.TufService.remove_latest", side_effect=_fake_remove),
        patch(f"{_CLI}.TufService.keys_dir", return_value=tmp_path / "keystore"),
    ):
        result = CliRunner().invoke(main, ["tuf", "remove-latest", *args], input=stdin)
    return result, removed


def test_remove_latest_should_show_recap_and_ask(tmp_path: Path) -> None:
    result, removed = _remove(tmp_path, stdin="y\n")

    out = _flat(result.output)
    assert result.exit_code == 0, result.output
    assert "Version withdrawn: 1.0.2" in out
    assert "App-1.0.2.tar.gz" in out and "App-1.0.2.patch" in out
    assert "New latest version: 1.0.0" in out
    assert "Withdraw this version?" in out
    assert removed == ["called"]
    assert "ezcompiler compile --required" in out
    assert "ezcompiler publish update" in out


def test_remove_latest_should_stop_when_declined(tmp_path: Path) -> None:
    result, removed = _remove(tmp_path, stdin="n\n")

    assert result.exit_code == 1
    assert removed == []


def test_remove_latest_should_skip_prompt_with_yes(tmp_path: Path) -> None:
    result, removed = _remove(tmp_path, "--yes")

    assert result.exit_code == 0, result.output
    assert "Withdraw this version?" not in result.output
    assert removed == ["called"]


def test_remove_latest_should_warn_when_removing_the_only_version(
    tmp_path: Path,
) -> None:
    only = _status(tmp_path, versions=(TufVersion("1.0.2", False, False),))
    result, _ = _remove(tmp_path, "--yes", status=only)

    out = _flat(result.output)
    assert "New latest version: none" in out
    assert "will offer no version at all" in out


def test_remove_latest_should_fail_before_recap_without_keys(tmp_path: Path) -> None:
    result, removed = _remove(tmp_path, "--yes", keys=False)

    assert result.exit_code == 1
    assert "Version withdrawn" not in result.output
    assert removed == []


def test_remove_latest_should_fail_when_tree_is_empty(tmp_path: Path) -> None:
    result, removed = _remove(tmp_path, "--yes", status=_status(tmp_path, versions=()))

    assert result.exit_code == 1
    assert "No version to withdraw" in result.output
    assert removed == []


# init ----------------------------------------------------------------


def test_init_should_exit_1_with_a_message_without_config(
    monkeypatch, tmp_path: Path
) -> None:
    from ezcompiler.shared.exceptions import ConfigurationError

    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(main, ["tuf", "init"])

    assert result.exit_code == 1, result.output
    assert isinstance(result.exception, SystemExit), repr(result.exception)
    assert not isinstance(result.exception, ConfigurationError)
    assert "No configuration source found" in _flat(result.output)


# options communes ----------------------------------------------------


def _write_config(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / "main.py").write_text("# m", encoding="utf-8")
    cfg_file = tmp_path / "ezcompiler.yaml"
    cfg_file.write_text("x: 1", encoding="utf-8")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'x'\n", encoding="utf-8")
    return cfg_file, pyproject


@pytest.mark.parametrize("command", ["init", "refresh"])
@pytest.mark.parametrize("short", [False, True])
def test_init_and_refresh_should_accept_config_and_pyproject(
    tmp_path: Path, command: str, short: bool
) -> None:
    cfg_file, pyproject = _write_config(tmp_path)
    args = (
        ["-c", str(cfg_file), "-p", str(pyproject)]
        if short
        else ["--config", str(cfg_file), "--pyproject", str(pyproject)]
    )
    with (
        patch(
            f"{_CLI}.ConfigService.build_compiler_config",
            return_value=_cfg(tmp_path),
        ) as build,
        patch(f"{_CLI}.ReleaseService.init_release", return_value=True),
        patch(
            "ezcompiler.services.release_service.ReleaseService.refresh_expiration",
            return_value=tmp_path / "repo",
        ),
    ):
        result = CliRunner().invoke(main, ["tuf", command, *args])

    assert result.exit_code == 0, result.output
    build.assert_called_once_with(config_path=cfg_file, pyproject_path=pyproject)
