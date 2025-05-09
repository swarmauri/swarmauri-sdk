import pytest
from swarmauri_standard.swarmauri_standard.inner_products.WeightedL2InnerProduct import WeightedL2InnerProduct
import logging
from swarmauri_core.types import IVector
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestWeightedL2InnerProduct:
    """Unit tests for the WeightedL2InnerProduct class."""

    @pytest.fixture
    def default_weight_function(self) -> Callable[[IVector], IVector]:
        """Fixture providing a default weight function that returns 1 for all vectors."""
        def weight_function(x: IVector) -> IVector:
            return x.ones_like()
        return weight_function

    @pytest.fixture
    def test_vector(self) -> IVector:
        """Fixture providing a test vector for computations."""
        # Assuming IVector has a ones() method
        return IVector.ones(5)

    @pytest.fixture
    def invalid_weight_function(self) -> Callable[[IVector], IVector]:
        """Fixture providing a weight function that may return zero or negative weights."""
        def weight_function(x: IVector) -> IVector:
            return x.zeros_like()
        return weight_function

    def test_compute(self, default_weight_function, test_vector):
        """Test the compute method with valid inputs."""
        weighted_l2 = WeightedL2InnerProduct(default_weight_function)
        result = weighted_l2.compute(test_vector, test_vector)
        assert result > 0

    def test_compute_invalid_weights(self, invalid_weight_function, test_vector):
        """Test that compute raises ValueError with invalid weights."""
        weighted_l2 = WeightedL2InnerProduct(invalid_weight_function)
        with pytest.raises(ValueError):
            weighted_l2.compute(test_vector, test_vector)

    def test_check_conjugate_symmetry(self, default_weight_function, test_vector):
        """Test the check_conjugate_symmetry method."""
        weighted_l2 = WeightedL2InnerProduct(default_weight_function)
        is_symmetric = weighted_l2.check_conjugate_symmetry(test_vector, test_vector)
        assert is_symmetric

    def test_check_linearity_first_argument(self, default_weight_function, test_vector):
        """Test the check_linearity_first_argument method."""
        weighted_l2 = WeightedL2InnerProduct(default_weight_function)
        x = test_vector
        y = test_vector
        z = test_vector
        a = 2.0
        b = 3.0
        
        lhs = weighted_l2.compute(a * x + b * y, z)
        rhs = a * weighted_l2.compute(x, z) + b * weighted_l2.compute(y, z)
        
        assert lhs == rhs

    def test_check_positivity(self, default_weight_function, test_vector):
        """Test the check_positivity method."""
        weighted_l2 = WeightedL2InnerProduct(default_weight_function)
        is_positive = weighted_l2.check_positivity(test_vector)
        assert is_positive

    @pytest.mark.parametrize("weight_parameters,expected_result", [
        (None, None),
        ({"scale": 2.0}, {"scale": 2.0}),
        ({"offset": 1.0}, {"offset": 1.0}),
    ])
    def test_weight_parameters(self, default_weight_function, weight_parameters, expected_result):
        """Test that weight parameters are stored correctly."""
        weighted_l2 = WeightedL2InnerProduct(default_weight_function, weight_parameters)
        assert weighted_l2.weight_parameters == expected_result

__all__ = ["TestWeightedL2InnerProduct"]