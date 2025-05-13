import logging

import numpy as np
import pytest

from swarmauri_standard.inner_products.TraceFormWeightedInnerProduct import (
    TraceFormWeightedInnerProduct,
)

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestTraceFormWeightedInnerProduct:
    """
    A test class for the TraceFormWeightedInnerProduct implementation.
    """

    @pytest.fixture
    def weight_matrix(self):
        """
        Provides a sample weight matrix for testing.
        """
        return np.array([[0.5, 0.0], [0.0, 1.0]])

    @pytest.fixture
    def instance(self, weight_matrix):
        """
        Provides a configured instance of TraceFormWeightedInnerProduct for testing.
        """
        return TraceFormWeightedInnerProduct(weight_matrix)

    @pytest.mark.unit
    def test_init(self, weight_matrix):
        """
        Tests the initialization of TraceFormWeightedInnerProduct.
        """
        # Test with valid weight matrix
        instance = TraceFormWeightedInnerProduct(weight_matrix)
        assert instance.weight is not None
        assert isinstance(instance.weight, np.ndarray)

        # Test with invalid weight
        with pytest.raises(ValueError):
            TraceFormWeightedInnerProduct("invalid_weight")

        # Test with valid but different shape
        different_weight = np.array([[1.0]])
        instance = TraceFormWeightedInnerProduct(different_weight)
        assert instance.weight.shape == (1, 1)

    @pytest.mark.unit
    def test_compute(self, instance):
        """
        Tests the compute method with various input types and shapes.
        """
        # Test with numpy arrays
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        result = instance.compute(a, b)
        assert isinstance(result, float)

        # Test with callable matrices
        def a_callable():
            return np.array([[1, 2], [3, 4]])

        def b_callable():
            return np.array([[5, 6], [7, 8]])

        result_callable = instance.compute(a_callable, b_callable)
        assert isinstance(result_callable, float)

    @pytest.mark.unit
    def test_compute_invalid_dimensions(self, instance):
        """
        Tests the compute method with incompatible matrix dimensions.
        """
        a = np.array([[1, 2]])
        b = np.array([[3], [4]])
        with pytest.raises(ValueError):
            instance.compute(a, b)

    @pytest.mark.unit
    def test_serialization(self, instance):
        """Tests the serialization and validation methods."""
        # Serialize the instance manually
        serialized_data = {
            "type": instance.type,
            "weight": instance.weight.tolist(),  # Convert numpy array to list
        }

        # Create a new instance from the serialized data
        new_instance = TraceFormWeightedInnerProduct(
            np.array(serialized_data["weight"])
        )

        # Compare values
        assert new_instance.type == instance.type
        assert np.array_equal(new_instance.weight, instance.weight)

    @pytest.mark.unit
    def test_getters(self, instance):
        """
        Tests the type and resource properties.
        """
        assert instance.type == "TraceFormWeightedInnerProduct"
        assert instance.resource == "InnerProduct"
