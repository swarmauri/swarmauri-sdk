import pytest
import numpy as np
import logging

from swarmauri_standard.inner_products.FrobeniusComplexInnerProduct import FrobeniusComplexInnerProduct

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestFrobeniusComplexInnerProduct:
    """Unit tests for FrobeniusComplexInnerProduct class."""

    def test_compute(self):
        """Test computation of Frobenius inner product for complex matrices."""
        # Generate random complex matrices
        a = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
        b = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)

        # Compute using class method
        inner_product = FrobeniusComplexInnerProduct()
        result = inner_product.compute(a, b)

        # Manual computation for verification
        b_conj_transpose = b.conj().T
        product = np.multiply(a, b_conj_transpose)
        expected_result = np.trace(product)

        # Assert results are close (floating point comparison)
        assert np.isclose(result, expected_result, rtol=1e-4)

    def test_check_conjugate_symmetry(self):
        """Test conjugate symmetry property."""
        a = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
        b = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)

        inner_product = FrobeniusComplexInnerProduct()
        inner_ab = inner_product.compute(a, b)
        inner_ba = inner_product.compute(b, a)

        # Check if inner_ab is close to the conjugate of inner_ba
        assert np.isclose(inner_ab, inner_ba.conjugate(), rtol=1e-4)

    def test_check_linearity_first_argument(self):
        """Test linearity in the first argument."""
        a = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
        b = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
        c = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)

        inner_product = FrobeniusComplexInnerProduct()

        # Test linearity: <a + b, c> = <a, c> + <b, c>
        ab = a + b
        inner_ab_c = inner_product.compute(ab, c)
        inner_a_c = inner_product.compute(a, c)
        inner_b_c = inner_product.compute(b, c)

        assert np.isclose(inner_ab_c, inner_a_c + inner_b_c, rtol=1e-4)

        # Test homogeneity: <αa, c> = α <a, c>
        alpha = 2.0
        a_scaled = alpha * a
        inner_scaled = inner_product.compute(a_scaled, c)
        expected = alpha * inner_a_c

        assert np.isclose(inner_scaled, expected, rtol=1e-4)

    def test_check_positivity(self):
        """Test positivity property."""
        a = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
        a = a @ a.conj().T  # Ensure a is positive definite

        inner_product = FrobeniusComplexInnerProduct()
        inner_aa = inner_product.compute(a, a)

        assert inner_aa > 0

    @pytest.mark.parametrize("matrix_size", [(2, 2), (3, 3)])
    def test_compute_parameterized(self, matrix_size):
        """Parameterized test for compute method with different matrix sizes."""
        a = np.random.rand(*matrix_size) + 1j * np.random.rand(*matrix_size)
        b = np.random.rand(*matrix_size) + 1j * np.random.rand(*matrix_size)

        inner_product = FrobeniusComplexInnerProduct()
        result = inner_product.compute(a, b)

        b_conj_transpose = b.conj().T
        product = np.multiply(a, b_conj_transpose)
        expected_result = np.trace(product)

        assert np.isclose(result, expected_result, rtol=1e-4)

    @pytest.mark.parametrize("matrix_type", ['complex', 'real'])
    def test_compute_different_types(self, matrix_type):
        """Test compute method with different matrix types."""
        if matrix_type == 'complex':
            a = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
            b = np.random.rand(2, 2) + 1j * np.random.rand(2, 2)
        else:
            a = np.random.rand(2, 2)
            b = np.random.rand(2, 2)

        inner_product = FrobeniusComplexInnerProduct()
        result = inner_product.compute(a, b)

        b_conj_transpose = b.conj().T
        product = np.multiply(a, b_conj_transpose)
        expected_result = np.trace(product)

        assert np.isclose(result, expected_result, rtol=1e-4)

def _generate_random_matrices():
    """Fixture to generate random matrices for testing."""
    matrix_size = (2, 2)
    a = np.random.rand(*matrix_size) + 1j * np.random.rand(*matrix_size)
    b = np.random.rand(*matrix_size) + 1j * np.random.rand(*matrix_size)
    return a, b

@pytest.mark.unit
def test_compute_with_fixture(_generate_random_matrices):
    """Test compute method using fixture-generated matrices."""
    a, b = _generate_random_matrices

    inner_product = FrobeniusComplexInnerProduct()
    result = inner_product.compute(a, b)

    b_conj_transpose = b.conj().T
    product = np.multiply(a, b_conj_transpose)
    expected_result = np.trace(product)

    assert np.isclose(result, expected_result, rtol=1e-4)