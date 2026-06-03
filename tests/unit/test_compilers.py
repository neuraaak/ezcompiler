# ///////////////////////////////////////////////////////////////
# TEST COMPILERS - Unit tests for compiler modules
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Unit tests for compiler modules.

Tests the basic functionality of compiler implementations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ezcompiler.adapters import BaseCompiler
from ezcompiler.adapters._cx_freeze_compiler import CxFreezeCompiler
from ezcompiler.adapters._nuitka_compiler import NuitkaCompiler
from ezcompiler.adapters._pyinstaller_compiler import PyInstallerCompiler
from ezcompiler.shared import CompilerConfig

# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER IMPORTS
# ///////////////////////////////////////////////////////////////


class TestCompilerImports:
    """Test compiler classes can be imported."""

    def test_should_be_importable_when_base_compiler_is_loaded(self) -> None:
        """Test that BaseCompiler can be imported."""
        assert BaseCompiler is not None

    def test_should_be_importable_when_cx_freeze_compiler_is_loaded(self) -> None:
        """Test that CxFreezeCompiler can be imported."""
        assert CxFreezeCompiler is not None

    def test_should_be_importable_when_pyinstaller_compiler_is_loaded(self) -> None:
        """Test that PyInstallerCompiler can be imported."""
        assert PyInstallerCompiler is not None

    def test_should_be_importable_when_nuitka_compiler_is_loaded(self) -> None:
        """Test that NuitkaCompiler can be imported."""
        assert NuitkaCompiler is not None


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER INSTANTIATION
# ///////////////////////////////////////////////////////////////


