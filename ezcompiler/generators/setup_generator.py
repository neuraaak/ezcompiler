# ///////////////////////////////////////////////////////////////
# SETUP_GENERATOR - Setup.py file generator
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Setup generator - Setup.py file generator for EzCompiler.

This module provides functionality for generating setup.py files using
templates and configuration values. Integrates with the template
management system for flexible output generation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Local imports
from ..core.exceptions import TemplateError
from ..templates import TemplateManager

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class SetupGenerator:
    """
    Generator for setup.py files.

    Handles the generation of setup.py files using templates and the
    TemplateManager system. Supports automatic directory creation and
    flexible output paths.

    Attributes:
        template_manager: TemplateManager instance for template processing

    Example:
        >>> generator = SetupGenerator()
        >>> config = {"version": "1.0.0", "project_name": "MyApp"}
        >>> setup_path = generator.generate_from_config(config)
    """

    # ////////////////////////////////////////////////
    # INITIALIZATION
    # ////////////////////////////////////////////////

    def __init__(self) -> None:
        """
        Initialize the setup generator.

        Note:
            Automatically creates a TemplateManager instance for
            template processing operations.
        """
        self.template_manager = TemplateManager()

    # ////////////////////////////////////////////////
    # GENERATION METHODS
    # ////////////////////////////////////////////////

    def generate(
        self, config: dict[str, Any], output_path: Path, format_type: str = "py"
    ) -> None:
        """
        Generate a setup.py file from template.

        Args:
            config: Project configuration dictionary
            output_path: Path where to save the setup.py file
            format_type: Template format type (py, etc.)

        Raises:
            TemplateError: If setup generation fails

        Example:
            >>> config = {
            ...     "version": "1.0.0",
            ...     "project_name": "MyApp",
            ...     "packages": ["myapp"]
            ... }
            >>> generator.generate(config, Path("setup.py"))
        """
        try:
            # Generate setup content using template
            setup_content = self.template_manager.process_setup_template(
                format_type=format_type, config=config
            )

            # Write the setup file
            output_path.write_text(setup_content, encoding="utf-8")

        except Exception as e:
            raise TemplateError(f"Failed to generate setup file: {str(e)}") from e

    def generate_from_config(
        self, config: dict[str, Any], output_dir: Path | None = None
    ) -> Path:
        """
        Generate setup.py file using configuration.

        Automatically creates output directory if specified and doesn't exist.
        Returns the path to the generated setup.py file.

        Args:
            config: Project configuration dictionary
            output_dir: Directory where to save setup.py (defaults to current directory)

        Returns:
            Path: Path to the generated setup.py file

        Raises:
            TemplateError: If setup generation fails

        Note:
            If output_dir is None, uses current working directory.
            Creates output_dir if it doesn't exist.

        Example:
            >>> config = {"version": "1.0.0", "project_name": "MyApp"}
            >>> setup_path = generator.generate_from_config(config, Path("build"))
            >>> print(setup_path)
            build/setup.py
        """
        try:
            # Determine output directory
            if output_dir is None:
                output_dir = Path.cwd()
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

            # Generate setup.py in the output directory
            output_path = output_dir / "setup.py"
            self.generate(config, output_path)

            return output_path

        except Exception as e:
            raise TemplateError(
                f"Failed to generate setup file from config: {str(e)}"
            ) from e
