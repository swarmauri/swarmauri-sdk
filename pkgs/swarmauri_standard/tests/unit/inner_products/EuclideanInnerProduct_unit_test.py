import logging

import numpy as np
import pytest

from swarmauri_standard.inner_products.EuclideanInnerProduct import (
    EuclideanInnerProduct,
)


@pytest.mark.unit
class TestEuclideanInnerProduct:
    """Unit tests for the EuclideanInnerProduct class."""

    @pytest.fixture
    def valid_vectors(self):
        """Fixture providing valid vector pairs for testing."""
        return (
            (np.array([1, 2, 3]), np.array([4, 5, 6])),
            (np.array([7, 8]), np.array([9, 10])),
            (np.array([11]), np.array([12])),
        )

    @pytest.fixture
    def invalid_vectors(self):
        """Fixture providing invalid vector pairs for testing."""
        return (
            (np.array([1, 2, 3]), np.array([4, 5])),
            (np.array([7, 8, 9]), np.array([10, 11, 12, 13])),
            (np.array([14, 15]), np.array([16])),
        )

    @pytest.fixture
    def non_real_vectors(self):
        """Fixture providing non-real vector pairs for testing."""
        return (
            (
                np.array([1 + 1j, 2 + 2j], dtype=np.complex64),
                np.array([3 + 3j, 4 + 4j]),
            ),
            (np.array([5, 6], dtype=np.complex128), np.array([7, 8])),
        )

    @pytest.fixture
    def callable_vectors(self):
        """Fixture providing callable vector pairs for testing."""

        def vec_a():
            return np.array([1, 2, 3])

        def vec_b():
            return np.array([4, 5, 6])

        return ((vec_a, vec_b),)

    @pytest.fixture
    def logger(self):
        """Fixture providing a logger instance."""
        return logging.getLogger(__name__)

    def test_compute_valid_inputs(self, valid_vectors):
        """Test the compute method with valid input vectors."""
        for a, b in valid_vectors:
            # Compute the expected result
            expected_result = np.dot(a, b)
            # Compute the actual result
            actual_result = EuclideanInnerProduct().compute(a, b)
            # Assert the results are equal
            assert actual_result == expected_result

    def test_compute_invalid_inputs(self, invalid_vectors):
        """Test the compute method with invalid input vectors."""
        for a, b in invalid_vectors:
            with pytest.raises(ValueError):
                EuclideanInnerProduct().compute(a, b)

    def test_compute_non_real_inputs(self, non_real_vectors):
        """Test the compute method with non-real input vectors."""
        for a, b in non_real_vectors:
            with pytest.raises(ValueError):
                EuclideanInnerProduct().compute(a, b)

    def test_compute_callable_inputs(self, callable_vectors):
        """Test the compute method with callable input vectors."""
        for a, b in callable_vectors:
            # Compute the expected result
            expected_result = np.dot(a(), b())
            # Compute the actual result
            actual_result = EuclideanInnerProduct().compute(a, b)
            # Assert the results are equal
            assert actual_result == expected_result

    def test_resource(self):
        """Test the resource property."""
        # Create an instance first
        instance = EuclideanInnerProduct()
        assert instance.resource == "InnerProduct"

    def test_type(self):
        """Test the type property."""
        # Create an instance first
        instance = EuclideanInnerProduct()
        assert instance.type == "EuclideanInnerProduct"

    def test_serialization(self):
        """Test model serialization and deserialization."""
        instance = EuclideanInnerProduct()
        # Serialize the model to JSON
        json_data = instance.model_dump_json()
        # Deserialize the JSON back
        deserialized = EuclideanInnerProduct.model_validate_json(json_data)
        # Assert the instances match
        assert deserialized == instance
