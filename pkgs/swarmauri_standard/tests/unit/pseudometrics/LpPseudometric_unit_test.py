import logging
import pytest
import numpy as np
from typing import List, Tuple, Optional
from swarmauri_standard.pseudometrics.LpPseudometric import LpPseudometric

# Configure logging
logger = logging.getLogger(__name__)

# Fixtures
@pytest.fixture
def lp_pseudometric():
    """
    Create a default LpPseudometric instance with p=2 (Euclidean).
    
    Returns:
        LpPseudometric: An instance with default parameters
    """
    return LpPseudometric(p=2)

@pytest.fixture
def sample_vectors():
    """
    Create sample vectors for testing.
    
    Returns:
        Tuple: A tuple containing sample vectors
    """
    return (
        np.array([1, 2, 3]),
        np.array([4, 5, 6]),
        np.array([7, 8, 9]),
        np.array([1, 1, 1])
    )

# Test cases
@pytest.mark.unit
def test_initialization():
    """Test proper initialization with different parameters."""
    # Test default initialization
    metric = LpPseudometric()
    assert metric.p == 2.0
    assert metric.domain is None
    assert metric.coordinates is None
    
    # Test with specific p value
    metric = LpPseudometric(p=1)
    assert metric.p == 1.0
    
    # Test with infinity p value (different representations)
    metric1 = LpPseudometric(p='inf')
    metric2 = LpPseudometric(p=float('inf'))
    metric3 = LpPseudometric(p='∞')
    assert metric1.p == float('inf')
    assert metric2.p == float('inf')
    assert metric3.p == float('inf')
    
    # Test with domain and coordinates
    domain = [0, 10]
    coordinates = [0, 2]
    metric = LpPseudometric(p=2, domain=domain, coordinates=coordinates)
    assert metric.p == 2.0
    assert metric.domain == domain
    assert metric.coordinates == coordinates

@pytest.mark.unit
def test_invalid_p_value():
    """Test that initialization with invalid p values raises ValueError."""
    with pytest.raises(ValueError):
        LpPseudometric(p=0)
    
    with pytest.raises(ValueError):
        LpPseudometric(p=-1)

@pytest.mark.unit
@pytest.mark.parametrize("p,x,y,expected", [
    (1, [1, 2, 3], [4, 5, 6], 9.0),  # Manhattan distance
    (2, [1, 2, 3], [4, 5, 6], 5.196152422706632),  # Euclidean distance
    ('inf', [1, 2, 3], [4, 5, 6], 3.0),  # Chebyshev distance
    (3, [1, 2, 3], [4, 5, 6], 4.326748710922225),  # L3 norm
])
def test_distance_calculation(p, x, y, expected):
    """
    Test distance calculation with different p values.
    
    Args:
        p: The p-value for the Lp norm
        x: First vector
        y: Second vector
        expected: Expected distance
    """
    metric = LpPseudometric(p=p)
    result = metric.distance(x, y)
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_distance_with_custom_extractor():
    """Test distance calculation with a custom value extractor."""
    # Define objects with a 'values' attribute
    class DataPoint:
        def __init__(self, values):
            self.values = values
    
    # Create a metric with a custom extractor
    extractor = lambda obj: obj.values
    metric = LpPseudometric(p=2, value_extractor=extractor)
    
    # Create test objects
    point1 = DataPoint([1, 2, 3])
    point2 = DataPoint([4, 5, 6])
    
    # Calculate distance
    distance = metric.distance(point1, point2)
    assert np.isclose(distance, 5.196152422706632)

@pytest.mark.unit
def test_distance_with_coordinates(sample_vectors):
    """
    Test distance calculation with specific coordinates.
    
    Args:
        sample_vectors: Fixture providing sample vectors
    """
    x, y = sample_vectors[0], sample_vectors[1]
    
    # Calculate distance using only first and last coordinates
    metric = LpPseudometric(p=2, coordinates=[0, 2])
    result = metric.distance(x, y)
    
    # Manually calculate expected distance
    expected = np.sqrt((x[0] - y[0])**2 + (x[2] - y[2])**2)
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_distance_with_domain():
    """Test distance calculation with domain restriction."""
    # Create vectors with some values outside the domain
    x = np.array([1, 5, 10, 15])
    y = np.array([2, 6, 11, 16])
    
    # Create metric with domain [0, 10]
    metric = LpPseudometric(p=2, domain=[0, 10])
    
    # Only the first three elements of each vector should be considered
    # since the last elements (15 and 16) are outside the domain
    result = metric.distance(x, y)
    
    # Calculate expected distance manually with filtered values
    filtered_x = np.array([1, 5, 10])
    filtered_y = np.array([2, 6, 11])
    expected = np.sqrt(np.sum((filtered_x - filtered_y)**2))
    
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_batch_distance(lp_pseudometric, sample_vectors):
    """
    Test batch distance calculation.
    
    Args:
        lp_pseudometric: Fixture providing a default LpPseudometric
        sample_vectors: Fixture providing sample vectors
    """
    x1, x2, y1, y2 = sample_vectors
    
    # Calculate batch distances
    results = lp_pseudometric.batch_distance([x1, x2], [y1, y2])
    
    # Calculate expected distances individually
    expected = [
        lp_pseudometric.distance(x1, y1),
        lp_pseudometric.distance(x2, y2)
    ]
    
    assert len(results) == 2
    assert np.isclose(results[0], expected[0])
    assert np.isclose(results[1], expected[1])

