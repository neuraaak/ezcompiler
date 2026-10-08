from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from ezcompiler.adapters.base_publisher import CLI_TIMEOUT_SECONDS, BasePublisher
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
        patch.object(pub, "_run_cli", return_value=completed) as run_cli,
        pytest.raises(PublishAuthError) as exc,
    ):
        pub._check_auth()
    assert "faketool auth login" in str(exc.value)
    run_cli.assert_called_once_with(["auth", "status"], check=False)


def test_should_pass_when_authenticated() -> None:
    pub = _Fake()
    completed = subprocess.CompletedProcess(
        args=["faketool", "auth", "status"], returncode=0, stdout="ok", stderr=""
    )
    with patch.object(pub, "_run_cli", return_value=completed) as run_cli:
        pub._check_auth()
    run_cli.assert_called_once_with(["auth", "status"], check=False)


def test_should_never_invoke_a_shell() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 0, "", "")
        _Fake()._run_cli(["release", "view", "a b;&|$()`'\".zip"])
    assert run.call_args.kwargs.get("shell", False) is False
    assert run.call_args.kwargs["capture_output"] is True
    assert run.call_args.args[0] == [
        "C:\\bin\\faketool.exe",
        "release",
        "view",
        "a b;&|$()`'\".zip",
    ]


def test_should_report_exit_code_without_exposing_stderr() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 2, "", "boom details")
        with pytest.raises(PublishCliError) as exc:
            _Fake()._run_cli(["release", "create"], check=True)
    assert "boom details" not in str(exc.value)
    assert "faketool" in str(exc.value)
    assert "2" in str(exc.value)


def test_should_not_raise_when_check_is_false() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 1, "", "diagnostic detail")
        result = _Fake()._run_cli(["release", "view", "v9"], check=False)
    assert result.returncode == 1
    assert result.stderr == "diagnostic detail"


def test_should_not_expose_token_from_arguments_or_stderr() -> None:
    token = "ghp_example_value_for_redaction"  # noqa: S105 - dummy test value
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 1, "", f"failed: {token}")
        with pytest.raises(PublishCliError) as exc:
            _Fake()._run_cli(["release", "create", token])
    assert token not in str(exc.value)
    assert "failed:" not in str(exc.value)


def test_should_not_expose_token_in_auth_error() -> None:
    pub = _Fake()
    completed = subprocess.CompletedProcess([], 1, "", "credential: hunter2")
    with (
        patch.object(pub, "_run_cli", return_value=completed),
        pytest.raises(PublishAuthError) as exc,
    ):
        pub._check_auth()
    assert "hunter2" not in str(exc.value)
    assert "credential:" not in str(exc.value)


@pytest.mark.parametrize(
    "stderr, credential",
    [
        ("authentication failed: gho_storedcredential123", "gho_storedcredential123"),
        ("token: shortsecret", "shortsecret"),
        ("credential: hunter2", "hunter2"),
        ("access_token: shortsecret", "shortsecret"),
        ("token is shortsecret", "shortsecret"),
        ("request failed for abcDEF0123456789xyzABC", "abcDEF0123456789xyzABC"),
    ],
)
def test_should_never_expose_arbitrary_cli_stderr(stderr: str, credential: str) -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run") as run,
        pytest.raises(PublishCliError) as exc,
    ):
        run.return_value = subprocess.CompletedProcess([], 1, "", stderr)
        _Fake()._run_cli(["release", "create"])
    assert stderr not in str(exc.value)
    assert credential not in str(exc.value)
    assert "faketool" in str(exc.value)


def test_should_wrap_os_error_without_exposing_exception_text() -> None:
    with (
        patch("shutil.which", return_value="C:\\bin\\faketool.exe"),
        patch("subprocess.run", side_effect=OSError("sensitive details")),
        pytest.raises(PublishCliError) as exc,
    ):
        _Fake()._run_cli(["release", "create"])
    assert "sensitive details" not in str(exc.value)
    assert "faketool" in str(exc.value)


def test_preflight_checks_auth() -> None:
    pub = _Fake()
    with patch.object(pub, "_check_auth") as auth:
        pub.preflight()
    auth.assert_called_once()


def test_should_pass_a_bounded_timeout_when_running_the_cli() -> None:
    with (
        patch("shutil.which", return_value="C:\bin\faketool.exe"),
        patch("subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess([], 0, "", "")
        _Fake()._run_cli(["release", "create"])
    assert run.call_args.kwargs["timeout"] == CLI_TIMEOUT_SECONDS
    assert CLI_TIMEOUT_SECONDS > 0


def test_should_raise_publish_cli_error_when_the_cli_times_out() -> None:
    expired = subprocess.TimeoutExpired(
        cmd=["faketool", "release", "create"], timeout=1, output="", stderr="token=abc"
    )
    with (
        patch("shutil.which", return_value="C:\bin\faketool.exe"),
        patch("subprocess.run", side_effect=expired),
        pytest.raises(PublishCliError) as exc,
    ):
        _Fake()._run_cli(["release", "create"], timeout=1)
    assert "token=abc" not in str(exc.value)
    assert "faketool" in str(exc.value)
