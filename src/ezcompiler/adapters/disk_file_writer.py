# ///////////////////////////////////////////////////////////////
# DISK_FILE_WRITER - Local filesystem file writer adapter
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""Filesystem adapter implementing the BaseFileWriter port."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Local imports
from .base_file_writer import BaseFileWriter

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class DiskFileWriter(BaseFileWriter):
    """Write text files to local disk using pathlib."""

    def write_text(
        self,
        output_path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        """Write text content to disk."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding=encoding)
