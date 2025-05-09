import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.norms.SobolevNorm import SobolevNorm


@pytest.mark.unit
def test_compute():
    """Test the compute method of the SobolevNorm class."""

    # Test with callable function
    def test_func(x):
        return 1.0

    norm = SobolevNorm().compute(test_func)
    assert norm >= 0.0

    # Test with numpy array
    test_array = np.array([1.0, 2.0, 3.0])
    norm = SobolevNorm().compute(test_array)
    assert norm >= 0.0

    # Test with string
    norm = SobolevNorm().compute("5.0")
    assert norm >= 0.0

    # Test invalid input
    with pytest.raises(ValueError):
        SobolevNorm().compute(None)


@pytest.mark.unit
def test_check_non_negativity():
    """Test the non-negativity check of the SobolevNorm class."""

    # Test with zero function
    def zero_func(x):
        return 0.0

    SobolevNorm().check_non_negativity(zero_func)

    # Test with non-zero function
    def non_zero_func(x):
        return 1.0

    SobolevNorm().check_non_negativity(non_zero_func)

    # Test with negative values
    with pytest.raises(AssertionError):
        SobolevNorm().check_non_negativity(-1.0)


@pytest.mark.unit
def test_check_triangle_inequality():
    """Test the triangle inequality check of the SobolevNorm class."""

    # Test with simple functions
    def func1(x):
        return 1.0

    def func2(x):
        return 2.0

    SobolevNorm().check_triangle_inequality(func1, func2)


@pytest.mark.unit
def test_check_absolute_homogeneity():
    """Test the absolute homogeneity check of the SobolevNorm class."""

    # Test with scalar 2.0
    def test_func(x):
        return 1.0

    SobolevNorm().check_absolute_homogeneity(test_func, 2.0)

    # Test with negative scalar
    SobolevNorm().check_absolute_homogeneity(test_func, -1.0)


@pytest.mark.unit
def test_check_definiteness():
    """Test the definiteness check of the SobolevNorm class."""
    # Test with zero vector
    zero_array = np.array([0.0, 0.0, 0.0])
    SobolevNorm().check_definiteness(zero_array)

    # Test with non-zero vector
    non_zero_array = np.array([1.0, 2.0, 3.0])
    SobolevNorm().check_definiteness(non_zero_array)

    # Test with zero function
    def zero_func(x):
        return 0.0

    SobolevNorm().check_definiteness(zero_func)

    # Test with non-zero function
    def non_zero_func(x):
        return 1.0

    SobolevNorm().check_definiteness(non_zero_func)


@pytest.fixture
def logging_config():
    """Fixture to configure logging."""
    logging.basicConfig(level=logging.WARNING)
    yield
    logging.basicConfig(level=logging.NOTSET)


def test_logging(logging_config):
    """Test logging configuration."""
    logger = logging.getLogger(__name__)
    logger.debug("Testing logging configuration")
    assert logger.level == logging.WARNING


@pytest.mark.unit
@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (np.array([1.0, 2.0, 3.0]), 3.0),
        ([1.0, 2.0, 3.0], 3.0),
    ],
)
def test_compute_parameterized(test_input, expected_result):
    """Parameterized test for compute method."""
    norm = SobolevNorm().compute(test_input)
    assert norm >= expected_result


@pytest.mark.unit
def test_invalid_input():
    """Test handling of invalid input types."""
    with pytest.raises(ValueError):
        SobolevNorm().compute("invalid_string")


@pytest.mark.unit
def test_compute_with_derivatives():
    """Test compute method with function and derivatives."""

    def func(x):
        return x**2

    def deriv(x):
        return 2 * x

    test_input = [func, deriv]
    norm = SobolevNorm().compute(test_input)
    assert norm >= 0.0


@pytest.mark.unit
def test_compute_with_multiple_derivatives():
    """Test compute method with multiple derivatives."""

    def func(x):
        return x**3

    def deriv1(x):
        return 3 * x**2

    def deriv2(x):
        return 6 * x

    test_input = [func, deriv1, deriv2]
    norm = SobolevNorm().compute(test_input)
    assert norm >= 0.0


@pytest.mark.unit
def test_compute_with_empty_input():
    """Test compute method with empty input."""
    with pytest.raises(ValueError):
        SobolevNorm().compute([])
