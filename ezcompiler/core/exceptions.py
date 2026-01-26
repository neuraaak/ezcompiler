# ///////////////////////////////////////////////////////////////
# EXCEPTIONS - Custom exception hierarchy
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Custom exceptions - Exception hierarchy for EzCompiler.

This module defines a hierarchy of custom exceptions for various
error conditions that may occur during EzCompiler operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# (no imports required)

# ///////////////////////////////////////////////////////////////
# EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class EzCompilerError(Exception):
    """
    Base exception for all EzCompiler errors.

    All custom exceptions in EzCompiler inherit from this class,
    allowing callers to catch all EzCompiler-specific errors with
    a single except clause.

    Example:
        >>> try:
        ...     # EzCompiler operation
        ... except EzCompilerError as e:
        ...     print(f"EzCompiler error: {e}")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the error condition
        """
        super().__init__(message)


class CompilationError(EzCompilerError):
    """
    Raised when compilation fails.

    Indicates an error occurred during the project compilation phase,
    such as compiler issues or incompatible compilation settings.

    Example:
        >>> raise CompilationError("PyInstaller compilation failed")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the compilation failure
        """
        super().__init__(message)


class ConfigurationError(EzCompilerError):
    """
    Raised when configuration is invalid.

    Indicates that configuration validation failed, such as missing
    required fields, invalid paths, or unsupported option values.

    Example:
        >>> raise ConfigurationError("Version cannot be empty")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the configuration error
        """
        super().__init__(message)


class TemplateError(EzCompilerError):
    """
    Raised when template processing fails.

    Indicates an error occurred while loading, processing, or
    validating template files.

    Example:
        >>> raise TemplateError("Template not found: config.yaml.template")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the template error
        """
        super().__init__(message)


class UploadError(EzCompilerError):
    """
    Raised when upload operation fails.

    Indicates an error occurred during the upload phase, such as
    network issues, authentication failures, or path problems.

    Example:
        >>> raise UploadError("Failed to connect to server")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the upload failure
        """
        super().__init__(message)


class VersionError(EzCompilerError):
    """
    Raised when version processing fails.

    Indicates an error occurred while generating or processing
    version information files.

    Example:
        >>> raise VersionError("Invalid version format: 1.0")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the version error
        """
        super().__init__(message)


class FileOperationError(EzCompilerError):
    """
    Raised when file operations fail.

    Indicates an error occurred during file operations such as
    reading, writing, copying, or deleting files.

    Example:
        >>> raise FileOperationError("Failed to copy file: permission denied")
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message describing the file operation error
        """
        super().__init__(message)
