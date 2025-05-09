import pytest
import numpy as np
from swarmauri_standard.seminorms.CoordinateProjectionSeminorm import CoordinateProjectionSeminorm
from swarmauri_core.vectors.IVector import IVector

@pytest.mark.unit
class TestCoordinateProjectionSeminorm:
    """Unit tests for the CoordinateProjectionSeminorm class."""
    
    @pytest.fixture
    def coordinate_projection_seminorm(self):
        """Fixture providing a default instance of CoordinateProjectionSeminorm."""
        return CoordinateProjectionSeminorm()

    @pytest.mark.unit
    def test_init(self, coordinate_projection_seminorm):
        """Test initialization of the CoordinateProjectionSeminorm instance."""
        assert coordinate_projection_seminorm.projection_indices == []

    @pytest.mark.unit
    def test_compute_with_ivector(self, coordinate_projection_seminorm):
        """Test compute method with IVector input."""
        test_vector = IVector(data=np.array([1.0, 2.0, 3.0]))
        result = coordinate_projection_seminorm.compute(test_vector)
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_compute_with_projection_indices(self):
        """Test compute method with custom projection indices."""
        projection_indices = [0, 2]
        seminorm = CoordinateProjectionSeminorm(projection_indices=projection_indices)
        test_vector = IVector(data=np.array([4.0, 5.0, 6.0]))
        projected_vector = test_vector.data[projection_indices]
        expected_result = np.linalg.norm(projected_vector)
        result = seminorm.compute(test_vector)
        assert np.isclose(result, expected_result)

    @pytest.mark.unit
    def test_compute_with_non_ivector_input(coordinate_projection_seminorm):
        """Test compute method with non-IVector input."""
        test_input = "non_vector_input"
        with pytest.raises(NotImplementedError):
            coordinate_projection_seminorm.compute(test_input)

    @pytest.mark.unit
    def test_triangle_inequality(coordinate_projection_seminorm):
        """Test the triangle inequality property."""
        vector_a = IVector(data=np.array([1.0, 2.0]))
        vector_b = IVector(data=np.array([3.0, 4.0]))
        
        seminorm_a = coordinate_projection_seminorm.compute(vector_a)
        seminorm_b = coordinate_projection_seminorm.compute(vector_b)
        seminorm_a_plus_b = coordinate_projection_seminorm.compute(vector_a + vector_b)
        
        assert seminorm_a_plus_b <= seminorm_a + seminorm_b

    @pytest.mark.unit
    def test_scalar_homogeneity(coordinate_projection_seminorm):
        """Test the scalar homogeneity property."""
        test_vector = IVector(data=np.array([2.0, 4.0]))
        scalar = 3.0
        
        scaled_vector = scalar * test_vector
        seminorm_scaled = coordinate_projection_seminorm.compute(scaled_vector)
        seminorm_original = coordinate_projection_seminorm.compute(test_vector)
        
        assert np.isclose(seminorm_scaled, abs(scalar) * seminorm_original)

    @pytest.mark.unit
    def test_str_representation(coordinate_projection_seminorm):
        """Test string representation of the object."""
        expected_str = f"CoordinateProjectionSeminorm(projection_indices={coordinate_projection_seminorm.projection_indices})"
        assert str(coordinate_projection_seminorm) == expected_str

    @pytest.mark.unit
    def test_repr(coordinate_projection_seminorm):
        """Test official string representation of the object."""
        assert repr(coordinate_projection_seminorm) == str(coordinate_projection_seminorm)

    @pytest.mark.unit
    def test_compute_without_projection_indices():
        """Test compute method when no projection indices are specified."""
        seminorm = CoordinateProjectionSeminorm()
        test_vector = IVector(data=np.array([5.0, 6.0]))
        expected_result = np.linalg.norm(test_vector.data)
        result = seminorm.compute(test_vector)
        assert np.isclose(result, expected_result)