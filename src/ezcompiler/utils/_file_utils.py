# ///////////////////////////////////////////////////////////////
# FILE_UTILS - File and directory operation utilities
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
File utilities - File and directory operation utilities for EzCompiler.

This module provides utility functions for common file operations including
path validation, directory creation, file copying, and path manipulation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
from pathlib import Path

# Local imports
from ..shared.exceptions.utils import (
    DirectoryCreationError,
    DirectoryListError,
    FileAccessError,
    FileCopyError,
    FileDeleteError,
    FileMoveError,
    FileNotFoundError,
)

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class FileUtils:
    """
    File and directory operations utility class.

    Provides static methods for common file and directory operations
    used throughout the EzCompiler project, including validation,
    creation, copying, moving, and listing operations.

    Example:
        >>> FileUtils.create_directory_if_not_exists("./output")
        >>> file_size = FileUtils.get_file_size("path/to/file.txt")
    """

    # ////////////////////////////////////////////////
    # VALIDATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def validate_file_exists(path: str | Path) -> bool:
        """
        Validate that a file exists and is accessible.

        Args:
            path: Path to the file to validate

        Returns:
            bool: True if file exists and is accessible, False otherwise
        """
        try:
            file_path = Path(path)
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False

    @staticmethod
    def validate_directory_exists(path: str | Path) -> bool:
        """
        Validate that a directory exists and is accessible.

        Args:
            path: Path to the directory to validate

        Returns:
            bool: True if directory exists and is accessible, False otherwise
        """
        try:
            dir_path = Path(path)
            return dir_path.exists() and dir_path.is_dir()
        except Exception:
            return False

    # ////////////////////////////////////////////////
    # DIRECTORY CREATION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def create_directory_if_not_exists(path: str | Path) -> None:
        """
        Create a directory if it doesn't exist.

        Args:
            path: Path to the directory to create

        Raises:
            DirectoryCreationError: If directory creation fails
        """
        try:
            dir_path = Path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DirectoryCreationError(
                f"Failed to create directory {path}: {e}"
            ) from e

    @staticmethod
    def ensure_parent_directory_exists(file_path: str | Path) -> None:
        """
        Ensure that the parent directory of a file exists.

        Args:
            file_path: Path to the file

        Raises:
            DirectoryCreationError: If parent directory creation fails
        """
        try:
            path = Path(file_path)
            # Not root directory check
            if path.parent != path:
                path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DirectoryCreationError(
                f"Failed to create parent directory for {file_path}: {e}"
            ) from e

    # ////////////////////////////////////////////////
    # FILE SIZE METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def get_file_size(path: str | Path) -> int:
        """
        Get the size of a file in bytes.

        Args:
            path: Path to the file

        Returns:
            int: File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            FileAccessError: If file is not accessible
        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                raise FileNotFoundError(f"File does not exist: {path}")
            return file_path.stat().st_size
        except FileNotFoundError:
            raise
        except Exception as e:
            raise FileAccessError(f"Failed to get file size for {path}: {e}") from e

    # ////////////////////////////////////////////////
    # FILE OPERATIONS METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def copy_file(
        source: str | Path,
        destination: str | Path,
        preserve_metadata: bool = True,
    ) -> None:
        """
        Copy a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path
            preserve_metadata: Whether to preserve file metadata (default: True)

        Raises:
            FileNotFoundError: If source file doesn't exist
            FileCopyError: If copy operation fails
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                raise FileNotFoundError(f"Source file does not exist: {source}")

            # Ensure destination directory exists
            FileUtils.ensure_parent_directory_exists(dest_path)

            # Copy the file with or without metadata preservation
            if preserve_metadata:
                shutil.copy2(source_path, dest_path)
            else:
                shutil.copy(source_path, dest_path)

        except FileNotFoundError:
            raise
        except Exception as e:
            raise FileCopyError(
                f"Failed to copy file from {source} to {destination}: {e}"
            ) from e

    @staticmethod
    def move_file(source: str | Path, destination: str | Path) -> None:
        """
        Move a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Raises:
            FileNotFoundError: If source file doesn't exist
            FileMoveError: If move operation fails
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                raise FileNotFoundError(f"Source file does not exist: {source}")

            # Ensure destination directory exists
            FileUtils.ensure_parent_directory_exists(dest_path)

            # Move the file
            shutil.move(str(source_path), str(dest_path))

        except FileNotFoundError:
            raise
        except Exception as e:
            raise FileMoveError(
                f"Failed to move file from {source} to {destination}: {e}"
            ) from e

    @staticmethod
    def delete_file(path: str | Path) -> None:
        """
        Delete a file.

        Args:
            path: Path to the file to delete

        Raises:
            FileDeleteError: If deletion fails
        """
        try:
            file_path = Path(path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            raise FileDeleteError(f"Failed to delete file {path}: {e}") from e

    # ////////////////////////////////////////////////
    # LISTING AND EXTENSION METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def list_files(directory: str | Path, pattern: str = "*") -> list[Path]:
        """
        List all files in a directory matching a pattern.

        Args:
            directory: Directory to search in
            pattern: File pattern to match (default: "*")

        Returns:
            list[Path]: List of matching file paths

        Raises:
            FileNotFoundError: If directory doesn't exist
            DirectoryListError: If directory access fails
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory does not exist: {directory}")

            return list(dir_path.glob(pattern))
        except FileNotFoundError:
            raise
        except Exception as e:
            raise DirectoryListError(f"Failed to list files in {directory}: {e}") from e

    @staticmethod
    def get_file_extension(path: str | Path) -> str:
        """
        Get the file extension.

        Args:
            path: Path to the file

        Returns:
            str: File extension (including the dot)
        """
        return Path(path).suffix

    @staticmethod
    def get_file_name_without_extension(path: str | Path) -> str:
        """
        Get the file name without extension.

        Args:
            path: Path to the file

        Returns:
            str: File name without extension
        """
        return Path(path).stem

    # ////////////////////////////////////////////////
    # PATH UTILITIES METHODS
    # ////////////////////////////////////////////////

    @staticmethod
    def is_hidden_file(path: str | Path) -> bool:
        """
        Check if a file is hidden.

        Args:
            path: Path to the file

        Returns:
            bool: True if file is hidden, False otherwise
        """
        file_path = Path(path)
        return file_path.name.startswith(".")

    @staticmethod
    def get_relative_path(base_path: str | Path, target_path: str | Path) -> str:
        """
        Get the relative path from base_path to target_path.

        Args:
            base_path: Base directory path
            target_path: Target file/directory path

        Returns:
            str: Relative path from base to target

        Note:
            If target is not relative to base, returns the absolute path.
        """
        try:
            base = Path(base_path).resolve()
            target = Path(target_path).resolve()
            return str(target.relative_to(base))
        except ValueError:
            # If target is not relative to base, return the absolute path
            return str(target)

    @staticmethod
    def normalize_path(path: str | Path) -> Path:
        """
        Normalize a path (resolve symlinks, make absolute).

        Args:
            path: Path to normalize

        Returns:
            Path: Normalized absolute path
        """
        return Path(path).resolve()

    @staticmethod
    def ensure_unique_filename(path: str | Path) -> Path:
        """
        Ensure a filename is unique by adding a number suffix if necessary.

        Args:
            path: Original file path

        Returns:
            Path: Unique file path, with numeric suffix added if original exists

        Example:
            >>> # If "output.txt" exists, returns "output_1.txt"
            >>> unique_path = FileUtils.ensure_unique_filename("output.txt")
        """
        file_path = Path(path)
        if not file_path.exists():
            return file_path

        counter = 1
        while True:
            new_path = file_path.with_name(
                f"{file_path.stem}_{counter}{file_path.suffix}"
            )
            if not new_path.exists():
                return new_path
            counter += 1
