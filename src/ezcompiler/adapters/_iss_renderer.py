# ///////////////////////////////////////////////////////////////
# ISS_RENDERER - Jinja2 rendering of Inno Setup scripts
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
ISS renderer - Renders an Inno Setup .iss script from an InstallerConfig.

Shared by the build pipeline (ephemeral mode) and the ``generate iss``
command (standalone mode). Knows nothing about ISCC.

Jinja2 delimiters are customized because the defaults collide head-on with
Inno syntax: ``{#`` opens a Jinja comment, which would swallow the rest of a
file containing ``{#MyAppName}``, and ``{{`` opens an expression, which the
AppId line ``{{{#MyAppName}...}`` would trigger.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import re
import uuid
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_TEMPLATE_DIR = Path(__file__).parent.parent / "assets" / "templates" / "installer"
_TEMPLATE_NAME = "setup.iss.jinja"

# Fixed namespace so a project's AppId is stable across builds and machines.
_APP_ID_NAMESPACE = uuid.UUID("6f1d5a4e-8c2b-4f7a-9e3d-1b5c7a9e0f42")

_FORBIDDEN_IN_ISS = ('"', "\n", "\r", "\t")
_VERSION_QUAD_RE = re.compile(r"\d+(?:\.\d+)*")

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def escape_iss(value: str) -> str:
    """Escape a value for safe interpolation into an Inno Setup script.

    Doubles ``{`` and ``}`` so Inno treats them as literal braces instead of
    opening/closing a constant (e.g. ``{app}``). Rejects characters that
    would truncate or split the generated directive.
    """
    for character in _FORBIDDEN_IN_ISS:
        if character in value:
            raise ValueError(f"invalid character {character!r} in {value!r}")
    return value.replace("{", "{{").replace("}", "}}")


def resolve_app_id(app_id: str | None, company_name: str, project_name: str) -> str:
    """Return the explicit ``app_id``, or derive a stable one deterministically.

    The derived id is a UUID5 keyed by company and project name, so it stays
    identical across builds and machines instead of varying per version.
    """
    if app_id:
        return app_id
    derived = uuid.uuid5(_APP_ID_NAMESPACE, f"{company_name}\x00{project_name}")
    return "{" + str(derived).upper() + "}"


def sanitize_version_info(version: str) -> str:
    """Coerce ``version`` into the numeric quadruplet Inno's VersionInfoVersion needs.

    Locates the leading run of dot-separated digits (ignoring a leading
    ``v`` and any trailing pre-release/build suffix), drops leading zeros
    via ``int()``, and pads or truncates to exactly four components.
    """
    match = _VERSION_QUAD_RE.search(version)
    if not match:
        raise ValueError(f"cannot derive a version quadruplet from {version!r}")
    components = [str(int(number)) for number in match.group().split(".")[:4]]
    components += ["0"] * (4 - len(components))
    return ".".join(components)


def build_environment() -> Environment:
    """Build the Jinja2 environment used to render Inno Setup scripts.

    Uses custom delimiters (``<% %>`` / ``<< >>`` / ``<# #>``) because the
    defaults collide with Inno Setup's own ``{#`` and ``{{`` syntax.
    """
    env = Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        undefined=StrictUndefined,
        autoescape=False,  # noqa: S701 - .iss is not HTML; escape_iss handles safety
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
    )
    env.filters["iss"] = escape_iss
    return env
