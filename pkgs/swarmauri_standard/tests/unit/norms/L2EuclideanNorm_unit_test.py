import pytest
import logging
from swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm


@pytest.mark.unit
def test_l2euclidean_norm_compute():
    """
    Tests the compute method of L2EuclideanNorm with various inputs.
    """
    norm = L2EuclideanNorm()

    # Test with list of floats
    test_input = [3.0, 4.0]
    expected_output = 5.0
    assert norm.compute(test_input) == expected_output

    # Test with tuple of floats
    test_input = (3.0, 4.0)
    assert norm.compute(test_input) == expected_output

    # Test with single float
    test_input = 5.0
    expected_output = 5.0
    assert norm.compute(test_input) == expected_output

    # Test with empty list
    test_input = []
    expected_output = 0.0
    assert norm.compute(test_input) == expected_output

    # Test with zero values
    test_input = [0.0, 0.0]
    expected_output = 0.0
    assert norm.compute(test_input) == expected_output

    # Test with negative values
    test_input = [-3.0, -4.0]
    expected_output = 5.0
    assert norm.compute(test_input) == expected_output


@pytest.mark.unit
def test_l2euclidean_norm_invalid_input():
    """
    Tests the input validation of L2EuclideanNorm.compute method.
    """
    norm = L2EuclideanNorm()

    # Test with invalid type (string)
    test_input = "invalid"
    with pytest.raises(TypeError):
        norm.compute(test_input)

    # Test with None
    test_input = None
    with pytest.raises(TypeError):
        norm.compute(test_input)

    # Test with mixed types
    test_input = [1, "2"]
    with pytest.raises(TypeError):
        norm.compute(test_input)


@pytest.mark.unit
def test_l2euclidean_norm_logging(caplog):
    """
    Tests the logging functionality in L2EuclideanNorm.compute method.
    """
    norm = L2EuclideanNorm()
    test_input = [3.0, 4.0]

    # Test debug log on success
    with caplog.at_level(logging.DEBUG):
        norm.compute(test_input)
        assert "Computing L2 Euclidean norm" in caplog.text

    # Test error log on failure
    test_input = [1, "2"]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(TypeError):
            norm.compute(test_input)
        assert "Error computing norm" in caplog.text


@pytest.mark.unit
def test_l2euclidean_norm_string_representation():
    """
    Tests the string representation methods of L2EuclideanNorm.
    """
    norm = L2EuclideanNorm()

    assert str(norm) == "L2EuclideanNorm()"
    assert repr(norm) == "L2EuclideanNorm()"


@pytest.fixture
def l2euclidean_norm_instance():
    """
    Fixture providing a fresh instance of L2EuclideanNorm for each test.
    """
    return L2EuclideanNorm()
