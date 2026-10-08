# ///////////////////////////////////////////////////////////////
# GITHUB_PUBLISHER - GitHub Releases publisher via the gh CLI
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
GitHub publisher - Creates GitHub Releases through the `gh` CLI.

Authentication is inherited from the environment (``GH_TOKEN`` or a prior
``gh auth login``): no credential ever transits through the configuration
or the command line.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path

# Local imports
from ..shared.exceptions import PublishError
from .base_publisher import BasePublisher

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Fragments through which `gh release view` reports an absence, by
# opposition a un echec d'authentification, de reseau ou de permission.
# Telling the two apart is critical: treating a 401 as an absence
# would publish over an existing release.
# Only "release not found" is kept: an "HTTP 404" or an unreachable repo
# does not attest that the release is absent.
_RELEASE_NOT_FOUND = "release not found"

# The HTTP status is the only stderr fragment copied into the error: stderr
# peut porter un secret (voir BasePublisher._run_cli).
_HTTP_STATUS = re.compile(r"\bHTTP (\d{3})\b")

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class GitHubPublisher(BasePublisher):
    """
    Publishes GitHub Releases through the `gh` CLI.

    Args:
        config: Optional dict. Key ``repo`` scopes every call to a given
            ``owner/repo``; when absent, `gh` infers the repository from the
            current directory's git remote.

    Example:
        >>> publisher = GitHubPublisher({"repo": "neuraaak/ezcompiler"})
        >>> publisher.get_publisher_name()
        'GitHub Releases (gh)'
    """

    _cli_name = "gh"
    _install_hint = "https://cli.github.com/"

    # ////////////////////////////////////////////////
    # PUBLIC METHODS
    # ////////////////////////////////////////////////

    def exists(self, tag: str) -> bool:
        """
        Whether a GitHub Release already exists for ``tag``.

        Args:
            tag: Release tag to look up.

        Returns:
            bool: True when the release exists.

        Raises:
            PublishError: If existence cannot be determined — an auth,
                network or permission failure is never reported as absence.
        """
        self._validate_tag(tag)
        result = self._run_cli(
            ["release", "view", tag, *self._repo_args()], check=False
        )
        if result.returncode == 0:
            return True

        stderr = result.stderr or ""
        if _RELEASE_NOT_FOUND in stderr.lower():
            return False

        http = _HTTP_STATUS.search(stderr)
        status = f", HTTP {http.group(1)}" if http else ""
        raise PublishError(
            f"Cannot determine whether release '{tag}' exists "
            f"(code {result.returncode}{status}). "
            "Publication aborted so an existing release is not overwritten."
        )

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
        """
        Create a GitHub Release and attach ``assets``.

        Args:
            assets: Files to attach. Must be a non-empty list of existing files.
            tag: Release tag.
            title: Release title.
            notes: Release body. ``None`` requests `--generate-notes`.
            prerelease: Mark as pre-release.
            draft: Create unpublished.

        Returns:
            str: URL of the created release, as printed by `gh`.

        Raises:
            PublishError: If validation, authentication or `gh` fails.
        """
        # Local checks first: they are cheap and must not hide behind a
        # missing or unauthenticated gh.
        self._validate_tag(tag)
        self._validate_assets(assets)
        self._check_auth()

        args = ["release", "create", tag, *self._repo_args(), "--title", title]
        if notes is None:
            args.append("--generate-notes")
        else:
            args += ["--notes", notes]
        if prerelease:
            args.append("--prerelease")
        if draft:
            args.append("--draft")
        # `--` closes the option list: an asset named `-x.zip` can no longer
        # be read as a flag by gh (symmetric with _validate_tag).
        args += ["--", *(str(asset) for asset in assets)]

        result = self._run_cli(args)
        return result.stdout.strip()

    def get_publisher_name(self) -> str:
        """
        Get the name of this publisher.

        Returns:
            str: Human-readable publisher name.
        """
        return "GitHub Releases (gh)"

    # ////////////////////////////////////////////////
    # PRIVATE METHODS
    # ////////////////////////////////////////////////

    def _repo_args(self) -> list[str]:
        """Return ``--repo owner/repo`` when configured, else nothing."""
        repo = self._config.get("repo")
        return ["--repo", str(repo)] if repo else []

    @staticmethod
    def _validate_tag(tag: str) -> None:
        """
        Reject a tag that `gh` would parse as an option.

        Raises:
            PublishError: If the tag is empty or starts with ``-``.
        """
        if not tag or tag.startswith("-"):
            raise PublishError(f"Tag de release invalide : '{tag}'.")

    @staticmethod
    def _validate_assets(assets: list[Path]) -> None:
        """
        Ensure every asset exists and is not option-like.

        Raises:
            PublishError: If the list is empty, a path starts with ``-`` (gh
                would read it as a flag), or a file is missing.
        """
        if not assets:
            raise PublishError("No asset to publish. Run `ezcompiler compile` first.")
        option_like = [str(a) for a in assets if str(a).startswith("-")]
        if option_like:
            raise PublishError(
                f"Invalid asset path: {', '.join(option_like)} — gh would "
                "read it as an option. Use an absolute path."
            )
        missing = [str(a) for a in assets if not a.is_file()]
        if missing:
            raise PublishError(
                f"Asset not found: {', '.join(missing)}. "
                "Run `ezcompiler compile` first."
            )
