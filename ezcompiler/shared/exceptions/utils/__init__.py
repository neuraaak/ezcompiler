# ///////////////////////////////////////////////////////////////
# EXCEPTIONS PACKAGE - Specialized exception hierarchy
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Exceptions package - Specialized exceptions organized by module functionality.

This package provides fine-grained exceptions for different layers and utilities
of the EzCompiler project, enabling precise error handling.

Structure:
- file_exceptions: File and directory operation errors
- compiler_exceptions: Compiler operation errors
- uploader_exceptions: Upload operation errors
- validation_exceptions: Validation errors
- zip_exceptions: ZIP archive errors
- config_exceptions: Configuration errors
- template_exceptions: Template processing errors
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS - Base exception
# ///////////////////////////////////////////////////////////////
from .base import EzCompilerError

# ///////////////////////////////////////////////////////////////
# IMPORTS - Compiler exceptions
# ///////////////////////////////////////////////////////////////
from .compiler_exceptions import (
    CompilationExecutionError,
    CompilerConfigValidationError,
    CompilerError,
    CompilerNotAvailableError,
    IncludeFilesFormatError,
    MainFileNotFoundError,
    OutputDirectoryError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - Config exceptions
# ///////////////////////////////////////////////////////////////
from .config_exceptions import (
    CompilerOptionError,
    ConfigError,
    ConfigFieldValidationError,
    ConfigFileNotFoundError,
    ConfigFileParseError,
    ConfigPathError,
    IncludeFilesError,
    MissingRequiredConfigError,
    OutputFolderError,
    TomlNotAvailableError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - File exceptions
# ///////////////////////////////////////////////////////////////
from .file_exceptions import (
    DirectoryCreationError,
    DirectoryListError,
    FileAccessError,
    FileCopyError,
    FileDeleteError,
    FileError,
    FileMoveError,
    FileNotFoundError,
    PathNormalizationError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - ZIP exceptions
# ///////////////////////////////////////////////////////////////
from .template_exceptions import (
    TemplateFileWriteError,
    TemplateProcessingError,
    TemplateSubstitutionError,
    TemplateValidationError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - Uploader exceptions
# ///////////////////////////////////////////////////////////////
from .uploader_exceptions import (
    BackupGenerationError,
    ServerConfigError,
    SourcePathError,
    UploadAuthenticationError,
    UploadConnectionError,
    UploaderTypeError,
    UploadTimeoutError,
)

# ///////////////////////////////////////////////////////////////
# IMPORTS - Validation exceptions
# ///////////////////////////////////////////////////////////////
from .validation_exceptions import (
    ChoiceValidationError,
    FormatValidationError,
    LengthValidationError,
    PatternValidationError,
    RangeValidationError,
    RequiredFieldError,
    SchemaValidationError,
    TypeValidationError,
    ValidationError,
)
from .zip_exceptions import (
    ZipCompressionError,
    ZipCreationError,
    ZipError,
    ZipExtractionError,
    ZipFileCorruptedError,
    ZipFileNotFoundError,
    ZipPathError,
    ZipProgressError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "EzCompilerError",
    # File exceptions
    "FileError",
    "FileNotFoundError",
    "DirectoryCreationError",
    "FileAccessError",
    "FileCopyError",
    "FileMoveError",
    "FileDeleteError",
    "DirectoryListError",
    "PathNormalizationError",
    # Compiler exceptions
    "CompilerError",
    "CompilerConfigValidationError",
    "MainFileNotFoundError",
    "OutputDirectoryError",
    "IncludeFilesFormatError",
    "CompilerNotAvailableError",
    "CompilationExecutionError",
    # Uploader exceptions
    "SourcePathError",
    "UploaderTypeError",
    "ServerConfigError",
    "BackupGenerationError",
    "UploadConnectionError",
    "UploadAuthenticationError",
    "UploadTimeoutError",
    # Validation exceptions
    "ValidationError",
    "TypeValidationError",
    "FormatValidationError",
    "RangeValidationError",
    "LengthValidationError",
    "PatternValidationError",
    "SchemaValidationError",
    "ChoiceValidationError",
    "RequiredFieldError",
    # ZIP exceptions
    "ZipError",
    "ZipCreationError",
    "ZipExtractionError",
    "ZipFileNotFoundError",
    "ZipFileCorruptedError",
    "ZipPathError",
    "ZipProgressError",
    "ZipCompressionError",
    # Config exceptions
    "ConfigError",
    "ConfigFieldValidationError",
    "ConfigFileNotFoundError",
    "ConfigFileParseError",
    "ConfigPathError",
    "CompilerOptionError",
    "OutputFolderError",
    "IncludeFilesError",
    "MissingRequiredConfigError",
    "TomlNotAvailableError",
    # Template exceptions
    "TemplateProcessingError",
    "TemplateSubstitutionError",
    "TemplateFileWriteError",
    "TemplateValidationError",
]
