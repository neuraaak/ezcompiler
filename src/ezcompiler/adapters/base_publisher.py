# ///////////////////////////////////////////////////////////////
# BASE_PUBLISHER - Abstract base release publisher
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Shared CLI behavior for release publishers."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import shutil

# CLI execution is isolated in _run_cli and always disables the shell.
import subprocess  # noqa: S404  # nosec B404
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..shared.exceptions import PublishAuthError, PublishCliError

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Ceiling for each external CLI call. A `gh release create` uploading an
# installer behind a corporate proxy that stalls would otherwise hang the
# process indefinitely, with no output at all (capture_output=True).
CLI_TIMEOUT_SECONDS = 300

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class BasePublisher(ABC):
    """Abstract publisher with one mockable seam for external CLI calls."""

    _cli_name: str = ""
    _install_hint: str = ""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    @property
    def config(self) -> dict[str, Any]:
        """Publisher configuration."""
        return self._config

    def preflight(self) -> None:
        """Raise unless the CLI is installed and authenticated.

        Lets callers run every check before showing a recap, so that an
        unauthenticated CLI is reported as such rather than as an opaque
        failure of a later call.
        """
        self._check_auth()

    @abstractmethod
    def exists(self, tag: str) -> bool:
        """Whether a release exists for ``tag``."""

    @abstractmethod
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
        """Create a release with assets and return its URL."""

    @abstractmethod
    def get_publisher_name(self) -> str:
        """Human-readable publisher name."""

    def _resolve_cli(self) -> str:
        """Return the CLI binary path or raise with an installation hint."""
        exe = shutil.which(self._cli_name)
        if exe is None:
            raise PublishCliError(
                f"'{self._cli_name}' not found in PATH. "
                f"Installer depuis {self._install_hint}, "
                f"puis lancer `{self._cli_name} auth login`."
            )
        return exe

    def _check_auth(self) -> None:
        """Raise when the external CLI reports no valid credentials."""
        result = self._run_cli(["auth", "status"], check=False)
        if result.returncode != 0:
            raise PublishAuthError(
                f"'{self._cli_name}' is not authenticated. "
                f"Run `{self._cli_name} auth login`, or export the token "
                "into the environment."
            )

    def _run_cli(
        self,
        args: list[str],
        *,
        check: bool = True,
        timeout: float = CLI_TIMEOUT_SECONDS,
    ) -> subprocess.CompletedProcess[str]:
        """Run a CLI command without a shell and capture its output.

        CLI stderr is retained in the returned result for callers using
        ``check=False``. It is never copied into an exception, because the
        external CLI can print credentials from outside this process.

        Args:
            args: Argument vector appended to the resolved CLI binary.
            check: Raise ``PublishCliError`` on a non-zero return code.
            timeout: Hard ceiling in seconds; expiry is reported as a
                publication error rather than hanging the process.

        Raises:
            PublishCliError: If the CLI cannot be executed, exceeds
                ``timeout``, or (with ``check=True``) returns non-zero.
        """
        exe = self._resolve_cli()
        # Argument vector is passed directly; no shell interprets asset names.
        try:
            result = subprocess.run(  # noqa: S603  # nosec B603
                [exe, *args],
                capture_output=True,
                text=True,
                check=False,
                shell=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise PublishCliError(
                f"`{self._cli_name}` did not answer within {timeout:g} s and was "
                "interrupted. Check the network or the proxy, then review "
                "the state of the release before retrying."
            ) from None
        except OSError:
            raise PublishCliError(
                f"'{self._cli_name}' could not be executed."
            ) from None
        if check and result.returncode != 0:
            raise PublishCliError(
                f"`{self._cli_name}` failed (code {result.returncode})."
            )
        return result
