# ///////////////////////////////////////////////////////////////
# TEST_BUILD_TEMPLATE - Generated build.py and config templates
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Verify that generated build scripts and config files are actually usable."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import ast
import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from ezcompiler.assets.templates._template_loader import TemplateLoader
from ezcompiler.interfaces.python_api import EzCompiler
from ezcompiler.shared._compiler_config import CompilerConfig

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def loader() -> TemplateLoader:
    return TemplateLoader()


def _config(tmp_path: Path, **extra: Any) -> dict[str, Any]:
    main_file = tmp_path / "main.py"
    main_file.write_text("print('hi')", encoding="utf-8")
    return {"project_name": "MyApp", "main_file": str(main_file), **extra}


# ///////////////////////////////////////////////////////////////
# BUILD SCRIPT
# ///////////////////////////////////////////////////////////////


def test_generated_build_script_is_valid_python(
    loader: TemplateLoader, tmp_path: Path
) -> None:
    """Every placeholder must be substituted. An unsubstituted one turns into
    a comment, so `__ZIP_NEEDED__ = #ZIP_NEEDED#` loses its value and the
    whole script stops parsing."""
    rendered = loader.process_setup_template("py", _config(tmp_path))

    ast.parse(rendered)
    assert not re.findall(r"#[A-Z_]+#", rendered)


def test_generated_build_script_initializes_ezpl(
    loader: TemplateLoader, tmp_path: Path
) -> None:
    """EzCompiler is passive until the host initializes Ezpl; without it
    run_pipeline() has no progress display to drive."""
    rendered = loader.process_setup_template("py", _config(tmp_path))

    assert "from ezplog import Ezpl" in rendered
    assert "Ezpl()" in rendered


def test_generated_build_script_only_calls_real_api(
    loader: TemplateLoader, tmp_path: Path
) -> None:
    """Guards against the template drifting from EzCompiler, which is how it
    came to call the long-removed compiler._ezpl.add_separator()."""
    rendered = loader.process_setup_template("py", _config(tmp_path))
    tree = ast.parse(rendered)

    attributes = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "compiler"
    }
    assert attributes, "the script no longer touches the compiler object"
    for attribute in attributes:
        assert hasattr(EzCompiler, attribute), f"EzCompiler has no {attribute}"


def test_generated_build_script_passes_pipeline_values(
    loader: TemplateLoader, tmp_path: Path
) -> None:
    config = _config(
        tmp_path,
        compilation={"console": False, "compiler": "Nuitka"},
        upload={"repo_endpoint": "D:/repo"},
    )
    rendered = loader.process_setup_template("py", config)

    assert "console=False," in rendered
    assert 'compiler="Nuitka",' in rendered


def test_generated_build_script_does_not_upload(
    loader: TemplateLoader, tmp_path: Path
) -> None:
    """Publication is a deliberate CLI step: the build script never uploads,
    even when an endpoint is configured."""
    config = _config(tmp_path, upload={"repo_endpoint": "D:/updates"})
    rendered = loader.process_setup_template("py", config)

    assert "compiler.upload(" not in rendered
    assert "__REPO_NEEDED__" not in rendered
    assert "REPO_PATH" not in rendered


def test_generated_build_script_points_to_the_publish_commands(
    loader: TemplateLoader, tmp_path: Path
) -> None:
    config = _config(tmp_path, upload={"repo_endpoint": "D:/updates"})
    rendered = loader.process_setup_template("py", config)

    assert "ezcompiler publish update" in rendered
    assert "ezcompiler publish release" in rendered


@pytest.mark.parametrize("value", [r"C:\Users\dev\main.py", 'na"me', "accentué.py"])
def test_generated_build_script_survives_hostile_string_values(
    loader: TemplateLoader, tmp_path: Path, value: str
) -> None:
    """Values used to be interpolated raw, so a Windows path made the
    generated script unparseable through its backslash escapes."""
    config = _config(tmp_path)
    config["main_file"] = value

    rendered = loader.process_setup_template("py", config)

    tree = ast.parse(rendered)
    assigned = {
        node.targets[0].id: node.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }
    assert assigned["main_file"] == value


# ///////////////////////////////////////////////////////////////
# CONFIG FILES
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize("fmt", ["yaml", "json"])
def test_generated_config_carries_the_installer_section(
    loader: TemplateLoader, tmp_path: Path, fmt: str
) -> None:
    config = _config(tmp_path, installer={"enabled": True, "per_user": True})

    rendered = loader.process_config_template(fmt, config)
    data = yaml.safe_load(rendered) if fmt == "yaml" else json.loads(rendered)

    assert data["installer"]["enabled"] is True
    assert data["installer"]["per_user"] is True


@pytest.mark.parametrize("fmt", ["yaml", "json"])
def test_generated_config_round_trips_through_compiler_config(
    loader: TemplateLoader, tmp_path: Path, fmt: str
) -> None:
    """The file a user is handed must load back without editing."""
    config = _config(
        tmp_path, installer={"enabled": True, "output_dir": "dist/installer"}
    )

    rendered = loader.process_config_template(fmt, config)
    data = yaml.safe_load(rendered) if fmt == "yaml" else json.loads(rendered)
    loaded = CompilerConfig.from_dict(dict(data))

    assert loaded.installer.enabled is True
    assert loaded.installer.output_dir == Path("dist/installer")


@pytest.mark.parametrize("fmt", ["yaml", "json"])
def test_generated_config_survives_a_windows_path(
    loader: TemplateLoader, tmp_path: Path, fmt: str
) -> None:
    config = _config(tmp_path)
    config["main_file"] = r"C:\Users\dev\main.py"

    rendered = loader.process_config_template(fmt, config)
    data = yaml.safe_load(rendered) if fmt == "yaml" else json.loads(rendered)

    assert data["main_file"] == r"C:\Users\dev\main.py"


@pytest.mark.parametrize("fmt", ["yaml", "json"])
def test_unset_installer_paths_are_null_not_empty(
    loader: TemplateLoader, tmp_path: Path, fmt: str
) -> None:
    """An empty string would coerce to Path('.'), silently writing the
    installer next to the config file."""
    rendered = loader.process_config_template(fmt, _config(tmp_path))
    data = yaml.safe_load(rendered) if fmt == "yaml" else json.loads(rendered)

    assert data["installer"]["output_dir"] is None
    assert data["installer"]["iss_path"] is None
