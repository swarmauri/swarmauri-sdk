import pytest
import logging
import numpy as np

from swarmauri_standard.inner_products.TraceFormWeightedInnerProduct import (
    TraceFormWeightedInnerProduct,
)


@pytest.mark.unit
class TestTraceFormWeightedInnerProduct:
    """Unit tests for TraceFormWeightedInnerProduct class."""

    @pytest.fixture
    def valid_matrices(self):
        """Fixture providing valid matrix pairs for testing."""
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        return a, b

    @pytest.fixture
    def invalid_matrices(self):
        """Fixture providing invalid matrix pairs for testing."""
        a = np.array([[1, 2, 3], [4, 5, 6]])
        b = np.array([[7, 8], [9, 10], [11, 12]])
        return a, b

    @pytest.fixture
    def complex_matrices(self):
        """Fixture providing complex matrix pairs for testing."""
        a = np.array([[1 + 1j, 2 - 1j], [3 + 2j, 4 - 3j]])
        b = np.array([[5 + 6j, 7 - 8j], [9 + 10j, 11 - 12j]])
        return a, b

    @pytest.mark.unit
    def test_resource_attribute(self):
        """Test the resource attribute."""
        assert TraceFormWeightedInnerProduct.resource == "Inner_product"

    @pytest.mark.unit
    def test_type_attribute(self):
        """Test the type attribute."""
        assert TraceFormWeightedInnerProduct.type == "TraceFormWeightedInnerProduct"

    @pytest.mark.unit
    def test_compute_with_valid_matrices(self, valid_matrices):
        """Test compute method with valid matrices."""
        a, b = valid_matrices
        ip = TraceFormWeightedInnerProduct()
        result = ip.compute(a, b)
        assert isinstance(result, (float, complex))

    @pytest.mark.unit
    def test_compute_with_invalid_matrices(self, invalid_matrices):
        """Test compute method with invalid matrices."""
        a, b = invalid_matrices
        ip = TraceFormWeightedInnerProduct()
        with pytest.raises(ValueError):
            ip.compute(a, b)

    @pytest.mark.unit
    def test_check_conjugate_symmetry(self, valid_matrices, complex_matrices):
        """Test conjugate symmetry check."""
        a, b = valid_matrices
        ip = TraceFormWeightedInnerProduct()

        # Test with real matrices
        ab = ip.compute(a, b)
        ba = ip.compute(b, a)
        assert np.isclose(ab, ba)

        # Test with complex matrices
        a_complex, b_complex = complex_matrices
        ab_complex = ip.compute(a_complex, b_complex)
        ba_complex = ip.compute(b_complex, a_complex)
        assert np.isclose(ab_complex, np.conj(ba_complex))

    @pytest.mark.unit
    def test_check_linearity_first_argument(self, valid_matrices):
        """Test linearity in the first argument."""
        a, b = valid_matrices
        c = np.array([[1, 0], [0, 1]])  # Identity matrix
        ip = TraceFormWeightedInnerProduct()

        # Test addition
        ab = ip.compute(a + c, b)
        a_b = ip.compute(a, b)
        c_b = ip.compute(c, b)
        assert np.isclose(ab, a_b + c_b)

        # Test scalar multiplication
        k = 2.0
        ka_b = ip.compute(k * a, b)
        assert np.isclose(ka_b, k * a_b)

    @pytest.mark.unit
    def test_check_positivity(self):
        """Test positive definiteness."""
        a = np.array([[2, 1], [1, 2]])
        ip = TraceFormWeightedInnerProduct()
        result = ip.check_positivity(a)
        assert result

    @pytest.mark.unit
    def test_logging(self, caplog):
        """Test logging functionality."""
        with caplog.at_level(logging.DEBUG):
            ip = TraceFormWeightedInnerProduct()
            a = np.array([[1, 2], [3, 4]])
            b = np.array([[5, 6], [7, 8]])
            result = ip.compute(a, b)

            assert "Computing inner product" in caplog.text
            assert "Inner product result" in caplog.text
