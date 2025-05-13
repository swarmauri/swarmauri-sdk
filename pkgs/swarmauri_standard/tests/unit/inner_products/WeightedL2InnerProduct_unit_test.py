import logging

import numpy as np
import pytest

from swarmauri_standard.inner_products.WeightedL2InnerProduct import (
    WeightedL2InnerProduct,
)
from swarmauri_standard.vectors.Vector import Vector

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestWeightedL2InnerProduct:
    """Unit tests for WeightedL2InnerProduct class."""

    def setup_class(self):
        """Setup class-level resources."""

        def weight_function(x, *args):
            """Handle both scalar and array inputs."""

            # If first argument is self (the test class), use the second argument (from *args)
            if isinstance(x, TestWeightedL2InnerProduct):
                if args:  # If we have additional arguments
                    actual_x = args[0]  # This is the real input
                    if isinstance(actual_x, np.ndarray):
                        return np.square(actual_x) + 1
                    if hasattr(actual_x, "value"):
                        return np.square(np.array(actual_x.value)) + 1
                    return actual_x**2 + 1
                return 1  # Default value if no arguments

            # Normal case (not bound to self)
            if isinstance(x, np.ndarray):
                return np.square(x) + 1
            if hasattr(x, "value"):
                return np.square(np.array(x.value)) + 1
            return x**2 + 1

        self.weighted_l2 = WeightedL2InnerProduct(weight_function)
        self.test_weight_function = weight_function

    def test_init_with_valid_weight_function(self):
        """Test initialization with a valid weight function."""

        # Arrange
        def weight_func(x):
            return x**2 + 1  # Positive function

        # Act
        weighted_l2 = WeightedL2InnerProduct(weight_func)

        # Assert
        assert weighted_l2.weight_function is not None
        assert callable(weighted_l2.weight_function)

    def test_init_with_invalid_weight_function(self):
        """Test initialization with a weight function that can be zero or negative."""

        # Arrange
        def weight_func(x):
            return x**2 - 1  # Can be zero or negative

        # Act and Assert
        with pytest.raises(ValueError):
            WeightedL2InnerProduct(weight_func)

    def test_compute_with_numpy_arrays(self):
        """Test compute method with numpy arrays."""
        # Arrange
        a = np.array([1, 2])
        b = np.array([3, 4])
        expected = np.dot(
            a * np.sqrt(self.test_weight_function(a)),
            b * np.sqrt(self.test_weight_function(b)),
        )

        # Act
        result = self.weighted_l2.compute(a, b)

        # Assert
        assert np.allclose(result, expected, atol=1e-6)

    def test_compute_with_vectors(self):
        """Test compute method with Vector instances."""
        # Arrange
        a = Vector(value=[1, 2])
        b = Vector(value=[3, 4])

        # Convert to numpy arrays for calculation
        a_array = a.to_numpy()
        b_array = b.to_numpy()

        expected = np.dot(
            a_array * np.sqrt(self.test_weight_function(a_array)),
            b_array * np.sqrt(self.test_weight_function(b_array)),
        )

        # Act
        result = self.weighted_l2.compute(a, b)

        # Assert
        assert np.allclose(result, expected, atol=1e-6)

    def test_compute_with_callables(self):
        """Test compute method with callable functions."""

        # Arrange
        def a(x):
            return x

        def b(x):
            return x**2

        # Use the same grid and calculation as in the implementation
        x_grid = np.linspace(0, 1, 100)  # Same grid as in implementation
        a_values = np.array([a(x) for x in x_grid])
        b_values = np.array([b(x) for x in x_grid])

        weighted_a = a_values * np.sqrt(self.test_weight_function(a_values))
        weighted_b = b_values * np.sqrt(self.test_weight_function(b_values))
        expected = np.dot(weighted_a, weighted_b)

        # Act
        result = self.weighted_l2.compute(a, b)

        # Assert
        assert np.allclose(result, expected, atol=1e-6)

    def test_serialization(self):
        """Test serialization and deserialization."""
        # Act
        instance = WeightedL2InnerProduct(self.test_weight_function)
        dumped_json = instance.model_dump_json()
        validated = instance.model_validate_json(dumped_json)

        # Assert
        assert instance.id == validated.id

    def test_str_representation(self):
        """Test string representation."""
        # Act
        str_repr = str(self.weighted_l2)

        # Assert
        assert str_repr.startswith("WeightedL2InnerProduct")
        assert "weight_function" in str_repr
