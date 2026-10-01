from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from ezcompiler._types import PublisherPort
from ezcompiler.adapters._github_publisher import GitHubPublisher
from ezcompiler.shared.exceptions import PublishError


def _completed(code: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(
        args=[], returncode=code, stdout=stdout, stderr=stderr
    )


def test_should_conform_to_publisher_port() -> None:
    assert isinstance(GitHubPublisher(), PublisherPort)


def test_should_report_its_name() -> None:
    assert "GitHub" in GitHubPublisher().get_publisher_name()


# ------------------------------------------------
# exists()
# ------------------------------------------------


def test_should_report_existing_tag() -> None:
    pub = GitHubPublisher()
    with patch.object(pub, "_run_cli", return_value=_completed(0)) as run:
        assert pub.exists("v1.0.0") is True
    assert run.call_args.args[0] == ["release", "view", "v1.0.0"]


def test_should_report_absent_tag_on_release_not_found() -> None:
    pub = GitHubPublisher()
    absent = _completed(1, stderr="release not found")
    with patch.object(pub, "_run_cli", return_value=absent) as run:
        assert pub.exists("v9.9.9") is False
    # Sans check=False, chaque tag absent leverait PublishCliError.
    assert run.call_args.kwargs["check"] is False


def test_should_raise_when_existence_cannot_be_determined() -> None:
    """Review Focus #1 : un echec d'auth ou de reseau n'est PAS une absence.

    Le confondre ferait publier par-dessus une release existante.
    """
    pub = GitHubPublisher()
    denied = _completed(1, stderr="HTTP 401: Bad credentials")
    with (
        patch.object(pub, "_run_cli", return_value=denied),
        pytest.raises(PublishError, match="401"),
    ):
        pub.exists("v1.0.0")


def test_should_scope_exists_to_configured_repo() -> None:
    pub = GitHubPublisher({"repo": "neuraaak/ezcompiler"})
    with patch.object(pub, "_run_cli", return_value=_completed(0)) as run:
        pub.exists("v1.0.0")
    assert "--repo" in run.call_args.args[0]
    assert "neuraaak/ezcompiler" in run.call_args.args[0]


# ------------------------------------------------
# publish()
# ------------------------------------------------


def test_should_request_generated_notes_when_none_given(tmp_path: Path) -> None:
    asset = tmp_path / "app-1.0.0.zip"
    asset.write_bytes(b"x")
    pub = GitHubPublisher()
    url = "https://github.com/o/r/releases/tag/v1.0.0"
    with (
        patch.object(pub, "_check_auth"),
        patch.object(pub, "_run_cli", return_value=_completed(0, stdout=url)) as run,
    ):
        assert pub.publish([asset], tag="v1.0.0", title="App 1.0.0") == url
    args = run.call_args.args[0]
    assert "--generate-notes" in args
    assert "--notes" not in args


def test_should_pass_literal_notes_when_given(tmp_path: Path) -> None:
    asset = tmp_path / "app-1.0.0.zip"
    asset.write_bytes(b"x")
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth"),
        patch.object(pub, "_run_cli", return_value=_completed(0, stdout="u")) as run,
    ):
        pub.publish([asset], tag="v1.0.0", title="T", notes="Corrections diverses")
    args = run.call_args.args[0]
    assert "--notes" in args
    assert "Corrections diverses" in args
    assert "--generate-notes" not in args


def test_should_mark_prerelease_and_draft(tmp_path: Path) -> None:
    asset = tmp_path / "a.zip"
    asset.write_bytes(b"x")
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth"),
        patch.object(pub, "_run_cli", return_value=_completed(0, stdout="u")) as run,
    ):
        pub.publish([asset], tag="v1.0.0rc1", title="T", prerelease=True, draft=True)
    args = run.call_args.args[0]
    assert "--prerelease" in args
    assert "--draft" in args


def test_should_pass_asset_paths_verbatim_including_spaces(tmp_path: Path) -> None:
    """Review Focus #5 : un nom accentue ou espace traverse sans transformation."""
    asset = tmp_path / "Mon Appli-1.0.0.zip"
    asset.write_bytes(b"x")
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth"),
        patch.object(pub, "_run_cli", return_value=_completed(0, stdout="u")) as run,
    ):
        pub.publish([asset], tag="v1.0.0", title="T")
    assert str(asset) in run.call_args.args[0]


def test_should_reject_an_empty_asset_list() -> None:
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth"),
        pytest.raises(PublishError, match="[Aa]ucun"),
    ):
        pub.publish([], tag="v1.0.0", title="T")


def test_should_reject_a_missing_asset(tmp_path: Path) -> None:
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth"),
        pytest.raises(PublishError, match="introuvable"),
    ):
        pub.publish([tmp_path / "absent.zip"], tag="v1.0.0", title="T")


def test_should_check_auth_before_publishing(tmp_path: Path) -> None:
    asset = tmp_path / "a.zip"
    asset.write_bytes(b"x")
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth") as auth,
        patch.object(pub, "_run_cli", return_value=_completed(0, stdout="u")),
    ):
        pub.publish([asset], tag="v1.0.0", title="T")
    auth.assert_called_once()


def test_should_raise_when_repository_is_not_found() -> None:
    """Review Focus #1 : un depot inexistant n'est pas une release absente."""
    pub = GitHubPublisher({"repo": "o/absent"})
    missing_repo = _completed(1, stderr="GraphQL: Could not resolve to a Repository")
    with (
        patch.object(pub, "_run_cli", return_value=missing_repo),
        pytest.raises(PublishError),
    ):
        pub.exists("v1.0.0")


def test_should_raise_on_generic_http_404() -> None:
    pub = GitHubPublisher()
    not_found = _completed(1, stderr="HTTP 404: Not Found (https://api.github.com/x)")
    with (
        patch.object(pub, "_run_cli", return_value=not_found),
        pytest.raises(PublishError, match="404"),
    ):
        pub.exists("v1.0.0")


def test_should_not_copy_stderr_into_the_existence_error() -> None:
    """Coherent avec BasePublisher : stderr peut porter un secret."""
    pub = GitHubPublisher()
    leaky = _completed(1, stderr="HTTP 401: token ghp_secretvalue rejected")
    with (
        patch.object(pub, "_run_cli", return_value=leaky),
        pytest.raises(PublishError) as excinfo,
    ):
        pub.exists("v1.0.0")
    assert "ghp_secretvalue" not in str(excinfo.value)


def test_should_validate_assets_before_checking_auth(tmp_path: Path) -> None:
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth") as auth,
        pytest.raises(PublishError, match="introuvable"),
    ):
        pub.publish([tmp_path / "absent.zip"], tag="v1.0.0", title="T")
    auth.assert_not_called()


@pytest.mark.parametrize("tag", ["", "--draft", "-v1"])
def test_should_reject_a_tag_gh_would_read_as_an_option(
    tmp_path: Path, tag: str
) -> None:
    asset = tmp_path / "a.zip"
    asset.write_bytes(b"x")
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_check_auth"),
        patch.object(pub, "_run_cli") as run,
        pytest.raises(PublishError, match="Tag"),
    ):
        pub.publish([asset], tag=tag, title="T")
    run.assert_not_called()


def test_exists_should_reject_a_tag_gh_would_read_as_an_option() -> None:
    pub = GitHubPublisher()
    with (
        patch.object(pub, "_run_cli") as run,
        pytest.raises(PublishError, match="Tag"),
    ):
        pub.exists("-x")
    run.assert_not_called()
