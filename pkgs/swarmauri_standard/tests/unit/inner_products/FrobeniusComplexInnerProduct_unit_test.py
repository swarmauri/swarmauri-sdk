"""Unit tests for FrobeniusComplexInnerProduct module."""
import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.inner_products import FrobeniusComplexInnerProduct

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

@pytest.mark.unit
class TestFrobeniusComplexInnerProduct:
    """Unit tests for FrobeniusComplexInnerProduct class."""
    
    @pytest.fixture
    def random_complex_matrix(self) -> np.ndarray:
        """Fixture providing a random complex matrix."""
        rng = np.random.default_rng()
        shape = (3, 3)
        matrix = rng.random(shape, dtype=np.complex64)
        return matrix
    
    @pytest.fixture
    def two_random_complex_matrices(self) -> tuple[np.ndarray, np.ndarray]:
        """Fixture providing two random complex matrices."""
        rng = np.random.default_rng()
        shape = (3, 3)
        matrix_a = rng.random(shape, dtype=np.complex64)
        matrix_b = rng.random(shape, dtype=np.complex64)
        return matrix_a, matrix_b
    
    @pytest.fixture
    def zero_complex_matrix(self) -> np.ndarray:
        """Fixture providing a zero complex matrix."""
        shape = (3, 3)
        return np.zeros(shape, dtype=np.complex64)
    
    @pytest.fixture
    def scalar(self) -> complex:
        """Fixture providing a random complex scalar."""
        rng = np.random.default_rng()
        return rng.random(1, dtype=np.complex64).item()
    
    def test_compute(self, random_complex_matrix, two_random_complex_matrices):
        """Test the compute method."""
        # Test with a single matrix
        a = random_complex_matrix
        fip = FrobeniusComplexInnerProduct()
        result = fip.compute(a, a)
        assert isinstance(result, float)
        
        # Test with two different matrices
        a, b = two_random_complex_matrices
        result_ab = fip.compute(a, b)
        result_ba = fip.compute(b, a)
        assert np.isclose(result_ab, result_ba.conjugate())
    
    def test_check_conjugate_symmetry(self, two_random_complex_matrices):
        """Test the conjugate symmetry check."""
        a, b = two_random_complex_matrices
        fip = FrobeniusComplexInnerProduct()
        is_symmetric = fip.check_conjugate_symmetry(a, b)
        assert is_symmetric
    
    def test_check_linearity(self, two_random_complex_matrices, scalar):
        """Test the linearity check."""
        a, b = two_random_complex_matrices
        c = scalar
        fip = FrobeniusComplexInnerProduct()
        is_linear = fip.check_linearity(a, b, c)
        assert is_linear
    
    def test_check_positivity(self, random_complex_matrix, zero_complex_matrix):
        """Test the positivity check."""
        fip = FrobeniusComplexInnerProduct()
        
        # Test with non-zero matrix
        a = random_complex_matrix
        is_positive = fip.check_positivity(a)
        assert is_positive
        
        # Test with zero matrix
        a = zero_complex_matrix
        is_positive = fip.check_positivity(a)
        assert not is_positive
    
    def test_invalid_input(self):
        """Test invalid input handling."""
        fip = FrobeniusComplexInnerProduct()
        with pytest.raises(ValueError):
            fip.compute("invalid", np.zeros((3,3), dtype=np.complex64))
    
    def test_serialization(self):
        """Test model serialization and validation."""
        fip = FrobeniusComplexInnerProduct()
        dumped = fip.model_dump_json()
        validated = FrobeniusComplexInnerProduct.model_validate_json(dumped)
        assert fip.id == validated.id