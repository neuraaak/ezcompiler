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
from ezcompiler import EzCompiler

# ///////////////////////////////////////////////////////////////
# TESTS - EDGE CASES
# ///////////////////////////////////////////////////////////////


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_multiple_instantiations(self) -> None:
        """Test that multiple EzCompiler instances can be created."""
        instances = [EzCompiler() for _ in range(10)]
        assert len(instances) == 10
        # Verify all are different instances
        assert len({id(inst) for inst in instances}) == 10

    def test_ezcompiler_instance_not_none(self) -> None:
        """Test that EzCompiler instance is never None."""
        compiler = EzCompiler()
        assert compiler is not None

    def test_ezcompiler_attributes_accessible(self) -> None:
        """Test that EzCompiler attributes are accessible."""
        compiler = EzCompiler()
        # These should not raise AttributeError
        _ = compiler.logger
        _ = compiler.printer
        assert True
