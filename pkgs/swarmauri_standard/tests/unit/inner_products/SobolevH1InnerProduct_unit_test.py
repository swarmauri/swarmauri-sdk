import pytest
import numpy as np
from swarmauri_standard.inner_products.SobolevH1InnerProduct import (
    SobolevH1InnerProduct,
)
from swarmauri_core.vectors.IVector import IVector
import logging

logger = logging.getLogger(__name__)


class TestSobolevH1InnerProduct:
    """Unit tests for SobolevH1InnerProduct class."""

    @pytest.fixture
    def base_class(self):
        """Fixture providing the base class for testing."""
        return SobolevH1InnerProduct()

    @pytest.mark.unit
    def test_compute_callable_inputs(self, base_class):
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
        result = base_class.compute(f, g)

        # Verify result is a float
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_compute_array_inputs(self, base_class):
        """
        Tests compute method with numpy array inputs.

        Verify that the compute method correctly handles numpy array inputs
        and computes the Sobolev H1 inner product.
        """
        # Generate test arrays
        a = np.linspace(0, 1, 100)
        b = np.linspace(0, 1, 100)

        # Compute inner product
        result = base_class.compute(a, b)

        # Verify result is a float
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_compute_vector_inputs(self, base_class):
        """
        Tests compute method with vector inputs.

        Verify that the compute method correctly handles vector inputs
        and computes the Sobolev H1 inner product.
        """

        # Create mock vector objects
        class MockVector(IVector):
            def __init__(self, data):
                self.data = data
                self.grad = np.zeros_like(data)

        a = MockVector(np.linspace(0, 1, 100))
        b = MockVector(np.linspace(0, 1, 100))

        # Compute inner product
        result = base_class.compute(a, b)

        # Verify result is a float
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_class_attributes(self, base_class):
        """
        Tests class attributes.

        Verify that the class has the correct type and resource attributes.
        """
        assert base_class.type == "SobolevH1InnerProduct"
        assert base_class.resource == "Inner_product"

    @pytest.mark.unit
    def test_invalid_input_types(self, base_class):
        """
        Tests handling of invalid input types.

        Verify that the compute method raises ValueError
        when given unsupported input types.
        """
        with pytest.raises(ValueError):
            base_class.compute(123, 456)

    @pytest.mark.unit
    def test_mismatched_dimensions(self, base_class):
        """
        Tests handling of mismatched dimensions.

        Verify that the compute method raises ValueError
        when input arrays have mismatched dimensions.
        """
        a = np.linspace(0, 1, 100)
        b = np.linspace(0, 1, 200)

        with pytest.raises(ValueError):
            base_class.compute(a, b)

    @pytest.mark.unit
    def test_logging(self, base_class, caplog):
        """
        Tests logging functionality.

        Verify that the compute method logs debug messages
        during execution.
        """
        with caplog.at_level(logging.DEBUG):
            base_class.compute(lambda x: x, lambda x: x)

        assert "Computing Sobolev H1 inner product" in caplog.text


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (lambda x: x, lambda x: x, 2.0),
        (np.array([1, 2]), np.array([3, 4]), 2.5),
    ],
)
@pytest.mark.unit
def test_compute_multiple_cases(a, b, expected, base_class):
    """
    Tests compute method with multiple input types and expected results.

    Parameterized test to verify compute method with different combinations
    of input types and expected results.
    """
    result = base_class.compute(a, b)
    assert result == expected
