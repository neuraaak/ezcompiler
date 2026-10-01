# ///////////////////////////////////////////////////////////////
# BASE_PUBLISHER - Abstract base release publisher
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Shared CLI behavior for release publishers."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import os
import re
import shutil

# CLI execution is isolated in _run_cli and always disables the shell.
import subprocess  # noqa: S404  # nosec B404
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..shared.exceptions import PublishAuthError, PublishCliError

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
                f"'{self._cli_name}' introuvable dans le PATH. "
                f"Installer depuis {self._install_hint}, "
                f"puis lancer `{self._cli_name} auth login`."
            )
        return exe

    def _check_auth(self) -> None:
        """Raise when the external CLI reports no valid credentials."""
        result = self._run_cli(["auth", "status"], check=False)
        if result.returncode != 0:
            detail = self._redact_secrets(result.stderr.strip())
            raise PublishAuthError(
                f"'{self._cli_name}' n'est pas authentifié. "
                f"Lancer `{self._cli_name} auth login`, ou exporter le token "
                f"dans l'environnement. Détail : {detail}"
            )

    def _run_cli(
        self, args: list[str], *, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run a CLI command without a shell and capture its output."""
        exe = self._resolve_cli()
        # Argument vector is passed directly; no shell interprets asset names.
        try:
            result = subprocess.run(  # noqa: S603  # nosec B603
                [exe, *args],
                capture_output=True,
                text=True,
                check=False,
                shell=False,
            )
        except OSError:
            raise PublishCliError(
                f"'{self._cli_name}' n'a pas pu être exécuté."
            ) from None
        if check and result.returncode != 0:
            detail = self._redact_secrets(result.stderr.strip())
            raise PublishCliError(
                f"`{self._cli_name}` a échoué (code {result.returncode}) : {detail}"
            )
        return result

    @staticmethod
    def _redact_secrets(message: str) -> str:
        """Mask likely credentials in CLI diagnostics before displaying stderr.

        The CLI can echo credentials stored outside the environment. Mask known
        token prefixes, labelled values, and long opaque strings in addition to
        environment credentials; never include raw command arguments in errors.
        """
        secret_values = {
            value
            for name, value in os.environ.items()
            if value
            and any(part in name.upper() for part in ("TOKEN", "SECRET", "PASSWORD"))
        }
        for value in sorted(secret_values, key=len, reverse=True):
            message = message.replace(value, "[REDACTED]")
        message = re.sub(
            r"(?i)\b(token|secret|password|authorization|api[-_ ]?key)\s*([=:])\s*\S+",
            r"\1\2 [REDACTED]",
            message,
        )
        message = re.sub(r"(?i)\bbearer\s+\S+", "Bearer [REDACTED]", message)
        message = re.sub(
            r"(?i)\b(?:github_pat_|gh[pousr]_|glpat-)[A-Za-z0-9_-]+",
            "[REDACTED]",
            message,
        )
        message = re.sub(r"\b[A-Za-z0-9_+/=-]{20,}\b", "[REDACTED]", message)
        return message
