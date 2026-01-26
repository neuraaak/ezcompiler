# ///////////////////////////////////////////////////////////////
# TEST INTEGRATION - Integration tests
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Integration tests for EzCompiler.

Tests the integration of multiple components working together.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from ezcompiler import EzCompiler

# ///////////////////////////////////////////////////////////////
# TESTS - EZCOMPILER INTEGRATION
# ///////////////////////////////////////////////////////////////


class TestEzCompilerIntegration:
    """Test EzCompiler integration with dependencies."""

    def test_ezcompiler_can_instantiate_with_logger(self) -> None:
        """Test that EzCompiler instantiates correctly with logger."""
        compiler = EzCompiler()
        assert compiler is not None
        assert compiler.logger is not None

    def test_multiple_instances_are_independent(self) -> None:
        """Test that multiple EzCompiler instances are independent."""
        compiler1 = EzCompiler()
        compiler2 = EzCompiler()
        assert compiler1 is not compiler2
        assert compiler1.logger is not compiler2.logger
