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
    - [test_ezcompiler.py](#test_ezcompilerpy--ezcompiler-facade-tests)
    - [test_compiler_config.py](#test_compiler_configpy--compilerconfig-tests)
    - [test_compilers.py](#test_compilerspy--compiler-tests)
    - [test_generators.py](#test_generatorspy--generator-tests)
    - [test_templates.py](#test_templatespy--template-system-tests)
    - [test_uploaders.py](#test_uploaderspy--uploader-tests)
    - [test_utils.py](#test_utilspy--utility-tests)
  - [Integration Tests](#integration-tests)
    - [test_ezcompiler_integration.py](#test_ezcompiler_integrationpy--full-workflow-integration)
    - [test_config_integration.py](#test_config_integrationpy--configuration-integration)
    - [test_compilation_integration.py](#test_compilation_integrationpy--compilation-pipeline-integration)
  - [Robustness Tests](#robustness-tests)
    - [test_error_handling.py](#test_error_handlingpy--error-handling)
    - [test_edge_cases.py](#test_edge_casespy--edge-cases)
  - [Test Configuration](#test-configuration)
    - [conftest.py](#conftest.py--shared-fixtures)
    - [run_tests.py](#run_testspy--test-runner)
  - [Running Tests](#running-tests)
    - [Using pytest](#using-pytest)
    - [Using run_tests.py](#using-run_testspy)
  - [Coverage Reports](#coverage-reports)
  - [Test Markers](#test-markers)
  - [Best Practices](#best-practices)
  - [Known Issues and Solutions](#known-issues-and-solutions)
  - [Additional Resources](#additional-resources)

---

## General Overview

The EzCompiler test suite is organized into three main categories:

- **Unit Tests** – Individual component testing with isolated test cases
- **Integration Tests** – Component interaction and integration scenarios
- **Robustness Tests** – Edge cases, error handling, and special character scenarios

## Test Structure

### Directory Organization

```
tests/
├── conftest.py                           # Shared fixtures and pytest configuration
├── run_tests.py                          # Test runner script
├── unit/                                 # Unit tests
│   ├── __init__.py
│   ├── test_ezcompiler.py               # EzCompiler facade tests
│   ├── test_compiler_config.py          # CompilerConfig tests
│   ├── test_compilers.py                # Compiler implementations tests
│   ├── test_generators.py               # Generator implementations tests
│   ├── test_templates.py                # Template system tests
│   ├── test_uploaders.py                # Uploader implementations tests
│   └── test_utils.py                    # Utility functions tests
├── integration/                          # Integration tests
│   ├── __init__.py
│   ├── test_ezcompiler_integration.py   # Full workflow integration
│   ├── test_config_integration.py       # Configuration integration
│   └── test_compilation_integration.py  # Compilation pipeline integration
└── robustness/                           # Robustness tests
    ├── __init__.py
    ├── test_error_handling.py           # Error scenarios
    ├── test_edge_cases.py               # Edge cases
    └── test_special_cases.py            # Special cases
```

---

## Unit Tests

### test_ezcompiler.py – EzCompiler Facade Tests

**Location:** `tests/unit/test_ezcompiler.py`

**Test Classes:**

#### TestInitialization

- `test_initialization_default` – Default initialization
- `test_initialization_with_log_level` – Custom log level
- `test_initialization_with_log_rotation` – Custom log rotation

#### TestProjectInitialization

- `test_init_project_minimal` – Minimal project initialization
- `test_init_project_complete` – Full project initialization
- `test_init_project_validation` – Configuration validation

#### TestFileGeneration

- `test_generate_version_file` – Version file generation
- `test_generate_setup_file` – Setup file generation
- `test_generate_files_sequence` – Sequential generation

#### TestCompilation

- `test_compile_project_pyinstaller` – PyInstaller compilation
- `test_compile_project_cxfreeze` – Cx_Freeze compilation
- `test_compile_project_auto` – Automatic compiler selection
- `test_compile_with_options` – Compilation with options

#### TestZipping

- `test_zip_compiled_project` – ZIP archive creation
- `test_zip_verification` – ZIP contents verification

#### TestUpload

- `test_upload_disk` – Disk upload
- `test_upload_server` – Server upload

#### TestAccessors

- `test_logger_accessor` – Logger property access
- `test_printer_accessor` – Printer property access
- `test_config_accessor` – Config property access

### test_compiler_config.py – CompilerConfig Tests

**Location:** `tests/unit/test_compiler_config.py`

**Test Classes:**

#### TestCreation

- `test_create_minimal_config` – Minimal configuration
- `test_create_full_config` – Complete configuration
- `test_create_with_defaults` – Default values

#### TestValidation

- `test_validate_required_fields` – Required field validation
- `test_validate_version_format` – Version format validation
- `test_validate_paths` – Path validation

#### TestConversion

- `test_to_dict` – Dictionary conversion
- `test_from_dict` – Creation from dictionary
- `test_roundtrip_conversion` – Conversion roundtrip

#### TestProperties

- `test_output_path_property` – Output path property
- `test_version_tuple_property` – Version tuple property

#### TestErrorHandling

- `test_invalid_version` – Invalid version handling
- `test_missing_required_field` – Missing field handling

### test_compilers.py – Compiler Tests

**Location:** `tests/unit/test_compilers.py`

**Test Classes:**

#### TestCxFreezeCompiler

- `test_cxfreeze_initialization` – Initialization
- `test_cxfreeze_compilation` – Compilation process
- `test_cxfreeze_zip_needed` – ZIP requirement check
- `test_cxfreeze_error_handling` – Error handling

#### TestPyInstallerCompiler

- `test_pyinstaller_initialization` – Initialization
- `test_pyinstaller_compilation` – Compilation process
- `test_pyinstaller_zip_needed` – ZIP requirement check
- `test_pyinstaller_single_file` – Single-file mode

#### TestCompilerSelection

- `test_compiler_validation` – Compiler name validation
- `test_compiler_requirements` – Requirements checking

### test_generators.py – Generator Tests

**Location:** `tests/unit/test_generators.py`

**Test Classes:**

#### TestVersionGenerator

- `test_generate_version_content` – Content generation
- `test_generate_version_file` – File generation
- `test_version_template_variables` – Template variables
- `test_version_file_format` – File format

#### TestSetupGenerator

- `test_generate_setup_content` – Content generation
- `test_generate_setup_file` – File generation
- `test_setup_template_variables` – Template variables
- `test_setup_file_format` – File format
- `test_setup_with_packages` – Package handling

### test_templates.py – Template System Tests

**Location:** `tests/unit/test_templates.py`

**Test Classes:**

#### TestTemplateManager

- `test_load_template` – Template loading
- `test_list_templates` – List templates
- `test_get_template_path` – Path retrieval
- `test_process_template` – Template processing

#### TestTemplateProcessor

- `test_substitute_variables` – Variable substitution
- `test_generate_mockup` – Mockup generation
- `test_validate_template` – Template validation
- `test_missing_variables` – Missing variables handling

### test_uploaders.py – Uploader Tests

**Location:** `tests/unit/test_uploaders.py`

**Test Classes:**

#### TestDiskUploader

- `test_disk_upload_file` – File upload
- `test_disk_upload_directory` – Directory upload
- `test_disk_upload_validation` – Upload validation
- `test_disk_permissions` – Permission handling

#### TestServerUploader

- `test_server_upload_initialization` – Initialization
- `test_server_upload_connection` – Connection test
- `test_server_upload_retry` – Retry logic
- `test_server_authentication` – Authentication

#### TestUploaderFactory

- `test_create_disk_uploader` – Disk uploader creation
- `test_create_server_uploader` – Server uploader creation
- `test_invalid_structure` – Invalid structure handling

### test_utils.py – Utility Tests

**Location:** `tests/unit/test_utils.py`

**Test Classes:**

#### TestFileUtils

- `test_ensure_directory` – Directory creation
- `test_copy_file` – File copying
- `test_copy_directory` – Directory copying
- `test_delete_directory` – Directory deletion
- `test_get_file_size` – File size

#### TestValidationUtils

- `test_validate_version` – Version validation
- `test_validate_path` – Path validation
- `test_validate_compiler_name` – Compiler name validation
- `test_validate_upload_structure` – Structure validation

#### TestZipUtils

- `test_create_zip_archive` – ZIP creation
- `test_extract_zip_archive` – ZIP extraction
- `test_list_zip_contents` – ZIP listing
- `test_zip_with_progress` – Progress callback

---

## Integration Tests

### test_ezcompiler_integration.py – Full Workflow Integration

**Location:** `tests/integration/test_ezcompiler_integration.py`

**Test Classes:**

#### TestFullBuildWorkflow

- `test_complete_build_pipeline` – Full build workflow
- `test_init_to_compilation` – Initialization to compilation
- `test_compilation_to_distribution` – Compilation to distribution
- `test_full_release_workflow` – Complete release workflow

#### TestConfigurationIntegration

- `test_config_from_file` – Configuration from file
- `test_config_from_api` – Configuration from API
- `test_config_validation_flow` – Validation flow

#### TestErrorRecovery

- `test_error_handling_in_pipeline` – Error handling
- `test_rollback_on_error` – Error rollback

### test_config_integration.py – Configuration Integration

**Location:** `tests/integration/test_config_integration.py`

**Test Classes:**

#### TestConfigurationSources

- `test_yaml_config_loading` – YAML loading
- `test_json_config_loading` – JSON loading
- `test_config_merging` – Configuration merging

#### TestConfigurationPipeline

- `test_config_to_generation` – Config to generation
- `test_config_to_compilation` – Config to compilation

### test_compilation_integration.py – Compilation Pipeline Integration

**Location:** `tests/integration/test_compilation_integration.py`

**Test Classes:**

#### TestCompilationPipeline

- `test_pyinstaller_pipeline` – PyInstaller pipeline
- `test_cxfreeze_pipeline` – Cx_Freeze pipeline
- `test_compiler_switching` – Compiler switching

#### TestDependencyHandling

- `test_package_inclusion` – Package inclusion
- `test_package_exclusion` – Package exclusion
- `test_dependency_resolution` – Dependency resolution

---

## Robustness Tests

### test_error_handling.py – Error Handling

**Location:** `tests/robustness/test_error_handling.py`

**Test Classes:**

#### TestConfigurationErrors

- `test_invalid_version_format` – Invalid version
- `test_missing_required_fields` – Missing fields
- `test_invalid_paths` – Invalid paths

#### TestCompilationErrors

- `test_compilation_failure` – Compilation failure
- `test_invalid_compiler` – Invalid compiler
- `test_missing_main_file` – Missing main file

#### TestUploadErrors

- `test_upload_failure` – Upload failure
- `test_connection_error` – Connection error
- `test_authentication_error` – Authentication error

#### TestFileOperationErrors

- `test_file_write_error` – File write error
- `test_directory_creation_error` – Directory creation error
- `test_permission_error` – Permission error

### test_edge_cases.py – Edge Cases

**Location:** `tests/robustness/test_edge_cases.py`

**Test Classes:**

#### TestExtremeValues

- `test_very_long_project_name` – Long name
- `test_very_large_number_of_packages` – Many packages
- `test_very_deep_directory_structure` – Deep directories
- `test_very_large_files` – Large files

#### TestSpecialCharacters

- `test_unicode_in_config` – Unicode characters
- `test_special_chars_in_paths` – Special characters
- `test_spaces_in_names` – Spaces in names

#### TestConcurrency

- `test_parallel_compilations` – Parallel builds
- `test_concurrent_file_access` – Concurrent access

#### TestVersionEdgeCases

- `test_version_edge_formats` – Version formats
- `test_version_comparison` – Version comparison

---

## Test Configuration

### conftest.py – Shared Fixtures

**Location:** `tests/conftest.py`

**Fixtures:**

- `temp_dir` – Temporary directory for test files
- `temp_file` – Temporary file
- `config_file` – Temporary configuration file
- `sample_project` – Sample project structure
- `compiler_config` – Sample compiler configuration

**Pytest Hooks:**

- `pytest_runtest_teardown` – Test cleanup
- `pytest_runtest_makereport` – Test reporting

### run_tests.py – Test Runner

**Location:** `tests/run_tests.py`

**Features:**

- Test type selection (unit, integration, robustness, all)
- Coverage reporting
- Verbose mode
- Parallel execution
- Marker filtering

**Usage:**

```bash
python tests/run_tests.py --type unit --coverage --verbose
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