class TestCompilerInstantiation:
    """Test compiler classes can be instantiated."""

    def test_should_instantiate_when_cx_freeze_compiler_is_given_valid_config(
        self, temp_dir
    ) -> None:
        """Test that CxFreezeCompiler can be instantiated."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        compiler = CxFreezeCompiler(config)
        assert compiler is not None
        assert isinstance(compiler, CxFreezeCompiler)

    def test_should_instantiate_when_pyinstaller_compiler_is_given_valid_config(
        self, temp_dir
    ) -> None:
        """Test that PyInstallerCompiler can be instantiated."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        compiler = PyInstallerCompiler(config)
        assert compiler is not None
        assert isinstance(compiler, PyInstallerCompiler)

    def test_should_instantiate_when_nuitka_compiler_is_given_valid_config(
        self, temp_dir
    ) -> None:
        """Test that NuitkaCompiler can be instantiated."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        compiler = NuitkaCompiler(config)
        assert compiler is not None
        assert isinstance(compiler, NuitkaCompiler)

    def test_should_store_config_when_cx_freeze_compiler_is_instantiated(
        self, temp_dir
    ) -> None:
        """Test that CxFreezeCompiler stores config."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        compiler = CxFreezeCompiler(config)
        assert hasattr(compiler, "config")
        assert compiler.config == config

    def test_should_be_base_compiler_instance_when_any_compiler_is_created(
        self, temp_dir
    ) -> None:
        """Test that all compilers are instances of BaseCompiler."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        assert isinstance(CxFreezeCompiler(config), BaseCompiler)
        assert isinstance(PyInstallerCompiler(config), BaseCompiler)
        assert isinstance(NuitkaCompiler(config), BaseCompiler)


# ///////////////////////////////////////////////////////////////
# TESTS - COMPILER NAMES
# ///////////////////////////////////////////////////////////////


class TestCompilerNames:
    """Test that compilers return correct names."""

    def test_should_return_cx_freeze_name_when_get_compiler_name_is_called(
        self, temp_dir
    ) -> None:
        """Test that CxFreezeCompiler returns correct name."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        name = CxFreezeCompiler(config).get_compiler_name()
        assert isinstance(name, str)
        assert "freeze" in name.lower() or "cx" in name.lower()

    def test_should_return_pyinstaller_name_when_get_compiler_name_is_called(
        self, temp_dir
    ) -> None:
        """Test that PyInstallerCompiler returns correct name."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        name = PyInstallerCompiler(config).get_compiler_name()
        assert isinstance(name, str)
        assert "pyinstaller" in name.lower()

    def test_should_return_nuitka_name_when_get_compiler_name_is_called(
        self, temp_dir
    ) -> None:
        """Test that NuitkaCompiler returns correct name."""
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")

        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
        )
        name = NuitkaCompiler(config).get_compiler_name()
        assert isinstance(name, str)
        assert "nuitka" in name.lower()


# ///////////////////////////////////////////////////////////////
# TESTS - PYINSTALLER COMPILER OPTIONS
# ///////////////////////////////////////////////////////////////


class TestPyInstallerCompilerOptions:
    """Test compiler_options handling for PyInstallerCompiler."""

    def _make_compiler(self, temp_dir, compiler_options: dict) -> PyInstallerCompiler:
        main_file = temp_dir / "main.py"
        main_file.write_text("# test")
        config = CompilerConfig(
            version="1.0.0",
            project_name="TestProject",
            main_file=str(main_file),
            include_files={"files": [], "folders": []},
            output_folder=str(temp_dir / "dist"),
            compiler_options=compiler_options,
        )
        return PyInstallerCompiler(config)

    def test_should_expand_list_option_to_multiple_flags_when_compiler_options_contains_list(
        self, temp_dir, monkeypatch
    ) -> None:
        """Each list item must produce a separate --key=item flag."""
        compiler = self._make_compiler(
            temp_dir,
            {"collect-all": ["webview", "fastexcel", "polars"]},
        )

        captured: list[list[str]] = []
        import subprocess

        monkeypatch.setattr(
            subprocess,
            "run",
            lambda cmd, **_kwargs: (
                captured.append(cmd)
                or type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            ),
        )

        compiler.compile()

        assert captured, "subprocess.run was not called"
        cmd = captured[0]
        assert "--collect-all=webview" in cmd
        assert "--collect-all=fastexcel" in cmd
        assert "--collect-all=polars" in cmd

    def test_should_add_single_flag_when_compiler_options_value_is_bool_true(
        self, temp_dir, monkeypatch
    ) -> None:
        """Bool True must produce a bare --key flag (no value)."""
        compiler = self._make_compiler(temp_dir, {"strip": True})

        captured: list[list[str]] = []
        import subprocess

        monkeypatch.setattr(
            subprocess,
            "run",
            lambda cmd, **_kwargs: (
                captured.append(cmd)
                or type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            ),
        )

        compiler.compile()

        cmd = captured[0]
        assert "--strip" in cmd
        assert not any(a.startswith("--strip=") for a in cmd)

    def test_should_omit_flag_when_compiler_options_value_is_bool_false(
        self, temp_dir, monkeypatch
    ) -> None:
        """Bool False must not add any flag to the command."""
        compiler = self._make_compiler(temp_dir, {"strip": False})

        captured: list[list[str]] = []
        import subprocess

        monkeypatch.setattr(
            subprocess,
            "run",
            lambda cmd, **_kwargs: (
                captured.append(cmd)
                or type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            ),
        )

        compiler.compile()

        cmd = captured[0]
        assert "--strip" not in cmd

    def test_should_add_key_value_flag_when_compiler_options_value_is_string(
        self, temp_dir, monkeypatch
    ) -> None:
        """String value must produce a --key=value flag."""
        compiler = self._make_compiler(temp_dir, {"log-level": "WARN"})

        captured: list[list[str]] = []
        import subprocess

        monkeypatch.setattr(
            subprocess,
            "run",
            lambda cmd, **_kwargs: (
                captured.append(cmd)
                or type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            ),
        )

        compiler.compile()

        cmd = captured[0]
        assert "--log-level=WARN" in cmd
