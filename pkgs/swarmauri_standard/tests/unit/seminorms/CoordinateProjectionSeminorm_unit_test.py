import pytest
from swarmauri_standard.swarmauri_standard.seminorms.CoordinateProjectionSeminorm import CoordinateProjectionSeminorm
from typing import Sequence
import logging

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestCoordinateProjectionSeminorm:
    """Unit tests for CoordinateProjectionSeminorm class."""
    
    @pytest.fixture
    def valid_projection_indices(self) -> Sequence[int]:
        """Fixture for valid projection indices."""
        return (0, 1, 2)
    
    @pytest.fixture
    def invalid_projection_indices(self) -> Sequence[int]:
        """Fixture for invalid projection indices."""
        return (0, -1, 2)
    
    @pytest.fixture
    def duplicate_projection_indices(self) -> Sequence[int]:
        """Fixture for duplicate projection indices."""
        return (0, 1, 1)
    
    @pytest.fixture
    def non_integer_projection_indices(self) -> Sequence[float]:
        """Fixture for non-integer projection indices."""
        return (0.0, 1.0, 2.0)
    
    def test_init_valid(self, valid_projection_indices: Sequence[int]) -> None:
        """Test initialization with valid projection indices."""
        seminorm = CoordinateProjectionSeminorm(valid_projection_indices)
        assert seminorm.projection_indices == valid_projection_indices
        
    def test_init_invalid(self, invalid_projection_indices: Sequence[int]) -> None:
        """Test initialization with invalid projection indices."""
        with pytest.raises(ValueError):
            CoordinateProjectionSeminorm(invalid_projection_indices)
            
    def test_init_duplicates(self, duplicate_projection_indices: Sequence[int]) -> None:
        """Test initialization with duplicate projection indices."""
        with pytest.raises(ValueError):
            CoordinateProjectionSeminorm(duplicate_projection_indices)
            
    def test_init_non_integer(self, non_integer_projection_indices: Sequence[float]) -> None:
        """Test initialization with non-integer projection indices."""
        with pytest.raises(TypeError):
            CoordinateProjectionSeminorm(non_integer_projection_indices)
            
    @pytest.mark.parametrize("input_type,input_value,expected_result", [
        (list, [1, 2, 3], 3.7417),  # L2 norm of [1,2,3] is sqrt(14) ≈ 3.7417
        (tuple, (4, 5, 6), 8.77496),  # L2 norm of [4,5,6] is sqrt(77) ≈ 8.77496
        (list, [[1, 2], [3, 4]], 5.0)  # Matrix rows' L2 norms are sqrt(5) and sqrt(25), max is 5.0
    ])
    def test_compute(self, input_type: type, input_value: T, expected_result: float) -> None:
        """Test compute method with different input types."""
        seminorm = CoordinateProjectionSeminorm((0, 1))
        result = seminorm.compute(input_value)
        assert abs(result - expected_result) < 1e-4  # Allowing for floating point precision
        
    def test_compute_invalid_type(self) -> None:
        """Test compute with invalid input type."""
        seminorm = CoordinateProjectionSeminorm((0, 1))
        with pytest.raises(ValueError):
            seminorm.compute("invalid_type")
            
    def test_check_triangle_inequality(self) -> None:
        """Test triangle inequality check."""
        seminorm = CoordinateProjectionSeminorm((0, 1))
        a = [1, 2]
        b = [2, 3]
        assert seminorm.check_triangle_inequality(a, b) is True
        
    def test_check_scalar_homogeneity(self) -> None:
        """Test scalar homogeneity check."""
        seminorm = CoordinateProjectionSeminorm((0, 1))
        a = [1, 2]
        scalar = 2.0
        assert seminorm.check_scalar_homogeneity(a, scalar) is True
        
    def test_type(self) -> None:
        """Test type property."""
        assert CoordinateProjectionSeminorm.type == "CoordinateProjectionSeminorm"
        
    def test_resource(self) -> None:
        """Test resource property."""
        assert CoordinateProjectionSeminorm.resource == "seminorm"