import pytest
import logging
from swarmauri_standard.swarmauri_standard.seminorms.PointEvaluationSeminorm import PointEvaluationSeminorm

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestPointEvaluationSeminorm:
    """
    Unit tests for the PointEvaluationSeminorm class.
    """
    
    @pytest.mark.parametrize("point,expected_exception", [
        (5, None),
        (5.5, None),
        ("test_point", None),
        (-1, ValueError),
        ("too_long", ValueError)
    ])
    def test_constructor(self, point, expected_exception):
        """
        Tests the initialization of PointEvaluationSeminorm with valid and invalid points.
        
        Args:
            point: The point to test
            expected_exception: The expected exception type or None
        """
        if expected_exception is not None:
            with pytest.raises(expected_exception):
                PointEvaluationSeminorm(point)
        else:
            seminorm = PointEvaluationSeminorm(point)
            assert seminorm.point == point
            logger.info(f"Successfully created PointEvaluationSeminorm with point {point}")

    @pytest.mark.parametrize("input_type,input_value,point,expected_output", [
        ("callable", lambda x: x**2, 2, 4.0),
        ("sequence", [1, 2, 3, 4], 2, 3.0),
        ("string", "hello", 2, 108.0),  # ord('l') = 108
        ("float", 10.5, 0, 10.5),
        ("int", 5, 0, 5.0)
    ])
    def test_compute(self, input_type, input_value, point, expected_output):
        """
        Tests the compute method with various input types and values.
        
        Args:
            input_type: Type of input being tested
            input_value: The input value to evaluate
            point: The point of evaluation
            expected_output: The expected result
        """
        seminorm = PointEvaluationSeminorm(point)
        result = seminorm.compute(input_value)
        assert result == expected_output
        logger.info(f"Computed seminorm {result} for input {input_value} at point {point}")

    @pytest.mark.parametrize("input_value,point,expected_exception", [
        ([1, 2, 3], 5, ValueError),
        ("test", 10, ValueError),
        (lambda x: x, "invalid_point", ValueError)
    ])
    def test_compute_error_cases(self, input_value, point, expected_exception):
        """
        Tests error cases for the compute method.
        
        Args:
            input_value: The input value to evaluate
            point: The point of evaluation
            expected_exception: The expected exception type
        """
        seminorm = PointEvaluationSeminorm(point)
        with pytest.raises(expected_exception):
            seminorm.compute(input_value)
        logger.info(f"Successfully raised exception for invalid input {input_value} at point {point}")

    @pytest.mark.parametrize("a,b,expected_result", [
        (lambda x: x, lambda x: x, True),
        ([1, 2, 3], [4, 5, 6], True),
        (5, 10, True)
    ])
    def test_check_triangle_inequality(self, a, b, expected_result):
        """
        Tests the check_triangle_inequality method.
        
        Args:
            a: First input for the inequality check
            b: Second input for the inequality check
            expected_result: The expected boolean result
        """
        seminorm = PointEvaluationSeminorm(0)
        result = seminorm.check_triangle_inequality(a, b)
        assert result == expected_result
        logger.info(f"Triangle inequality check returned {result} for inputs {a} and {b}")

    @pytest.mark.parametrize("a,scalar,expected_result", [
        (lambda x: x, 2, True),
        ([1, 2, 3], 0.5, True),
        (5, -1, True)
    ])
    def test_check_scalar_homogeneity(self, a, scalar, expected_result):
        """
        Tests the check_scalar_homogeneity method.
        
        Args:
            a: Input to check
            scalar: Scalar to test homogeneity with
            expected_result: The expected boolean result
        """
        seminorm = PointEvaluationSeminorm(0)
        result = seminorm.check_scalar_homogeneity(a, scalar)
        assert result == expected_result
        logger.info(f"Scalar homogeneity check returned {result} for input {a} and scalar {scalar}")

    @pytest.mark.unit
    def test_class_attributes(self):
        """
        Tests the class-level attributes of PointEvaluationSeminorm.
        """
        assert PointEvaluationSeminorm.type == "PointEvaluationSeminorm"
        assert PointEvaluationSeminorm.resource == "Seminorm"
        logger.info("Successfully verified class attributes")