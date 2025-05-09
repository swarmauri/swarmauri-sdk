"""Unit tests for TraceFormWeightedInnerProduct module."""
import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.inner_products import TraceFormWeightedInnerProduct

@pytest.mark.unit
class TestTraceFormWeightedInnerProduct:
    """Unit tests for the TraceFormWeightedInnerProduct class."""

    @pytest.fixture
    def weight_matrix(self) -> np.ndarray:
        """Fixture providing a 2x2 identity matrix as weight matrix."""
        return np.identity(2)

    @pytest.fixture
    def trace_form(self, weight_matrix) -> TraceFormWeightedInnerProduct:
        """Fixture providing an instance of TraceFormWeightedInnerProduct."""
        return TraceFormWeightedInnerProduct(weight_matrix)

    def test_compute(self, trace_form) -> None:
        """Test the compute method with example matrices."""
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        result = trace_form.compute(a, b)
        
        # Expected result with identity weight matrix
        expected = np.trace(np.matmul(a, b))
        assert result == expected

    def test_compute_non_square(self, trace_form) -> None:
        """Test compute method with non-square matrices."""
        a = np.array([[1, 2, 3]])
        b = np.array([[4], [5], [6]])
        with pytest.raises(ValueError):
            trace_form.compute(a, b)

    def test_check_conjugate_symmetry(self, trace_form) -> None:
        """Test the conjugate symmetry check."""
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        
        inner_ab = trace_form.compute(a, b)
        inner_ba = trace_form.compute(b, a)
        
        assert np.isclose(inner_ab, inner_ba)

    def test_check_positivity(self, trace_form) -> None:
        """Test the positivity check."""
        # Positive definite matrix
        a = np.array([[2, 1], [1, 2]])
        result = trace_form.check_positivity(a)
        assert result

        # Non-positive definite matrix
        b = np.array([[1, 2], [3, 4]])
        result = trace_form.check_positivity(b)
        assert not result

    def test_init(self) -> None:
        """Test initialization with valid weight matrix."""
        weight = np.array([[1, 0], [0, 1]])
        instance = TraceFormWeightedInnerProduct(weight)
        assert isinstance(instance.weight_matrix, np.ndarray)

    def test_resource(self) -> None:
        """Test the resource class property."""
        assert TraceFormWeightedInnerProduct.resource == "Inner_product"

    def test_type(self) -> None:
        """Test the type class property."""
        assert TraceFormWeightedInnerProduct.type == "TraceFormWeightedInnerProduct"