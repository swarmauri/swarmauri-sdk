import pytest
from swarmauri_standard.swarmauri_standard.seminorms.PartialSumSeminorm import PartialSumSeminorm
import logging

@pytest.mark.unit
class TestPartialSumSeminorm:
    """
    Unit tests for the PartialSumSeminorm class.
    
    This class provides comprehensive unit testing for the PartialSumSeminorm
    implementation. It tests initialization, compute method, and other auxiliary
    methods to ensure correct functionality.
    """
    
    @pytest.fixture
    def setup_logging(self):
        """
        Fixture to setup basic logging for tests.
        
        Returns:
            logger: The configured logger instance
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        return logger
    
    @pytest.mark.unit
    def test_init_with_none_indices(self, setup_logging):
        """
        Test initialization with None indices.
        
        When indices are None, they should default to slice(None).
        """
        pss = PartialSumSeminorm()
        assert pss.indices == slice(None)
        
    @pytest.mark.unit
    def test_init_with_slice_indices(self):
        """
        Test initialization with slice indices.
        """
        indices = slice(0, 5, 2)
        pss = PartialSumSeminorm(indices=indices)
        assert pss.indices == indices
        
    @pytest.mark.unit
    def test_init_with_list_indices(self):
        """
        Test initialization with list indices.
        """
        indices = [0, 2, 4]
        pss = PartialSumSeminorm(indices=indices)
        assert pss.indices == tuple(sorted(indices))
        
    @pytest.mark.unit
    def test_init_with_tuple_indices(self):
        """
        Test initialization with tuple indices.
        """
        indices = (0, 2, 4)
        pss = PartialSumSeminorm(indices=indices)
        assert pss.indices == indices
        
    @pytest.mark.unit
    def test_init_with_invalid_indices(self):
        """
        Test initialization with invalid indices.
        
        Should raise ValueError for invalid types.
        """
        with pytest.raises(ValueError):
            PartialSumSeminorm(indices="invalid")
            
    @pytest.mark.unit
    @pytest.mark.parametrize("input_type, input_value, expected_result", [
        (list, [1, 2, 3, 4], 10),
        (tuple, (5, 6, 7), 18),
        (str, "1234", 10)
    ])
    def test_compute_with_valid_inputs(self, input_type, input_value, expected_result):
        """
        Test compute method with valid input types.
        
        Tests that the compute method correctly handles different iterable types
        and returns the expected sum.
        """
        pss = PartialSumSeminorm()
        result = pss.compute(input_value)
        assert result == expected_result
        
    @pytest.mark.unit
    def test_compute_with_non_iterable_input(self):
        """
        Test compute method with non-iterable input.
        
        Should raise ValueError when input is not iterable.
        """
        pss = PartialSumSeminorm()
        with pytest.raises(ValueError):
            pss.compute(123)
            
    @pytest.mark.unit
    def test_compute_with_slice_indices(self):
        """
        Test compute method with slice indices.
        """
        pss = PartialSumSeminorm(slice(0, 3))
        input = [1, 2, 3, 4, 5]
        result = pss.compute(input)
        assert result == 6
        
    @pytest.mark.unit
    def test_compute_with_list_indices(self):
        """
        Test compute method with list indices.
        """
        pss = PartialSumSeminorm([0, 2, 4])
        input = [1, 2, 3, 4, 5]
        result = pss.compute(input)
        assert result == 1 + 3 + 5
        
    @pytest.mark.unit
    def test_check_triangle_inequality(self):
        """
        Test check_triangle_inequality method.
        
        The triangle inequality should always hold for partial sum seminorm.
        """
        pss = PartialSumSeminorm()
        a = [1, 2]
        b = [3, 4]
        assert pss.check_triangle_inequality(a, b) is True
        
    @pytest.mark.unit
    def test_check_scalar_homogeneity(self):
        """
        Test check_scalar_homogeneity method.
        
        The scalar homogeneity should always hold for partial sum seminorm.
        """
        pss = PartialSumSeminorm()
        a = [1, 2]
        scalar = 5
        assert pss.check_scalar_homogeneity(a, scalar) is True
        
    @pytest.mark.unit
    def test_serialization(self):
        """
        Test serialization/deserialization of PartialSumSeminorm.
        
        Verify that model_dump_json and model_validate_json work correctly.
        """
        pss = PartialSumSeminorm()
        dumped = pss.model_dump_json()
        validated = PartialSumSeminorm.model_validate_json(dumped)
        assert pss.id == validated.id