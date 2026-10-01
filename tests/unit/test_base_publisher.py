from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from ezcompiler.adapters.base_publisher import BasePublisher
from ezcompiler.shared.exceptions import PublishAuthError, PublishCliError


class _Fake(BasePublisher):
    _cli_name = "faketool"
    _install_hint = "https://example.test/install"

    def exists(self, tag: str) -> bool:
        return False

    def publish(
        self,
        assets: list[Path],
        *,
        tag: str,
        title: str,
        notes: str | None = None,
        prerelease: bool = False,
        draft: bool = False,
    ) -> str:
        return ""

    def get_publisher_name(self) -> str:
        return "Fake"


def test_should_raise_with_install_hint_when_cli_is_absent() -> None:
    with (
        patch("shutil.which", return_value=None),
        pytest.raises(PublishCliError) as exc,
    ):
        _Fake()._resolve_cli()
    assert "faketool" in str(exc.value)
    assert "https://example.test/install" in str(exc.value)


def test_should_return_absolute_path_when_cli_is_present() -> None:
    with patch("shutil.which", return_value="C:\\bin\\faketool.exe"):
        assert _Fake()._resolve_cli() == "C:\\bin\\faketool.exe"


def test_should_raise_auth_error_when_auth_status_fails() -> None:
    pub = _Fake()
    completed = subprocess.CompletedProcess(
        args=["faketool", "auth", "status"],
        returncode=1,
        stdout="",
        stderr="not logged in",
    )
    with (
        patch.object(pub, "_run_cli", return_value=completed),
        pytest.raises(PublishAuthError) as exc,
    ):
        pub._check_auth()
    assert "faketool auth login" in str(exc.value)


def test_should_pass_when_authenticated() -> None:
    pub = _Fake()
    completed = subprocess.CompletedProcess(
        args=["faketool", "auth", "status"], returncode=0, stdout="ok", stderr=""
    )
    with patch.object(pub, "_run_cli", return_value=completed):
        pub._check_auth()


def test_should_never_invoke_a_shell() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 0, "", "")
        _Fake()._run_cli(["release", "view", "v1.0.0"])
    assert run.call_args.kwargs.get("shell", False) is False
    assert run.call_args.kwargs["capture_output"] is True
    assert isinstance(run.call_args.args[0], list)


def test_should_surface_stderr_when_cli_exits_non_zero() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 2, "", "boom details")
        with pytest.raises(PublishCliError) as exc:
            _Fake()._run_cli(["release", "create"], check=True)
    assert "boom details" in str(exc.value)
    assert "2" in str(exc.value)


def test_should_not_raise_when_check_is_false() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 1, "", "")
        result = _Fake()._run_cli(["release", "view", "v9"], check=False)
    assert result.returncode == 1


def test_should_not_expose_token_from_arguments_or_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "ghp_example_value_for_redaction"  # noqa: S105 - dummy test value
    monkeypatch.setenv("GH_TOKEN", token)
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 1, "", f"failed: {token}")
        with pytest.raises(PublishCliError) as exc:
            _Fake()._run_cli(["release", "create", token])
    assert token not in str(exc.value)
    assert "failed:" in str(exc.value)


def test_should_not_expose_token_in_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "ghp_example_auth_value"  # noqa: S105 - dummy test value
    monkeypatch.setenv("GH_TOKEN", token)
    pub = _Fake()
    completed = subprocess.CompletedProcess([], 1, "", f"invalid token: {token}")
    with (
        patch.object(pub, "_run_cli", return_value=completed),
        pytest.raises(PublishAuthError) as exc,
    ):
        pub._check_auth()
    assert token not in str(exc.value)
