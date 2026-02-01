# Test Documentation – EzCompiler

## Overview

This document provides comprehensive documentation for the **EzCompiler** test suite. The test suite ensures reliability, robustness, and correctness of all EzCompiler components through unit tests, integration tests, and robustness tests.

## Table of Contents

- [Test Documentation – EzCompiler](#test-documentation--ezcompiler)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [General Overview](#general-overview)
  - [Test Structure](#test-structure)
    - [Directory Organization](#directory-organization)
  - [Unit Tests](#unit-tests)
    - [test\_core.py – Core Module Tests](#test_corepy--core-module-tests)
      - [TestExceptions (5 tests)](#testexceptions-5-tests)
      - [TestCompilerConfig (8 tests)](#testcompilerconfig-8-tests)
    - [test\_compilers.py – Compiler Implementation Tests](#test_compilerspy--compiler-implementation-tests)
      - [TestCompilerImports (4 tests)](#testcompilerimports-4-tests)
      - [TestCompilerInstantiation (5 tests)](#testcompilerinstantiation-5-tests)
      - [TestCompilerNames (3 tests)](#testcompilernames-3-tests)
    - [test\_ezcompiler\_basic.py – EzCompiler Facade Tests](#test_ezcompiler_basicpy--ezcompiler-facade-tests)
      - [TestEzCompilerImport (11 tests)](#testezcompilerimport-11-tests)
      - [TestEzCompilerInitialization (2 tests)](#testezcompilerinitialization-2-tests)
    - [test\_utils.py – Utility Functions Tests](#test_utilspy--utility-functions-tests)
      - [TestFileUtils (3 tests)](#testfileutils-3-tests)
      - [TestValidationUtils (3 tests)](#testvalidationutils-3-tests)
      - [TestZipUtils (3 tests)](#testziputils-3-tests)
      - [TestFileUtilsMethods (4 tests)](#testfileutilsmethods-4-tests)
      - [TestValidationUtilsMethods (8 tests)](#testvalidationutilsmethods-8-tests)
      - [TestZipUtilsMethods (2 tests)](#testziputilsmethods-2-tests)
  - [Integration Tests](#integration-tests)
    - [test\_imports.py – Public API Import Tests](#test_importspy--public-api-import-tests)
      - [TestPublicAPIImports (4 tests)](#testpublicapiimports-4-tests)
    - [test\_ezcompiler\_integration.py – Component Integration](#test_ezcompiler_integrationpy--component-integration)
      - [TestEzCompilerIntegration (2 tests)](#testezcompilerintegration-2-tests)
  - [Robustness Tests](#robustness-tests)
    - [test\_error\_handling.py – Error Handling Tests](#test_error_handlingpy--error-handling-tests)
      - [TestConfigurationErrors (3 tests)](#testconfigurationerrors-3-tests)
      - [TestCompilationErrors (4 tests)](#testcompilationerrors-4-tests)
      - [TestFileOperationErrors (3 tests)](#testfileoperationerrors-3-tests)
    - [test\_edge\_cases.py – Edge Cases](#test_edge_casespy--edge-cases)
      - [TestExtremeValues (4 tests)](#testextremevalues-4-tests)
      - [TestVersionEdgeCases (3 tests)](#testversionedgecases-3-tests)
      - [TestPathEdgeCases (3 tests)](#testpathedgecases-3-tests)
  - [Test Configuration](#test-configuration)
    - [conftest.py – Shared Fixtures](#conftestpy--shared-fixtures)
  - [Running Tests](#running-tests)
    - [Using pytest](#using-pytest)
    - [Using run\_tests.py](#using-run_testspy)
  - [Coverage Reports](#coverage-reports)
  - [Test Markers](#test-markers)
  - [Best Practices](#best-practices)
    - [1. Test Isolation](#1-test-isolation)
    - [2. Use Fixtures](#2-use-fixtures)
    - [3. Use Appropriate Markers](#3-use-appropriate-markers)
    - [4. Coverage Goals](#4-coverage-goals)
    - [5. Platform Compatibility](#5-platform-compatibility)
  - [Known Issues and Solutions](#known-issues-and-solutions)
    - [Temporary File Cleanup](#temporary-file-cleanup)
    - [Slow Tests](#slow-tests)
  - [Additional Resources](#additional-resources)

---

## General Overview

The EzCompiler test suite is organized into three main categories:

- **Unit Tests** – Individual component testing with isolated test cases
- **Integration Tests** – Component interaction and integration scenarios
- **Robustness Tests** – Edge cases, error handling, and special character scenarios

## Test Structure

### Directory Organization

```text
tests/
├── conftest.py                           # Shared fixtures and pytest configuration
├── pytest.ini                            # Pytest settings
├── run_tests.py                          # Test runner script
├── unit/                                 # Unit tests (68 tests)
│   ├── __init__.py
│   ├── test_core.py                     # Exception and CompilerConfig tests (13 tests)
│   ├── test_compilers.py                # Compiler implementations (12 tests)
│   ├── test_ezcompiler_basic.py         # EzCompiler facade tests (13 tests)
│   └── test_utils.py                    # Utility functions tests (30 tests)
├── integration/                          # Integration tests
│   ├── __init__.py
│   ├── test_imports.py                  # Public API imports
│   └── test_ezcompiler_integration.py   # Component integration
└── robustness/                           # Robustness tests
    ├── __init__.py
    ├── test_error_handling.py           # Exception handling
    └── test_edge_cases.py               # Edge cases
```

---

## Unit Tests

### test_core.py – Core Module Tests

**Location:** `tests/unit/test_core.py`

**Test Classes:**

#### TestExceptions (5 tests)

- `test_ezcompiler_error_exists` – EzCompilerError can be imported
- `test_compilation_error_is_subclass` – CompilationError inherits from Exception
- `test_configuration_error_is_subclass` – ConfigurationError inherits from Exception
- `test_raise_ezcompiler_error` – EzCompilerError can be raised

#### TestCompilerConfig (8 tests)

- `test_compiler_config_import` – CompilerConfig import
- `test_compiler_config_creation_minimal` – Minimal configuration creation with temp files
- `test_compiler_config_creation_full` – Full configuration with all fields
- `test_compiler_config_to_dict` – Configuration to dictionary conversion
- `test_compiler_config_from_dict` – Configuration from dictionary
- `test_compiler_config_defaults` – Default values validation

### test_compilers.py – Compiler Implementation Tests

**Location:** `tests/unit/test_compilers.py`

**Test Classes:**

#### TestCompilerImports (4 tests)

- `test_base_compiler_import` – BaseCompiler can be imported
- `test_cx_freeze_compiler_import` – CxFreezeCompiler can be imported
- `test_pyinstaller_compiler_import` – PyInstallerCompiler can be imported  
- `test_nuitka_compiler_import` – NuitkaCompiler can be imported

#### TestCompilerInstantiation (5 tests)

- `test_instantiate_cx_freeze_compiler` – CxFreezeCompiler instantiation with temp files
- `test_instantiate_pyinstaller_compiler` – PyInstallerCompiler instantiation with temp files
- `test_instantiate_nuitka_compiler` – NuitkaCompiler instantiation with temp files
- `test_cx_freeze_compiler_has_config` – Config attribute validation
- `test_compiler_is_base_compiler_instance` – BaseCompiler inheritance check

#### TestCompilerNames (3 tests)

- `test_cx_freeze_compiler_name` – CxFreezeCompiler name verification
- `test_pyinstaller_compiler_name` – PyInstallerCompiler name verification
- `test_nuitka_compiler_name` – NuitkaCompiler name verification

### test_ezcompiler_basic.py – EzCompiler Facade Tests

**Location:** `tests/unit/test_ezcompiler_basic.py`

**Test Classes:**

#### TestEzCompilerImport (11 tests)

- `test_import_ezcompiler` – EzCompiler can be imported
- `test_instantiate_ezcompiler` – EzCompiler instantiation
- `test_ezcompiler_has_logger` – Logger attribute exists
- `test_ezcompiler_has_printer` – Printer attribute exists
- `test_ezcompiler_has_config` – Config property exists
- `test_ezcompiler_config_returns_compiler_config` – Config attribute validation
- `test_ezcompiler_with_custom_log_level` – Custom log level initialization
- `test_ezcompiler_with_custom_log_rotation` – Custom log rotation
- `test_ezcompiler_has_printer_attribute` – Printer accessible
- `test_ezcompiler_has_logger_attribute` – Logger accessible
- `test_ezcompiler_has_ezpl_attribute` – Ezpl accessible

#### TestEzCompilerInitialization (2 tests)

- `test_init_project_minimal` – Minimal project initialization with temp files
- `test_init_project_full` – Full project initialization with all options

### test_utils.py – Utility Functions Tests

**Location:** `tests/unit/test_utils.py`

**Test Classes:**

#### TestFileUtils (3 tests)

- `test_file_utils_exists` – FileUtils can be imported
- `test_file_utils_instantiate` – FileUtils instantiation

#### TestValidationUtils (3 tests)

- `test_validation_utils_exists` – ValidationUtils can be imported
- `test_validation_utils_instantiate` – ValidationUtils instantiation

#### TestZipUtils (3 tests)

- `test_zip_utils_exists` – ZipUtils can be imported
- `test_zip_utils_instantiate` – ZipUtils instantiation

#### TestFileUtilsMethods (4 tests)

- `test_file_utils_create_directory` – Directory creation with temp fixture
- `test_file_utils_create_directory_existing` – Existing directory handling
- `test_file_utils_get_file_size` – File size retrieval
- `test_file_utils_validate_file_exists` – File existence validation

#### TestValidationUtilsMethods (8 tests)

- `test_validate_version_valid` – Valid version string validation
- `test_validate_version_invalid` – Invalid version string rejection
- `test_validate_compiler_name_valid` – Valid compiler name validation
- `test_validate_compiler_name_invalid` – Invalid compiler name rejection
- `test_validate_upload_structure_valid` – Valid upload structure validation
- `test_validate_upload_structure_invalid` – Invalid upload structure rejection

#### TestZipUtilsMethods (2 tests)

- `test_create_zip_archive` – ZIP archive creation with temp files
- `test_list_zip_contents` – ZIP contents listing

---

## Integration Tests

### test_imports.py – Public API Import Tests

**Location:** `tests/integration/test_imports.py`

**Test Classes:**

#### TestPublicAPIImports (4 tests)

- `test_ezcompiler_import` – Main EzCompiler class import
- `test_compiler_config_import` – CompilerConfig dataclass import
- `test_exceptions_import` – Exception classes import
- `test_exception_hierarchy` – Exception inheritance validation

---

### test_ezcompiler_integration.py – Component Integration

**Location:** `tests/integration/test_ezcompiler_integration.py`

**Test Classes:**

#### TestEzCompilerIntegration (2 tests)

- `test_ezcompiler_with_config` – EzCompiler initialization with CompilerConfig
- `test_ezcompiler_logger_integration` – Logger component integration

---

## Robustness Tests

### test_error_handling.py – Error Handling Tests

**Location:** `tests/robustness/test_error_handling.py`

**Test Classes:**

**Test Classes:**

#### TestConfigurationErrors (3 tests)

- `test_invalid_config` – Invalid configuration detection
- `test_missing_required_fields` – Required field validation
- `test_invalid_version_format` – Version format validation

#### TestCompilationErrors (4 tests)

- `test_compilation_failure` – Compilation failure handling
- `test_invalid_compiler` – Invalid compiler name rejection
- `test_missing_main_file` – Missing main file detection
- `test_output_directory_error` – Output directory issues

#### TestFileOperationErrors (3 tests)

- `test_file_not_found` – File not found errors
- `test_directory_creation_error` – Directory creation failures
- `test_invalid_path` – Invalid path handling

---

### test_edge_cases.py – Edge Cases

**Location:** `tests/robustness/test_edge_cases.py`

**Test Classes:**

#### TestExtremeValues (4 tests)

- `test_very_long_project_name` – Long project names (255+ chars)
- `test_empty_project_name` – Empty string handling
- `test_very_deep_directory_structure` – Deep nested paths
- `test_special_characters_in_name` – Unicode and special chars

#### TestVersionEdgeCases (3 tests)

- `test_version_edge_formats` – Various version formats (0.0.0, 99.99.99)
- `test_invalid_version_formats` – Invalid versions (abc, 1.2.x)
- `test_version_with_prerelease` – Pre-release identifiers

#### TestPathEdgeCases (3 tests)

- `test_relative_paths` – Relative path handling
- `test_absolute_paths` – Absolute path normalization
- `test_path_with_spaces` – Spaces in paths

---

## Test Configuration

### conftest.py – Shared Fixtures

**Location:** `tests/conftest.py`

**Fixtures:**

- `temp_dir` – Temporary directory for test file operations (scope: function)
- `temp_file` – Temporary file creation in temp_dir (scope: function)

**Usage:**

```python
def test_example(temp_dir, temp_file):
    # temp_dir: pathlib.Path to temporary directory
    # temp_file: callable(name: str, content: str) -> Path
    test_py = temp_file("test.py", "print('hello')")
    assert test_py.exists()
```

---

## Running Tests

### Using pytest

```bash
# All tests
pytest tests/

# Specific directory
pytest tests/unit/
pytest tests/integration/
pytest tests/robustness/

# Specific test file
pytest tests/unit/test_ezcompiler.py

# Specific test class
pytest tests/unit/test_ezcompiler.py::TestInitialization

# Specific test
pytest tests/unit/test_ezcompiler.py::TestInitialization::test_initialization_default

# With coverage
pytest --cov=ezcompiler --cov-report=html tests/
```

### Using run_tests.py

```bash
# Unit tests
python tests/run_tests.py --type unit

# Integration tests
python tests/run_tests.py --type integration

# Robustness tests
python tests/run_tests.py --type robustness

# All tests with coverage
python tests/run_tests.py --type all --coverage

# Parallel execution
python tests/run_tests.py --parallel

# Verbose mode
python tests/run_tests.py --verbose
```

---

## Coverage Reports

```bash
# Terminal report
pytest --cov=ezcompiler --cov-report=term-missing tests/

# HTML report
pytest --cov=ezcompiler --cov-report=html:htmlcov tests/
# Open htmlcov/index.html in browser

# XML report (for CI/CD)
pytest --cov=ezcompiler --cov-report=xml tests/
```

---

## Test Markers

Custom pytest markers for test categorization:

- `@pytest.mark.unit` – Unit tests
- `@pytest.mark.integration` – Integration tests
- `@pytest.mark.robustness` – Robustness tests
- `@pytest.mark.slow` – Slow tests
- `@pytest.mark.compilation` – Compilation-related tests
- `@pytest.mark.upload` – Upload-related tests

**Usage:**

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run integration and robustness tests
pytest -m "integration or robustness"

# Run compilation tests
pytest -m compilation
```

---

## Best Practices

### 1. Test Isolation

Each test is independent. Use fixtures for setup and teardown.

### 2. Use Fixtures

Use shared fixtures from `conftest.py`:

```python
def test_example(temp_dir, sample_project):
    # Use temp_dir and sample_project
    pass
```

### 3. Use Appropriate Markers

Mark tests with appropriate markers:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_integration():
    pass
```

### 4. Coverage Goals

Aim for >90% code coverage. Use coverage reports to identify untested code.

### 5. Platform Compatibility

Tests should be platform-independent. Handle path differences:

```python
from pathlib import Path

# Use Path instead of string concatenation
path = Path("tests") / "data" / "file.txt"
```

---

## Known Issues and Solutions

### Temporary File Cleanup

On Windows, files may remain locked. Use fixtures that properly cleanup:

```python
@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")
    yield file_path
    # Cleanup happens automatically
```

### Slow Tests

Mark slow tests and optionally skip them:

```bash
# Run all except slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m "slow"
```

---

## Additional Resources

- **[Test Summary](SUMMARY.md)** – Quick test overview
- **[API Documentation](../api/API_DOCUMENTATION.md)** – API reference
- **[Examples Documentation](../examples/EXAMPLES.md)** – Usage examples

---

**EzCompiler** – Comprehensive test suite for reliable project compilation. 🧪
