import pytest
from unittest.mock import patch
import logging
from swarmauri_standard.pseudometrics.ProjectionPseudometricR2 import ProjectionPseudometricR2

@pytest.mark.unit
class TestProjectionPseudometricR2:
    """
    Unit test class for ProjectionPseudometricR2.
    
    This class provides comprehensive unit tests for the ProjectionPseudometricR2
    class, ensuring all functionality works as expected.
    """

    @pytest.fixture
    def projection_pseudometric(self):
        """
        Fixture to provide a default instance of ProjectionPseudometricR2.
        
        Returns:
            ProjectionPseudometricR2:
                An instance of ProjectionPseudometricR2 with default axis='x'
        """
        return ProjectionPseudometricR2()

    @pytest.mark.unit
    def test_resource_type(self, projection_pseudometric):
        """
        Test the resource type of the pseudometric.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
        """
        assert projection_pseudometric.resource == "Pseudometric"

    @pytest.mark.unit
    def test_axis_initialization(self):
        """
        Test initialization with different axis values.
        """
        # Test valid axis values
        projection_x = ProjectionPseudometricR2(axis="x")
        projection_y = ProjectionPseudometricR2(axis="y")
        
        assert projection_x.axis == "x"
        assert projection_y.axis == "y"
        
        # Test invalid axis value
        with pytest.raises(ValueError):
            ProjectionPseudometricR2(axis="z")

    @pytest.mark.unit
    @patch('logging.getLogger')
    def test_logging_initialization(self, mock_logger, projection_pseudometric):
        """
        Test logging during initialization.
        
        Args:
            mock_logger: Mock
                Mocked logging.getLogger for verification
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
        """
        # Verify debug message was logged during initialization
        mock_logger.return_value.debug.assert_called_once_with(
            f"Initialized ProjectionPseudometricR2 with axis={projection_pseudometric.axis}"
        )

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y,expected_distance", [
        ((0, 0), (0, 0), 0),  # Same point
        ((1, 2), (3, 4), 2),  # Distance on x-axis
        ((1, 2), (1, 4), 0),  # Same x-coordinate
        ((1, 2), (3, 2), 2),  # Same y-coordinate
    ])
    def test_distance(self, projection_pseudometric, x, y, expected_distance):
        """
        Test distance calculation between two points.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
            x: tuple
                First point coordinates
            y: tuple
                Second point coordinates
            expected_distance: float
                Expected distance value
        """
        assert projection_pseudometric.distance(x, y) == expected_distance

    @pytest.mark.unit
    def test_distance_invalid_input(self, projection_pseudometric):
        """
        Test distance calculation with invalid input.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
        """
        with pytest.raises(ValueError):
            projection_pseudometric.distance("invalid", (0, 0))
            
        with pytest.raises(ValueError):
            projection_pseudometric.distance((0, 0, 0), (0, 0))

    @pytest.mark.unit
    @pytest.mark.parametrize("x,ys,expected_distances", [
        ((0, 0), [(0, 0), (1, 0)], [0, 1]),  # Simple x-axis projections
        ((0, 0), [(0, 1), (0, 2)], [0, 0]),  # Same x-coordinate
        ((0, 0), [(1, 1), (2, 1)], [1, 2]),  # Different x-coordinates
    ])
    def test_distances(self, projection_pseudometric, x, ys, expected_distances):
        """
        Test distances calculation from one point to multiple points.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
            x: tuple
                Reference point coordinates
            ys: list[tuple]
                List of points to calculate distances to
            expected_distances: list[float]
                Expected distances
        """
        distances = projection_pseudometric.distances(x, ys)
        assert list(distances) == expected_distances

    @pytest.mark.unit
    def test_check_non_negativity(self, projection_pseudometric):
        """
        Test non-negativity check.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
        """
        # Test with positive distance
        assert projection_pseudometric.check_non_negativity((0, 0), (1, 0))
        
        # Test with zero distance
        assert projection_pseudometric.check_non_negativity((0, 0), (0, 0))

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y", [
        ((0, 0), (1, 0)),  # Different points
        ((0, 0), (0, 0)),  # Same point
    ])
    def test_check_symmetry(self, projection_pseudometric, x, y):
        """
        Test symmetry check.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
            x: tuple
                First point coordinates
            y: tuple
                Second point coordinates
        """
        assert projection_pseudometric.check_symmetry(x, y)

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y,z,expected_result", [
        ((0, 0), (1, 0), (2, 0), True),  # Simple line
        ((0, 0), (1, 0), (0, 1), True),  # Right triangle
        ((0, 0), (1, 0), (3, 0), True),  # Extended line
    ])
    def test_check_triangle_inequality(self, projection_pseudometric, x, y, z, expected_result):
        """
        Test triangle inequality check.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
            x: tuple
                First point coordinates
            y: tuple
                Second point coordinates
            z: tuple
                Third point coordinates
            expected_result: bool
                Expected result of the check
        """
        assert projection_pseudometric.check_triangle_inequality(x, y, z) == expected_result

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y,expected_result", [
        ((0, 0), (0, 0), True),  # Same point
        ((0, 0), (1, 0), False),  # Different points
        ((0, 0), (0, 1), False),  # Same x but different y
    ])
    def test_check_weak_identity(self, projection_pseudometric, x, y, expected_result):
        """
        Test weak identity of indiscernibles check.
        
        Args:
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
            x: tuple
                First point coordinates
            y: tuple
                Second point coordinates
            expected_result: bool
                Expected result of the check
        """
        assert projection_pseudometric.check_weak_identity(x, y) == expected_result

    @pytest.mark.unit
    @patch('logging.getLogger')
    def test_logging_distance_error(self, mock_logger, projection_pseudometric):
        """
        Test logging during distance calculation error.
        
        Args:
            mock_logger: Mock
                Mocked logging.getLogger for verification
            projection_pseudometric: ProjectionPseudometricR2
                Instance of ProjectionPseudometricR2 from fixture
        """
        with pytest.raises(ValueError):
            projection_pseudometric.distance("invalid", (0, 0))
            
        # Verify error message was logged
        mock_logger.return_value.error.assert_called_once_with(
            "Invalid input types for distance calculation: %s",
            "invalid input types"
        )