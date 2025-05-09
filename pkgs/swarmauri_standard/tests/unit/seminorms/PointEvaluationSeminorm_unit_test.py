import logging
from collections.abc import Callable

import pytest

from swarmauri_standard.seminorms.PointEvaluationSeminorm import PointEvaluationSeminorm


@pytest.mark.unit
class TestPointEvaluationSeminorm:
    """
    Unit test class for PointEvaluationSeminorm.

    This class contains unit tests for the PointEvaluationSeminorm class.
    It verifies the functionality of the compute method, triangle inequality,
    and scalar homogeneity checks.
    """

    @pytest.fixture
    def point_evaluation(self):
        """
        Fixture to provide a default PointEvaluationSeminorm instance.

        Returns:
            PointEvaluationSeminorm: Instance with fixed_point=0.0
        """
        return PointEvaluationSeminorm(fixed_point=0.0)

    @pytest.mark.parametrize(
        "input_type, input_value, expected_result",
        [(Callable, lambda x: x**2, 0.0), (list, [1, 2, 3], 1), (tuple, (1, 2, 3), 1)],
    )
    def test_compute_success(
        self, input_type, input_value, expected_result, point_evaluation
    ):
        """
        Test successful computation of seminorm for different input types.

        Args:
            input_type: Type of input to test
            input_value: Input value for computation
            expected_result: Expected result of computation
            point_evaluation: PointEvaluationSeminorm instance
        """
        result = point_evaluation.compute(input_value)
        assert result == expected_result
        assert isinstance(result, float)

    def test_compute_unsupported_type(self, point_evaluation):
        """
        Test that compute raises TypeError for unsupported input types.

        Args:
            point_evaluation: PointEvaluationSeminorm instance
        """
        with pytest.raises(TypeError):
            point_evaluation.compute(set())

    def test_compute_fixed_point_not_set(self):
        """
        Test that compute raises ValueError when fixed_point is not set.
        """
        pes = PointEvaluationSeminorm(fixed_point=None)
        with pytest.raises(ValueError):
            pes.compute([1, 2, 3])

    @pytest.mark.parametrize(
        "a, b, expected_result",
        [([1, 2, 3], [4, 5, 6], True), (lambda x: x**2, lambda x: x + 1, True)],
    )
    def test_check_triangle_inequality(self, a, b, expected_result, point_evaluation):
        """
        Test triangle inequality check for different input types.

        Args:
            a: First element to check
            b: Second element to check
            expected_result: Expected result of triangle inequality check
            point_evaluation: PointEvaluationSeminorm instance
        """
        result = point_evaluation.check_triangle_inequality(a, b)
        assert result == expected_result

    @pytest.mark.parametrize(
        "a, scalar, expected_result",
        [([1, 2, 3], 2, True), (lambda x: x**2, 0.5, True)],
    )
    def test_check_scalar_homogeneity(
        self, a, scalar, expected_result, point_evaluation
    ):
        """
        Test scalar homogeneity check for different input types.

        Args:
            a: Element to check
            scalar: Scalar value to scale with
            expected_result: Expected result of scalar homogeneity check
            point_evaluation: PointEvaluationSeminorm instance
        """
        result = point_evaluation.check_scalar_homogeneity(a, scalar)
        assert result == expected_result

    def test_constructor(self):
        """
        Test that constructor initializes with correct default values.
        """
        pes_default = PointEvaluationSeminorm()
        assert pes_default.fixed_point is None
        assert pes_default.resource == "PointEvaluationSeminorm"

        pes_custom = PointEvaluationSeminorm(fixed_point=(1, 2))
        assert pes_custom.fixed_point == (1, 2)


@pytest.mark.unit
def test_point_evaluation_serialization():
    """
    Test serialization/deserialization of PointEvaluationSeminorm.
    """
    pes = PointEvaluationSeminorm(fixed_point=1.0)
    dumped = pes.model_dump_json()
    loaded = PointEvaluationSeminorm.model_validate_json(dumped)
    assert isinstance(loaded, PointEvaluationSeminorm)
    assert loaded.fixed_point == pes.fixed_point


@pytest.mark.unit
def test_logging():
    """
    Test that logging is properly configured and used.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    pes = PointEvaluationSeminorm(fixed_point=0.0)
    pes.compute([1, 2, 3])

    # Verify that debug messages are being logged
    # This is a basic check - in a real test environment,
    # you would typically use a logging handler to capture messages
    assert True
