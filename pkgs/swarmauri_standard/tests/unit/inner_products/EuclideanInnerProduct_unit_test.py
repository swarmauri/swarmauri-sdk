import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.inner_products.EuclideanInnerProduct import (
    EuclideanInnerProduct,
)

# Set up logging
logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestEuclideanInnerProduct:
    """
    Unit tests for the EuclideanInnerProduct class.

    This class provides comprehensive unit tests for the EuclideanInnerProduct
    implementation. It verifies the correctness of the inner product computation,
    as well as the mathematical properties required for an inner product (symmetry,
    linearity, and positivity).
    """

    @pytest.fixture
    def vectors(self):
        """
        Fixture providing test vectors for inner product computation.

        Returns:
            tuple: Two real-valued vectors (numpy arrays)
        """
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([4.0, 5.0, 6.0])
        return a, b

    @pytest.mark.unit
    def test_compute(self, vectors):
        """
        Tests the compute method of the EuclideanInnerProduct class.

        Verifies that the inner product (dot product) is computed correctly
        for valid input vectors. Also tests edge cases with empty vectors
        and zero vectors.
        """
        a, b = vectors

        # Test with numpy arrays
        result_np = EuclideanInnerProduct().compute(a, b)
        expected_np = np.dot(a, b)
        assert np.isclose(result_np, expected_np)

        # Test with lists
        a_list = a.tolist()
        b_list = b.tolist()
        result_list = EuclideanInnerProduct().compute(a_list, b_list)
        assert np.isclose(result_list, expected_np)

        # Test edge case: empty vectors
        empty = np.array([])
        with pytest.raises(ValueError):
            EuclideanInnerProduct().compute(empty, empty)

        # Test edge case: zero vectors
        zero_a = np.zeros(3)
        zero_b = np.zeros(3)
        result_zero = EuclideanInnerProduct().compute(zero_a, zero_b)
        assert result_zero == 0.0

        # Test incompatible dimensions
        a_2d = np.array([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError):
            EuclideanInnerProduct().compute(a_2d, b)

    @pytest.mark.unit
    def test_check_conjugate_symmetry(self, vectors):
        """
        Tests the conjugate symmetry property of the inner product.

        For real-valued vectors, the inner product should be symmetric,
        i.e., compute(a, b) = compute(b, a).
        """
        a, b = vectors

        inner_product = EuclideanInnerProduct()
        symmetry_ab = inner_product.check_conjugate_symmetry(a, b)
        symmetry_ba = inner_product.check_conjugate_symmetry(b, a)

        assert symmetry_ab
        assert symmetry_ba

        # Test with zero vectors
        zero_a = np.zeros(3)
        zero_b = np.zeros(3)
        symmetry_zero = inner_product.check_conjugate_symmetry(zero_a, zero_b)
        assert symmetry_zero

    @pytest.mark.unit
    def test_check_linearity_first_argument(self, vectors):
        """
        Tests the linearity of the inner product in the first argument.

        Verifies that the inner product satisfies both additivity and
        homogeneity in the first argument.
        """
        a, b = vectors
        c = np.array([7.0, 8.0, 9.0])

        inner_product = EuclideanInnerProduct()

        # Test additivity: compute(a + c, b) = compute(a, b) + compute(c, b)
        ab = inner_product.compute(a, b)
        cb = inner_product.compute(c, b)
        ab_plus_cb = inner_product.compute(a + c, b)
        assert np.isclose(ab + cb, ab_plus_cb)

        # Test homogeneity: compute(k * a, b) = k * compute(a, b)
        k = 2.0
        k_ab = inner_product.compute(k * a, b)
        k_times_ab = k * ab
        assert np.isclose(k_ab, k_times_ab)

        # Test with zero vectors
        zero_a = np.zeros(3)
        zero_c = np.zeros(3)
        ab_zero = inner_product.compute(zero_a, b)
        cb_zero = inner_product.compute(zero_c, b)
        assert ab_zero == 0.0
        assert cb_zero == 0.0

    @pytest.mark.unit
    def test_check_positivity(self):
        """
        Tests the positivity of the inner product.

        The inner product of any non-zero vector with itself should be positive.
        """
        inner_product = EuclideanInnerProduct()

        # Test with non-zero vector
        a = np.array([1.0, 2.0, 3.0])
        is_positive = inner_product.check_positivity(a)
        assert is_positive

        # Test with zero vector
        zero_a = np.zeros(3)
        is_positive_zero = inner_product.check_positivity(zero_a)
        assert not is_positive_zero

        # Test with negative vector (should still be positive definite)
        negative_a = np.array([-1.0, -2.0, -3.0])
        is_positive_negative = inner_product.check_positivity(negative_a)
        assert is_positive_negative
