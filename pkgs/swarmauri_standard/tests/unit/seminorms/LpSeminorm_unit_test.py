import pytest
import numpy as np
import logging
from swarmauri_standard.swarmauri_standard.seminorms.LpSeminorm import LpSeminorm


@pytest.fixture
def lp_seminorm():
    """Fixture to create a default LpSeminorm instance with p=2 (Euclidean norm)"""
    return LpSeminorm(p=2.0)


@pytest.mark.unit
def test_resource(lp_seminorm):
    """Test that the resource type is correctly set"""
    assert lp_seminorm.resource == LpSeminorm.ResourceTypes.SEMINORM.value


@pytest.mark.unit
def test_type(lp_seminorm):
    """Test that the type is correctly set"""
    assert lp_seminorm.type == "LpSeminorm"


@pytest.mark.unit
def test_compute_scalar(lp_seminorm):
    """Test computing seminorm for scalar input"""
    result = lp_seminorm.compute(5.0)
    assert result == 0.0


@pytest.mark.unit
@pytest.mark.parametrize(
    "input,expected",
    [
        (np.array([1, 2, 3]), 3.0),  # L2 norm of [1,2,3] is sqrt(14) ≈ 3.7417
        (np.array([1, 0, 0]), 1.0),
        (np.array([0, 0, 0]), 0.0),
    ],
)
def test_compute_vector(lp_seminorm, input, expected):
    """Test computing seminorm for vector input"""
    result = lp_seminorm.compute(input)
    assert np.isclose(result, expected, rtol=1e-2)


@pytest.mark.unit
@pytest.mark.parametrize(
    "input,axis,expected",
    [
        (np.array([[1, 2], [3, 4]]), 0, 5.0),  # L2 norm along axis 0
        (np.array([[1, 2], [3, 4]]), 1, np.sqrt(5)),  # L2 norm along axis 1
        (np.array([[1, 2], [3, 4]]), None, np.sqrt(30)),  # Frobenius norm
    ],
)
def test_compute_matrix(lp_seminorm, input, axis, expected):
    """Test computing seminorm for matrix input with different axes"""
    lp_seminorm.axis = axis
    result = lp_seminorm.compute(input)
    assert np.isclose(result, expected, rtol=1e-2)


@pytest.mark.unit
def test_triangle_inequality(lp_seminorm):
    """Test triangle inequality for Lp seminorm"""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    seminorm_ab = lp_seminorm.compute(a + b)
    seminorm_a = lp_seminorm.compute(a)
    seminorm_b = lp_seminorm.compute(b)
    assert seminorm_ab <= seminorm_a + seminorm_b


@pytest.mark.unit
def test_scalar_homogeneity(lp_seminorm):
    """Test scalar homogeneity property"""
    a = np.array([1, 2, 3])
    scalar = 2.0
    seminorm_a = lp_seminorm.compute(a)
    scaled_a = scalar * a
    seminorm_scaled = lp_seminorm.compute(scaled_a)
    expected = scalar ** (1.0 / lp_seminorm.p) * seminorm_a
    assert np.isclose(seminorm_scaled, expected)


@pytest.mark.unit
def test_invalid_p_value():
    """Test that invalid p values are handled correctly"""
    with pytest.raises(ValueError):
        LpSeminorm(p=-1.0)


@pytest.mark.unit
def test_logging():
    """Test that logging messages are generated"""
    logger = logging.getLogger(__name__)
    with pytest.raises(AssertionError):
        # Use a side effect to check if debug message is logged
        def check_debug(msg, args):
            assert "Computing Lp seminorm" in msg
            raise AssertionError("Debug message found")

        logger.debug = check_debug
        lp_seminorm.compute(np.array([1, 2, 3]))


@pytest.mark.unit
def test_error_handling(lp_seminorm):
    """Test that errors are properly logged and raised"""
    logger = logging.getLogger(__name__)
    error_msg = "Test error message"

    def mock_error(*args):
        raise ValueError(error_msg)

    with pytest.raises(ValueError) as exc_info:
        logger.error = mock_error
        lp_seminorm.compute("invalid_input")

    assert str(exc_info.value) == f"Failed to compute Lp seminorm: {error_msg}"
