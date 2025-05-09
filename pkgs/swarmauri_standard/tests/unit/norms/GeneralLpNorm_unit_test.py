import pytest
from swarmauri_standard.swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestGeneralLpNorm:
    """Unit tests for the GeneralLpNorm class implementation."""

    @pytest.fixture
    def norm_instance(self):
        """Fixture to provide a GeneralLpNorm instance with valid parameters."""
        return GeneralLpNorm(p=2.0)

    @pytest.mark.unit
    def test_constructor_valid_input(self):
        """Test initialization with valid p values."""
        # Test with p=2.0 (valid)
        norm = GeneralLpNorm(p=2.0)
        assert norm.p == 2.0

        # Test with p=1.5 (valid)
        norm = GeneralLpNorm(p=1.5)
        assert norm.p == 1.5

        # Test with p= float('inf') (invalid)
        with pytest.raises(ValueError):
            GeneralLpNorm(p=float("inf"))

        # Test with p=1.0 (invalid)
        with pytest.raises(ValueError):
            GeneralLpNorm(p=1.0)

        # Test with p=-2.0 (invalid)
        with pytest.raises(ValueError):
            GeneralLpNorm(p=-2.0)

        # Test with p as non-float (invalid)
        with pytest.raises(ValueError):
            GeneralLpNorm(p="2.0")

    @pytest.mark.unit
    def test_compute_vector(self, norm_instance):
        """Test compute method with vector input."""
        # Test with positive numbers
        x = [1.0, 2.0, 3.0]
        expected_norm = (1**2 + 2**2 + 3**2) ** 0.5  # Since p=2
        assert abs(norm_instance.compute(x) - expected_norm) < 1e-9

        # Test with zero vector
        x = [0.0, 0.0, 0.0]
        assert norm_instance.compute(x) == 0.0

        # Test with negative numbers
        x = [-1.0, -2.0, -3.0]
        expected_norm = (1**2 + 2**2 + 3**2) ** 0.5  # Absolute values
        assert abs(norm_instance.compute(x) - expected_norm) < 1e-9

    @pytest.mark.unit
    def test_compute_matrix(self, norm_instance):
        """Test compute method with matrix input."""
        x = [[1.0, 2.0], [3.0, 4.0]]  # 2x2 matrix
        row1_norm = (1**2 + 2**2) ** 0.5
        row2_norm = (3**2 + 4**2) ** 0.5
        expected_norm = max(row1_norm, row2_norm)
        assert abs(norm_instance.compute(x) - expected_norm) < 1e-9

    @pytest.mark.unit
    def test_compute_callable(self, norm_instance):
        """Test compute method with callable input."""

        # Test with callable that returns a vector
        def vector_callable():
            return [1.0, 2.0, 3.0]

        expected_norm = (1**2 + 2**2 + 3**2) ** 0.5
        assert abs(norm_instance.compute(vector_callable) - expected_norm) < 1e-9

        # Test with invalid callable (returns string)
        def invalid_callable():
            return "string"

        with pytest.raises(ValueError):
            norm_instance.compute(invalid_callable)

    @pytest.mark.unit
    def test_check_non_negativity(self, norm_instance):
        """Test non-negativity property."""
        # Test with positive vector
        x = [1.0, 2.0, 3.0]
        norm = norm_instance.compute(x)
        assert norm >= 0

        # Test with zero vector
        x = [0.0, 0.0, 0.0]
        norm = norm_instance.compute(x)
        assert norm == 0.0

        # Test with negative vector
        x = [-1.0, -2.0, -3.0]
        norm = norm_instance.compute(x)
        assert norm >= 0

    @pytest.mark.unit
    def test_check_triangle_inequality(self, norm_instance):
        """Test triangle inequality property."""
        # Test with two vectors in R^2
        x = [1.0, 2.0]
        y = [3.0, 4.0]
        norm_x = norm_instance.compute(x)
        norm_y = norm_instance.compute(y)
        combined = [4.0, 6.0]
        norm_combined = norm_instance.compute(combined)
        assert norm_combined <= norm_x + norm_y

    @pytest.mark.unit
    def test_check_absolute_homogeneity(self, norm_instance):
        """Test absolute homogeneity property."""
        # Test with scaling factor 2.0
        x = [1.0, 2.0, 3.0]
        alpha = 2.0
        scaled_x = [2.0, 4.0, 6.0]
        norm_x = norm_instance.compute(x)
        norm_scaled = norm_instance.compute(scaled_x)
        assert abs(norm_scaled - abs(alpha) * norm_x) < 1e-9

        # Test with negative scaling factor
        alpha = -2.0
        scaled_x = [-2.0, -4.0, -6.0]
        norm_scaled = norm_instance.compute(scaled_x)
        assert abs(norm_scaled - abs(alpha) * norm_x) < 1e-9

    @pytest.mark.unit
    def test_check_definiteness(self, norm_instance):
        """Test definiteness property."""
        # Test with zero vector
        x = [0.0, 0.0, 0.0]
        norm = norm_instance.compute(x)
        assert norm == 0.0

        # Test with non-zero vector
        x = [1.0, 2.0, 3.0]
        norm = norm_instance.compute(x)
        assert norm > 0.0
