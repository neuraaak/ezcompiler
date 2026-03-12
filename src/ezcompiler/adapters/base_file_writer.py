# ///////////////////////////////////////////////////////////////
# BASE_FILE_WRITER - Abstract file writer port
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Abstract file writer port for template output operations."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from abc import ABC, abstractmethod
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class BaseFileWriter(ABC):
    """Port for writing text content to a target file path."""

    @abstractmethod
    def write_text(
        self,
        output_path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        """Write text content to output_path."""
