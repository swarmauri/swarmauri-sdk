import pytest
import logging
from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestGeneralLpNorm:
    """
    Unit tests for the GeneralLpNorm class.
    """

    @pytest.fixture
    def general_l_p_norm(self):
        """
        Fixture to provide a GeneralLpNorm instance with default p=2.0.
        """
        return GeneralLpNorm()

    @pytest.mark.unit
    def test_initialization(self, general_l_p_norm):
        """
        Test that the GeneralLpNorm instance initializes correctly.
        """
        logger.debug("Testing GeneralLpNorm initialization")
        assert general_l_p_norm.p == 2.0
        assert general_l_p_norm.type == "GeneralLpNorm"

    @pytest.mark.unit
    @pytest.mark.parametrize("invalid_p,expected_error", [
        (1.0, ValueError),
        (0.5, ValueError),
        (float('inf'), ValueError),
        (float('nan'), ValueError),
        ('non-numeric', ValueError)
    ])
    def test_invalid_p_values(self, invalid_p, expected_error):
        """
        Test that initializing with invalid p values raises ValueError.
        """
        logger.debug(f"Testing invalid p value: {invalid_p}")
        with pytest.raises(expected_error):
            GeneralLpNorm(p=invalid_p)

    @pytest.mark.unit
    def test_compute_method(self, general_l_p_norm):
        """
        Test that the compute method calculates the correct Lp norm.
        """
        logger.debug("Testing compute method with various inputs")
        
        # Test with p=2.0 (Euclidean norm)
        vector = [3.0, 4.0]
        expected_norm = 5.0
        assert general_l_p_norm.compute(vector) == expected_norm
        
        # Test with p=1.0 (Should use a different instance)
        l1_norm = GeneralLpNorm(p=1.0)
        vector = [1.0, 2.0, 3.0]
        expected_norm = 6.0
        assert l1_norm.compute(vector) == expected_norm
        
        # Test with single-element vector
        vector = [5.0]
        expected_norm = 5.0
        assert general_l_p_norm.compute(vector) == expected_norm
        
        # Test with zero vector
        vector = [0.0, 0.0, 0.0]
        expected_norm = 0.0
        assert general_l_p_norm.compute(vector) == expected_norm

    @pytest.mark.unit
    def test_compute_invalid_input(self, general_l_p_norm):
        """
        Test that compute method raises ValueError for invalid input.
        """
        logger.debug("Testing compute method with invalid input")
        
        # Test with non-sequence input
        with pytest.raises(ValueError):
            general_l_p_norm.compute(5.0)
            
        # Test with None input
        with pytest.raises(ValueError):
            general_l_p_norm.compute(None)

    @pytest.mark.unit
    def test_repr_method(self, general_l_p_norm):
        """
        Test that the string representation is correct.
        """
        logger.debug("Testing __repr__ method")
        expected_repr = f"GeneralLpNorm(p={general_l_p_norm.p})"
        assert repr(general_l_p_norm) == expected_repr

    @pytest.mark.unit
    def test_resource_and_type_attributes(self):
        """
        Test that the resource and type class attributes are correctly set.
        """
        logger.debug("Testing resource and type attributes")
        assert GeneralLpNorm.resource == "Norm"
        assert GeneralLpNorm.type == "GeneralLpNorm"