@pytest.mark.unit
def test_batch_distance_with_different_lengths(lp_pseudometric, sample_vectors):
    """
    Test that batch_distance raises ValueError when input lists have different lengths.
    
    Args:
        lp_pseudometric: Fixture providing a default LpPseudometric
        sample_vectors: Fixture providing sample vectors
    """
    x1, x2, y1, _ = sample_vectors
    
    with pytest.raises(ValueError):
        lp_pseudometric.batch_distance([x1, x2], [y1])

@pytest.mark.unit
def test_pairwise_distances(lp_pseudometric, sample_vectors):
    """
    Test pairwise distance calculation.
    
    Args:
        lp_pseudometric: Fixture providing a default LpPseudometric
        sample_vectors: Fixture providing sample vectors
    """
    x1, x2, x3, _ = sample_vectors
    points = [x1, x2, x3]
    
    # Calculate pairwise distances
    distances = lp_pseudometric.pairwise_distances(points)
    
    # Verify matrix properties
    assert len(distances) == 3
    assert len(distances[0]) == 3
    
    # Verify diagonal elements (should be 0)
    for i in range(3):
        assert distances[i][i] == 0.0
    
    # Verify symmetry
    for i in range(3):
        for j in range(i+1, 3):
            assert np.isclose(distances[i][j], distances[j][i])
    
    # Verify specific distances
    assert np.isclose(distances[0][1], lp_pseudometric.distance(x1, x2))
    assert np.isclose(distances[0][2], lp_pseudometric.distance(x1, x3))
    assert np.isclose(distances[1][2], lp_pseudometric.distance(x2, x3))

@pytest.mark.unit
def test_verify_properties(lp_pseudometric, sample_vectors):
    """
    Test verification of pseudometric properties.
    
    Args:
        lp_pseudometric: Fixture providing a default LpPseudometric
        sample_vectors: Fixture providing sample vectors
    """
    x1, x2, x3, _ = sample_vectors
    
    # Verify properties with sample vectors
    result = lp_pseudometric.verify_properties([x1, x2, x3])
    assert result is True

@pytest.mark.unit
def test_verify_properties_insufficient_samples(lp_pseudometric, sample_vectors):
    """
    Test that verify_properties returns False with insufficient samples.
    
    Args:
        lp_pseudometric: Fixture providing a default LpPseudometric
        sample_vectors: Fixture providing sample vectors
    """
    x1, x2, _, _ = sample_vectors
    
    # Try to verify with only 2 samples
    result = lp_pseudometric.verify_properties([x1, x2])
    assert result is False

@pytest.mark.unit
def test_different_length_inputs(lp_pseudometric):
    """
    Test handling of inputs with different lengths.
    
    Args:
        lp_pseudometric: Fixture providing a default LpPseudometric
    """
    x = np.array([1, 2, 3, 4])
    y = np.array([5, 6, 7])
    
    # Should use the first 3 elements only
    result = lp_pseudometric.distance(x, y)
    expected = np.sqrt(np.sum((x[:3] - y)**2))
    
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_string_representation():
    """Test the string representation of LpPseudometric."""
    # Test with default parameters
    metric = LpPseudometric()
    assert str(metric) == "LpPseudometric(p=2.0)"
    
    # Test with specific parameters
    metric = LpPseudometric(p=1, domain=[0, 10], coordinates=[0, 2])
    assert str(metric) == "LpPseudometric(p=1.0, domain=[0, 10], coordinates=[0, 2])"

@pytest.mark.unit
def test_component_registration():
    """Test that LpPseudometric is properly registered as a component."""
    from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
    
    # Check that LpPseudometric is registered with the correct type
    assert "LpPseudometric" in PseudometricBase.get_registered_types()
    
    # Check that the resource type is correct
    assert LpPseudometric.resource == "Pseudometric"
    assert LpPseudometric.type == "LpPseudometric"