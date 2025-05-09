import pytest
import logging
from swarmauri_standard.swarmauri_standard.pseudometrics.ProjectionPseudometricR2 import ProjectionPseudometricR2

@pytest.mark.unit
class TestProjectionPseudometricR2:
    """
    Unit tests for the ProjectionPseudometricR2 class.
    """
    
    @pytest.fixture
    def logger(self):
        """
        Fixture to provide a logger instance.
        """
        return logging.getLogger(__name__)

    @pytest.mark.unit
    def test_initialization(self, logger):
        """
        Test the initialization of ProjectionPseudometricR2 with valid and invalid parameters.
        """
        # Test default initialization
        p = ProjectionPseudometricR2()
        assert p.axis == 'x'
        logger.debug("Test default initialization passed")

        # Test initialization with 'y' axis
        p = ProjectionPseudometricR2(axis='y')
        assert p.axis == 'y'
        logger.debug("Test initialization with 'y' axis passed")

        # Test invalid axis value
        with pytest.raises(ValueError):
            ProjectionPseudometricR2(axis='z')
        logger.debug("Test invalid axis value passed")

    @pytest.mark.unit
    def test_distance(self, logger):
        """
        Test the distance calculation for various input types and scenarios.
        """
        p_x = ProjectionPseudometricR2(axis='x')
        p_y = ProjectionPseudometricR2(axis='y')

        # Test with tuples
        assert p_x.distance((1, 2), (3, 4)) == 2
        assert p_y.distance((1, 2), (3, 4)) == 2
        logger.debug("Test distance with tuples passed")

        # Test with lists
        assert p_x.distance([1, 2], [3, 4]) == 2
        assert p_y.distance([1, 2], [3, 4]) == 2
        logger.debug("Test distance with lists passed")

        # Test invalid points
        with pytest.raises(ValueError):
            p_x.distance([1], [2])
        logger.debug("Test invalid points passed")

    @pytest.mark.unit
    def test_distances(self, logger):
        """
        Test the distances method with multiple points.
        """
        p = ProjectionPseudometricR2()
        
        # Test with list of tuples
        points = [(1, 2), (3, 4), (5, 6)]
        distances = p.distances((0, 0), points)
        assert len(distances) == 3
        logger.debug("Test distances with list of tuples passed")

        # Test with a single point as a tuple
        distance = p.distances((0, 0), [(1, 1)])
        assert len(distance) == 1
        logger.debug("Test distances with single point as tuple passed")

    @pytest.mark.unit
    def test_check_non_negativity(self, logger):
        """
        Test the non-negativity check.
        """
        p = ProjectionPseudometricR2()
        assert p.check_non_negativity((1, 2), (3, 4)) == True
        logger.debug("Test non-negativity passed")

    @pytest.mark.unit
    def test_check_symmetry(self, logger):
        """
        Test the symmetry check.
        """
        p = ProjectionPseudometricR2()
        assert p.check_symmetry((1, 2), (3, 4)) == True
        logger.debug("Test symmetry passed")

    @pytest.mark.unit
    def test_check_triangle_inequality(self, logger):
        """
        Test the triangle inequality check.
        """
        p = ProjectionPseudometricR2()
        assert p.check_triangle_inequality((0, 0), (1, 1), (2, 2)) == True
        logger.debug("Test triangle inequality passed")

    @pytest.mark.unit
    def test_check_weak_identity(self, logger):
        """
        Test the weak identity check.
        """
        p = ProjectionPseudometricR2()
        assert p.check_weak_identity((1, 2), (1, 3)) == False
        logger.debug("Test weak identity passed")

    @pytest.mark.unit
    @pytest.mark.parametrize("axis,expected_distance", [
        ('x', 2),
        ('y', 1)
    ])
    def test_parameterized_distance(self, axis, expected_distance, logger):
        """
        Parameterized test for distance calculation with different axes.
        """
        p = ProjectionPseudometricR2(axis=axis)
        distance = p.distance((1, 2), (3, 3))
        assert distance == expected_distance
        logger.debug(f"Test parameterized distance with axis={axis} passed")