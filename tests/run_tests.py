#!/usr/bin/env python
# ///////////////////////////////////////////////////////////////
# RUN_TESTS - Test runner script
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Test runner script for EzCompiler.

Provides a convenient CLI wrapper around pytest for executing different
types of tests (unit, integration, robustness) with various configurations.

Supports:
    - Running specific test types or all tests
    - Coverage reporting
    - Verbose output
    - Parallel execution via pytest-xdist
    - Marker-based filtering
    - Fast mode (excluding slow tests)

Example:
    python run_tests.py --type unit --verbose --coverage
    python run_tests.py --type all --parallel
    python run_tests.py --marker integration --fast
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import argparse
import subprocess
import sys
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS
# ///////////////////////////////////////////////////////////////


def run_command(cmd: list[str], description: str) -> bool:
    """
    Execute a shell command and display output in real-time.

    Runs a command using subprocess with output displayed directly to the console
    without buffering. This provides real-time feedback during test execution.

    Args:
        cmd: Command and arguments as list of strings
        description: Human-readable description of what's running

    Returns:
        bool: True if command succeeded (exit code 0), False otherwise

    Note:
        Uses S603 security rule bypass for subprocess.run() since this is
        a test runner with trusted input.
    """
    print(f"\n{'=' * 60}")
    print(f"🚀 {description}")
    print(f"{'=' * 60}")
    try:
        # Run without capturing output - displays in real-time
        result = subprocess.run(cmd, check=False)  # noqa: S603
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False


# ///////////////////////////////////////////////////////////////
# MAIN FUNCTION
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """
    Main entry point for the test runner.

    Parses CLI arguments and executes pytest with appropriate configuration.
    Validates that pyproject.toml exists before running tests.

    Exit codes:
        0: All tests passed
        1: Tests failed or pyproject.toml not found
    """
    parser = argparse.ArgumentParser(
        description="Test runner for EzCompiler with flexible configuration"
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "robustness", "all"],
        default="unit",
        help="Test type to run (default: unit)",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report (HTML + terminal)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output (shows each test)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Exclude slow tests (deselect with 'slow' marker)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel using pytest-xdist",
    )
    parser.add_argument(
        "--marker",
        type=str,
        help="Run only tests with specific marker (e.g., integration, robustness)",
    )
    args = parser.parse_args()

    # Validate project structure
    if not Path("pyproject.toml").exists():
        print(
            "❌ Error: pyproject.toml not found. Run this script from the project root."
        )
        sys.exit(1)

    # Build pytest command
    cmd_parts = [sys.executable, "-m", "pytest"]

    # Add verbosity flag
    if args.verbose:
        cmd_parts.append("-v")

    # Add marker-based filtering
    if args.fast:
        cmd_parts.extend(["-m", "not slow"])
    if args.marker:
        cmd_parts.extend(["-m", args.marker])

    # Add parallel execution
    if args.parallel:
        cmd_parts.extend(["-n", "auto"])

    # Add test path based on type
    if args.type == "unit":
        cmd_parts.append("tests/unit/")
    elif args.type == "integration":
        cmd_parts.append("tests/integration/")
    elif args.type == "robustness":
        cmd_parts.append("tests/robustness/")
    else:
        cmd_parts.append("tests/")

    # Add coverage options
    if args.coverage:
        cmd_parts.extend(
            [
                "--cov=ezcompiler",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
            ]
        )

    # Execute tests
    success = run_command(cmd_parts, f"Running {args.type} tests")

    # Display results
    if success:
        print("\n✅ Tests passed successfully!")
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/")
            print("   Open htmlcov/index.html in your browser")
    else:
        print("\n❌ Tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
