import pytest
import numpy as np
import logging
from typing import List, Tuple, Any

from swarmauri_standard.metrics.LpMetric import LpMetric

# Configure logger
logger = logging.getLogger(__name__)


@pytest.fixture
def lp_metric_p2():
    """
    Fixture that returns an LpMetric instance with p=2 (Euclidean).
    
    Returns
    -------
    LpMetric
        An instance of LpMetric with p=2
    """
    return LpMetric(p=2.0)


@pytest.fixture
def lp_metric_p1():
    """
    Fixture that returns an LpMetric instance with p=1 (Manhattan).
    
    Returns
    -------
    LpMetric
        An instance of LpMetric with p=1
    """
    return LpMetric(p=1.0)


@pytest.fixture
def lp_metric_pinf():
    """
    Fixture that returns an LpMetric instance with p=infinity (Chebyshev).
    
    Returns
    -------
    LpMetric
        An instance of LpMetric with p=infinity
    """
    return LpMetric(p=float('inf'))


@pytest.mark.unit
def test_lp_metric_initialization():
    """Test that LpMetric initializes correctly with default and custom values."""
    # Default initialization should set p to 2
    default_metric = LpMetric()
    assert default_metric.p == 2.0
    assert default_metric.type == "LpMetric"
    
    # Custom p value
    custom_metric = LpMetric(p=3.0)
    assert custom_metric.p == 3.0


@pytest.mark.unit
def test_lp_metric_validation():
    """Test that LpMetric validates p value correctly."""
    # Valid p values
    assert LpMetric(p=1.0).p == 1.0
    assert LpMetric(p=2.0).p == 2.0
    assert LpMetric(p=float('inf')).p == float('inf')
    
    # Invalid p values should raise ValueError
    with pytest.raises(ValueError):
        LpMetric(p=0.5)
    
    with pytest.raises(ValueError):
        LpMetric(p=0)
    
    with pytest.raises(ValueError):
        LpMetric(p=-1)


@pytest.mark.unit
@pytest.mark.parametrize("p,x,y,expected", [
    # p=1 (Manhattan distance)
    (1, [0, 0], [3, 4], 7.0),
    (1, [1, 2, 3], [4, 5, 6], 9.0),
    # p=2 (Euclidean distance)
    (2, [0, 0], [3, 4], 5.0),
    (2, [1, 2, 3], [4, 5, 6], 5.196152422706632),
    # p=3
    (3, [0, 0], [3, 4], 4.497941445275415),
    # p=infinity (Chebyshev distance)
    (float('inf'), [0, 0], [3, 4], 4.0),
    (float('inf'), [1, 2, 3], [4, 5, 6], 3.0),
])
def test_lp_metric_distance(p: float, x: List[float], y: List[float], expected: float):
    """
    Test LpMetric distance calculation with different p values.
    
    Parameters
    ----------
    p : float
        The p value for the metric
    x : List[float]
        First vector
    y : List[float]
        Second vector
    expected : float
        Expected distance
    """
    metric = LpMetric(p=p)
    result = metric.distance(x, y)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_lp_metric_distance_numpy_arrays(lp_metric_p2):
    """Test LpMetric distance calculation with numpy arrays."""
    x = np.array([0, 0])
    y = np.array([3, 4])
    assert np.isclose(lp_metric_p2.distance(x, y), 5.0)
    
    # Test with multi-dimensional arrays
    x = np.array([[0, 0], [1, 1]])
    y = np.array([[3, 4], [2, 3]])
    with pytest.raises(ValueError):
        # Should raise error for multi-dimensional arrays with different shapes
        lp_metric_p2.distance(x, y.flatten())


@pytest.mark.unit
def test_lp_metric_euclidean(lp_metric_p2):
    """Test specific Euclidean distance cases."""
    # Origin to (1,1)
    assert np.isclose(lp_metric_p2.distance([0, 0], [1, 1]), np.sqrt(2))
    
    # Points on a line
    assert np.isclose(lp_metric_p2.distance([0, 0, 0], [1, 0, 0]), 1.0)
    
    # 3D space
    assert np.isclose(lp_metric_p2.distance([1, 2, 3], [4, 5, 6]), 5.196152422706632)


@pytest.mark.unit
def test_lp_metric_manhattan(lp_metric_p1):
    """Test specific Manhattan distance cases."""
    # Origin to (1,1)
    assert np.isclose(lp_metric_p1.distance([0, 0], [1, 1]), 2.0)
    
    # Points on a line
    assert np.isclose(lp_metric_p1.distance([0, 0, 0], [1, 0, 0]), 1.0)
    
    # 3D space
    assert np.isclose(lp_metric_p1.distance([1, 2, 3], [4, 5, 6]), 9.0)


@pytest.mark.unit
def test_lp_metric_chebyshev(lp_metric_pinf):
    """Test specific Chebyshev distance cases."""
    # Origin to (1,1)
    assert np.isclose(lp_metric_pinf.distance([0, 0], [1, 1]), 1.0)
    
    # Points with different coordinates
    assert np.isclose(lp_metric_pinf.distance([0, 0], [3, 4]), 4.0)
    
    # 3D space
    assert np.isclose(lp_metric_pinf.distance([1, 2, 3], [4, 5, 6]), 3.0)


@pytest.mark.unit
def test_lp_metric_are_identical():
    """Test the are_identical method of LpMetric."""
    metric = LpMetric(p=2.0)
    
    # Identical points
    assert metric.are_identical([1, 2, 3], [1, 2, 3])
    
    # Nearly identical points (floating-point comparison)
    assert metric.are_identical([1.0, 2.0, 3.0], [1.0, 2.0, 3.0 + 1e-10])
    
    # Different points
    assert not metric.are_identical([1, 2, 3], [1, 2, 4])
    assert not metric.are_identical([0, 0], [1, 1])


@pytest.mark.unit
def test_lp_metric_error_handling():
    """Test error handling in LpMetric."""
    metric = LpMetric(p=2.0)
    
    # Different length vectors
    with pytest.raises(ValueError):
        metric.distance([1, 2, 3], [1, 2])
    
    # Non-numeric inputs
    with pytest.raises(TypeError):
        metric.distance(["a", "b"], ["c", "d"])


@pytest.mark.unit
def test_lp_metric_string_representation():
    """Test the string representation of LpMetric."""
    # Manhattan (p=1)
    assert str(LpMetric(p=1.0)) == "Manhattan Metric (p=1.0)"
    
    # Euclidean (p=2)
    assert str(LpMetric(p=2.0)) == "Euclidean Metric (p=2.0)"
    
    # Chebyshev (p=inf)
    assert str(LpMetric(p=float('inf'))) == "Chebyshev Metric (p=inf)"
    
    # Other p values
    assert str(LpMetric(p=3.0)) == "L3.0 Metric (p=3.0)"


@pytest.mark.unit
def test_lp_metric_serialization():
    """Test serialization and deserialization of LpMetric."""
    # Create an instance
    original = LpMetric(p=3.5)
    
    # Serialize to JSON
    json_str = original.model_dump_json()
    
    # Deserialize from JSON
    deserialized = LpMetric.model_validate_json(json_str)
    
    # Check that the deserialized object matches the original
    assert deserialized.p == original.p
    assert deserialized.type == original.type