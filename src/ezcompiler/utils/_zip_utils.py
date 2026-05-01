# ///////////////////////////////////////////////////////////////
# ZIP_UTILS - ZIP archive operation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
ZIP utilities - ZIP archive operation utilities for EzCompiler.

This module provides utility functions for creating, extracting, and managing
ZIP archives used in the EzCompiler project, with support for progress tracking
and logging.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import zipfile
from collections.abc import Callable
from pathlib import Path

# Local imports
from ..shared.exceptions.utils import (
    ZipCreationError,
    ZipExtractionError,
    ZipFileCorruptedError,
    ZipFileNotFoundError,
    ZipPathError,
)
from ._file_utils import FileUtils

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ZipUtils:
    """
    ZIP archive operations utility class.

    Provides static methods for creating, extracting, and managing
    ZIP archives used in the EzCompiler project. Supports compression,
    progress tracking, and detailed logging.

    Class Variables:
        _ezpl: Cached Ezpl instance for logging
        _logger: Cached logger instance
        _printer: Cached printer instance

    Example:
        >>> ZipUtils.create_zip_archive("./source", "./output.zip")
        >>> ZipUtils.extract_zip_archive("./output.zip", "./extracted")
    """

    # Utils layer should not initialize logging directly
    # Logging is handled by the service and interface layers

    # ////////////////////////////////////////////////
    # ARCHIVE CREATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def create_zip_archive(
        source_path: str | Path,
        output_path: str | Path,
        compression: int = zipfile.ZIP_DEFLATED,
        include_hidden: bool = False,
        progress_callback: Callable[[str, int], None] | None = None,
    ) -> None:
        """
        Create a ZIP archive from a file or directory.

        Args:
            source_path: Path to the source file or directory
            output_path: Path where the ZIP file will be created
            compression: Compression method (default: ZIP_DEFLATED)
            include_hidden: Whether to include hidden files (default: False)
            progress_callback: Optional callback for progress updates (file, progress)

        Raises:
            FileOperationError: If ZIP creation fails

        Note:
            Progress callback receives (filename: str, progress: int) where
            progress is a percentage from 0 to 100.
        """
        try:
            source = Path(source_path)
            output = Path(output_path)

            if not source.exists():
                raise ZipPathError(f"Source path does not exist: {source_path}")

            # Ensure output directory exists
            FileUtils.ensure_parent_directory_exists(output)

            # Create the ZIP file
            with zipfile.ZipFile(output, "w", compression) as zipf:
                if source.is_file():
                    # Add single file
                    arcname = source.name
                    zipf.write(source, arcname)
                    if progress_callback:
                        progress_callback(str(source), 100)

                elif source.is_dir():
                    # Add directory recursively with progress tracking
                    total_files = sum(1 for _ in source.rglob("*") if _.is_file())
                    processed_files = 0

                    for file_path in source.rglob("*"):
                        if file_path.is_file():
                            # Skip hidden files if not requested
                            if not include_hidden and ZipUtils._is_hidden_file(
                                file_path
                            ):
                                continue

                            # Calculate relative path for archive
                            arcname = file_path.relative_to(source)
                            zipf.write(file_path, arcname)

                            processed_files += 1
                            if progress_callback:
                                progress = int((processed_files / total_files) * 100)
                                progress_callback(str(file_path), progress)

        except Exception as e:
            raise ZipCreationError(
                f"Failed to create ZIP archive {output_path}: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # ARCHIVE EXTRACTION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def extract_zip_archive(
        zip_path: str | Path,
        extract_path: str | Path,
        password: str | None = None,
        progress_callback: Callable[[str, int], None] | None = None,
    ) -> None:
        """
        Extract a ZIP archive to a directory.

        Args:
            zip_path: Path to the ZIP file
            extract_path: Directory where files will be extracted
            password: Optional password for encrypted archives (default: None)
            progress_callback: Optional callback for progress updates (file, progress)

        Raises:
            FileOperationError: If extraction fails

        Note:
            Progress callback receives (filename: str, progress: int) where
            progress is a percentage from 0 to 100.
        """
        try:
            zip_file = Path(zip_path)
            extract_dir = Path(extract_path)

            if not zip_file.exists():
                raise ZipFileNotFoundError(f"ZIP file does not exist: {zip_path}")

            if not zip_file.is_file():
                raise ZipPathError(f"Path is not a file: {zip_path}")

            # Create extraction directory
            FileUtils.create_directory_if_not_exists(extract_dir)

            # Extract the ZIP file
            with zipfile.ZipFile(zip_file, "r") as zipf:
                # Set password if provided
                if password:
                    zipf.setpassword(password.encode("utf-8"))

                # Get list of files for progress tracking
                file_list = zipf.namelist()
                total_files = len(file_list)

                for index, file_info in enumerate(zipf.filelist):
                    try:
                        zipf.extract(file_info, extract_dir)

                        if progress_callback:
                            progress = int(((index + 1) / total_files) * 100)
                            progress_callback(file_info.filename, progress)

                    except Exception as e:
                        raise ZipExtractionError(
                            f"Failed to extract file '{file_info.filename}' from ZIP archive {zip_path}: {e}"
                        ) from e

        except Exception as e:
            raise ZipExtractionError(
                f"Failed to extract ZIP archive {zip_path}: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # ARCHIVE INFORMATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def list_zip_contents(zip_path: str | Path) -> list[str]:
        """
        List the contents of a ZIP archive.

        Args:
            zip_path: Path to the ZIP file

        Returns:
            list[str]: List of file names in the archive

        Raises:
            ZipFileCorruptedError: If listing fails
        """
        try:
            zip_file = Path(zip_path)

            if not zip_file.exists():
                raise ZipFileNotFoundError(f"ZIP file does not exist: {zip_path}")

            with zipfile.ZipFile(zip_file, "r") as zipf:
                return zipf.namelist()

        except Exception as e:
            raise ZipFileCorruptedError(
                f"Failed to list ZIP contents {zip_path}: {e}"
            ) from e

    @staticmethod
    def get_zip_info(zip_path: str | Path) -> dict:
        """
        Get information about a ZIP archive.

        Args:
            zip_path: Path to the ZIP file

        Returns:
            dict: Dictionary with ZIP information including:
                - file_count: Number of files in the archive
                - total_size: Total uncompressed size in bytes
                - compressed_size: Total compressed size in bytes
                - compression_ratio: Compression ratio as percentage
                - files: List of file names in the archive

        Raises:
            ZipFileCorruptedError: If getting info fails
        """
        try:
            zip_file = Path(zip_path)

            if not zip_file.exists():
                raise ZipFileNotFoundError(f"ZIP file does not exist: {zip_path}")

            with zipfile.ZipFile(zip_file, "r") as zipf:
                info = zipf.infolist()

                total_size = sum(file_info.file_size for file_info in info)
                compressed_size = sum(file_info.compress_size for file_info in info)

                return {
                    "file_count": len(info),
                    "total_size": total_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": (
                        (1 - compressed_size / total_size) * 100
                        if total_size > 0
                        else 0
                    ),
                    "files": [file_info.filename for file_info in info],
                }

        except Exception as e:
            raise ZipFileCorruptedError(
                f"Failed to get ZIP info {zip_path}: {e}"
            ) from e

    @staticmethod
    def is_valid_zip(zip_path: str | Path) -> bool:
        """
        Check if a file is a valid ZIP archive.

        Args:
            zip_path: Path to the file to check

        Returns:
            bool: True if file is a valid ZIP archive, False otherwise
        """
        try:
            zip_file = Path(zip_path)

            if not zip_file.exists() or not zip_file.is_file():
                return False

            with zipfile.ZipFile(zip_file, "r") as zipf:
                # Try to read the ZIP structure to test integrity
                zipf.testzip()
                return True

        except Exception:
            return False

    # ////////////////////////////////////////////////
    # FILE MODIFICATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def add_file_to_zip(
        zip_path: str | Path,
        file_path: str | Path,
        arcname: str | None = None,
    ) -> None:
        """
        Add a single file to an existing ZIP archive.

        Args:
            zip_path: Path to the ZIP file
            file_path: Path to the file to add
            arcname: Name of the file in the archive (default: file name)

        Raises:
            ZipCreationError: If adding file fails
        """
        try:
            zip_file = Path(zip_path)
            file_to_add = Path(file_path)

            if not file_to_add.exists():
                raise ZipPathError(f"File to add does not exist: {file_path}")

            if not file_to_add.is_file():
                raise ZipPathError(f"Path is not a file: {file_path}")

            # Use file name if arcname not specified
            if arcname is None:
                arcname = file_to_add.name

            with zipfile.ZipFile(zip_file, "a") as zipf:
                zipf.write(file_to_add, arcname)

        except Exception as e:
            raise ZipCreationError(f"Failed to add file to ZIP {zip_path}: {e}") from e

    @staticmethod
    def remove_file_from_zip(zip_path: str | Path, file_name: str) -> None:
        """
        Remove a file from a ZIP archive.

        Args:
            zip_path: Path to the ZIP file
            file_name: Name of the file to remove from the archive

        Raises:
            ZipCreationError: If removal fails

        Note:
            Creates a temporary file during removal process.
        """
        try:
            zip_file = Path(zip_path)

            if not zip_file.exists():
                raise ZipFileNotFoundError(f"ZIP file does not exist: {zip_path}")

            # Create a temporary ZIP without the file
            temp_zip = zip_file.with_suffix(".tmp.zip")

            with (
                zipfile.ZipFile(zip_file, "r") as zipf_read,
                zipfile.ZipFile(temp_zip, "w") as zipf_write,
            ):
                for item in zipf_read.infolist():
                    if item.filename != file_name:
                        zipf_write.writestr(item, zipf_read.read(item.filename))

            # Replace original with temporary
            zip_file.unlink()
            temp_zip.rename(zip_file)

        except Exception as e:
            raise ZipCreationError(
                f"Failed to remove file from ZIP {zip_path}: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # PRIVATE UTILITY METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def _is_hidden_file(file_path: Path) -> bool:
        """
        Check if a file is hidden (starts with dot or has hidden attribute).

        Args:
            file_path: Path to the file

        Returns:
            bool: True if file is hidden, False otherwise

        Note:
            On Windows, checks both filename and FILE_ATTRIBUTE_HIDDEN.
            On Unix, checks if filename starts with dot.
        """
        # Check if filename starts with dot
        if file_path.name.startswith("."):
            return True

        # Check hidden attribute on Windows
        try:
            import stat

            return bool(
                file_path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN
            )
        except (AttributeError, ImportError):
            # Not on Windows or attribute not available
            return False
