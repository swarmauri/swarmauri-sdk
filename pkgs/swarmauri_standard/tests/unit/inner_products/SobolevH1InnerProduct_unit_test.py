import logging

import numpy as np
import pytest

from swarmauri_standard.inner_products.SobolevH1InnerProduct import (
    SobolevH1InnerProduct,
)
from swarmauri_standard.vectors.Vector import Vector

logger = logging.getLogger(__name__)


class TestSobolevH1InnerProduct:
    """Unit tests for SobolevH1InnerProduct class."""

    @pytest.fixture
    def sobolev_instance(self):
        """Fixture providing a SobolevH1InnerProduct instance."""
        return SobolevH1InnerProduct()

    @pytest.mark.unit
    def test_compute_callable_inputs(self, sobolev_instance):
        """
        Tests compute method with callable inputs.

        Verify that the compute method correctly handles callable functions
        and computes the Sobolev H1 inner product.
        """

        # Define test functions
        def f(x):
            return x

        def g(x):
            return x

        # Compute inner product
        result = sobolev_instance.compute(f, g)

        # Verify result is a float
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_compute_array_inputs(self, sobolev_instance):
        """
        Tests compute method with numpy array inputs.

        Verify that the compute method correctly handles numpy array inputs
        and computes the Sobolev H1 inner product.
        """
        # Generate test arrays
        a = np.linspace(0, 1, 100)
        b = np.linspace(0, 1, 100)

        # Compute inner product
        result = sobolev_instance.compute(a, b)

        # Verify result is a float
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_compute_vector_inputs(self, sobolev_instance):
        """
        Tests compute method with vector inputs.

        Verify that the compute method correctly handles vector inputs
        and computes the Sobolev H1 inner product.
        """
        # Create Vector instances directly
        data_a = [0, 1, 100]
        data_b = [0, 1, 100]

        # Initialize Vector objects with proper data
        a = Vector(value=data_a, grad=np.zeros_like(data_a))
        b = Vector(value=data_b, grad=np.zeros_like(data_b))

        # Compute inner product
        result = sobolev_instance.compute(a, b)

        # Verify result is a float
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_class_attributes(self, sobolev_instance):
        """
        Tests class attributes.

        Verify that the class has the correct type and resource attributes.
        """
        assert sobolev_instance.type == "SobolevH1InnerProduct"
        assert sobolev_instance.resource == "InnerProduct"

    @pytest.mark.unit
    def test_invalid_input_types(self, sobolev_instance):
        """
        Tests handling of invalid input types.

        Verify that the compute method raises ValueError
        when given unsupported input types.
        """
        with pytest.raises(ValueError):
            sobolev_instance.compute(123, 456)

    @pytest.mark.unit
    def test_mismatched_dimensions(self, sobolev_instance):
        """
        Tests handling of mismatched dimensions.

        Verify that the compute method raises ValueError
        when input arrays have mismatched dimensions.
        """
        a = np.linspace(0, 1, 100)
        b = np.linspace(0, 1, 200)

        with pytest.raises(ValueError):
            sobolev_instance.compute(a, b)

    @pytest.mark.unit
    def test_logging(self, sobolev_instance, caplog):
        """
        Tests logging functionality.

        Verify that the compute method logs debug messages
        during execution.
        """
        with caplog.at_level(logging.DEBUG):
            sobolev_instance.compute(lambda x: x, lambda x: x)

        assert "Computing Sobolev H1 inner product" in caplog.text


@pytest.fixture
def sobolev_h1():
    """Module-level fixture providing a SobolevH1InnerProduct instance."""
    return SobolevH1InnerProduct()


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (lambda x: x, lambda x: x, 333.5),
        (np.array([1, 2]), np.array([3, 4]), 11.0),
    ],
)
@pytest.mark.unit
def test_compute_multiple_cases(a, b, expected, sobolev_h1):  # Changed fixture name
    """Tests compute method with multiple input types."""
    result = sobolev_h1.compute(a, b)
    assert result == pytest.approx(expected, abs=0.1)
