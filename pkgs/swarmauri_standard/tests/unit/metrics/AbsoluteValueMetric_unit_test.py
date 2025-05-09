import pytest
from typing import Union, Sequence, Any
import logging
from swarmauri_standard.metrics import AbsoluteValueMetric

@pytest.mark.unit
class TestAbsoluteValueMetric:
    """Unit tests for the AbsoluteValueMetric class."""
    
    def test_init(self):
        """Test the initialization of AbsoluteValueMetric."""
        absolute_value = AbsoluteValueMetric()
        assert absolute_value.type == "AbsoluteValueMetric"

    @pytest.mark.unit
    def test_distance(self):
        """Test the distance method with various inputs."""
        absolute_value = AbsoluteValueMetric()
        
        # Test with positive numbers
        assert absolute_value.distance(5, 3) == 2
        # Test with negative numbers
        assert absolute_value.distance(-5, -3) == 2
        # Test with mixed signs
        assert absolute_value.distance(-5, 3) == 8
        # Test with zero
        assert absolute_value.distance(0, 5) == 5
        # Test with same values
        assert absolute_value.distance(5, 5) == 0

    @pytest.mark.unit
    def test_distances(self):
        """Test the distances method with single and multiple values."""
        absolute_value = AbsoluteValueMetric()
        
        # Test with single value
        assert absolute_value.distances(5, 3) == 2
        # Test with list of values
        assert absolute_value.distances(5, [3, 7, 5]) == [2, 2, 0]

    @pytest.mark.unit
    def test_check_non_negativity(self):
        """Test the non-negativity check."""
        absolute_value = AbsoluteValueMetric()
        # Test with positive distance
        assert absolute_value.check_non_negativity(5, 3) == True
        # Test with zero distance
        assert absolute_value.check_non_negativity(5, 5) == True
        # Test with negative values (should still return True due to absolute value)
        assert absolute_value.check_non_negativity(-5, -3) == True

    @pytest.mark.unit
    def test_check_identity(self):
        """Test the identity check."""
        absolute_value = AbsoluteValueMetric()
        # Test with identical values
        assert absolute_value.check_identity(5, 5) == True
        # Test with different values
        assert absolute_value.check_identity(5, 3) == False

    @pytest.mark.unit
    def test_check_symmetry(self):
        """Test the symmetry check."""
        absolute_value = AbsoluteValueMetric()
        # Test with commutative values
        assert absolute_value.check_symmetry(5, 3) == True
        # Test with negative values
        assert absolute_value.check_symmetry(-5, -3) == True
        # Test with mixed signs
        assert absolute_value.check_symmetry(-5, 3) == True

    @pytest.mark.unit
    def test_check_triangle_inequality(self):
        """Test the triangle inequality check."""
        absolute_value = AbsoluteValueMetric()
        # Test with valid triangle inequality
        assert absolute_value.check_triangle_inequality(1, 2, 3) == True
        # Test with edge case (1 + 2 = 3)
        assert absolute_value.check_triangle_inequality(1, 2, 3) == True
        # Test with negative values
        assert absolute_value.check_triangle_inequality(-1, -2, -3) == True

    @pytest.mark.unit
    def test_serialization(self):
        """Test the serialization and deserialization."""
        absolute_value = AbsoluteValueMetric()
        dumped_json = absolute_value.model_dump_json()
        assert absolute_value.model_validate_json(dumped_json) == absolute_value.id