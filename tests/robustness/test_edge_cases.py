# ///////////////////////////////////////////////////////////////
# TEST EDGE CASES - Robustness tests for edge cases
# Project: ezcompiler
# ///////////////////////////////////////////////////////////////

"""
Robustness tests for edge cases and unusual scenarios.

Tests behavior in edge cases and boundary conditions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
import pytest

from ezcompiler import EzCompiler

pytestmark = pytest.mark.robustness

# ///////////////////////////////////////////////////////////////
# TESTS - EDGE CASES
# ///////////////////////////////////////////////////////////////


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_should_create_independent_instances_when_multiple_are_instantiated(
        self,
    ) -> None:
        """Test that multiple EzCompiler instances can be created."""
        instances = [EzCompiler() for _ in range(10)]
        assert len(instances) == 10
        assert len({id(inst) for inst in instances}) == 10

    def test_should_not_be_none_when_ezcompiler_is_instantiated(self) -> None:
        """Test that EzCompiler instance is never None."""
        compiler = EzCompiler()
        assert compiler is not None

    def test_should_expose_attributes_when_ezcompiler_is_instantiated(self) -> None:
        """Test that EzCompiler attributes are accessible."""
        compiler = EzCompiler()
        _ = compiler.logger
        _ = compiler.printer
        assert True
