import logging
import numpy as np
import pytest
from typing import List, Set, Tuple
from swarmauri_standard.seminorms.CoordinateProjectionSeminorm import CoordinateProjectionSeminorm

# Set up logging
logger = logging.getLogger(__name__)

# Fixtures for common test data
@pytest.fixture
def sample_projection_indices() -> Set[int]:
    """
    Fixture providing a sample set of projection indices.

    Returns
    -------
    Set[int]
        A set of indices to use for projection.
    """
    return {0, 2, 4}

@pytest.fixture
def sample_vectors() -> List[np.ndarray]:
    """
    Fixture providing sample vectors for testing.

    Returns
    -------
    List[np.ndarray]
        A list of sample vectors.
    """
    return [
        np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([-1.0, -2.0, -3.0, -4.0, -5.0]),
        np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    ]

@pytest.mark.unit
def test_initialization():
    """Test the initialization of CoordinateProjectionSeminorm."""
    # Test with a list of indices
    indices_list = [0, 2, 4]
    seminorm_list = CoordinateProjectionSeminorm(indices_list)
    assert seminorm_list.projection_indices == set(indices_list)
    
    # Test with a set of indices
    indices_set = {1, 3}
    seminorm_set = CoordinateProjectionSeminorm(indices_set)
    assert seminorm_set.projection_indices == indices_set

@pytest.mark.unit
def test_type():
    """Test the type attribute of CoordinateProjectionSeminorm."""
    seminorm = CoordinateProjectionSeminorm([0, 1])
    assert seminorm.type == "CoordinateProjectionSeminorm"

@pytest.mark.unit
def test_project(sample_projection_indices, sample_vectors):
    """Test the projection functionality."""
    seminorm = CoordinateProjectionSeminorm(sample_projection_indices)
    
    # Test projection on the first sample vector
    x = sample_vectors[0]
    projected = seminorm._project(x)
    
    # Verify that only the specified indices have non-zero values
    for i in range(len(x)):
        if i in sample_projection_indices:
            assert projected[i] == x[i]
        else:
            assert projected[i] == 0.0

@pytest.mark.unit
@pytest.mark.parametrize("vector_idx, expected_norm", [
    (0, np.sqrt(1.0**2 + 3.0**2 + 5.0**2)),  # First vector
    (1, 0.0),  # Zero vector
    (2, np.sqrt(1.0**2 + 3.0**2 + 5.0**2)),  # Negative vector
    (3, np.sqrt(0.1**2 + 0.3**2 + 0.5**2))   # Small values
])
def test_evaluate(sample_projection_indices, sample_vectors, vector_idx, expected_norm):
    """Test the evaluate method with different vectors."""
    seminorm = CoordinateProjectionSeminorm(sample_projection_indices)
    x = sample_vectors[vector_idx]
    
    norm_value = seminorm.evaluate(x)
    assert np.isclose(norm_value, expected_norm)

@pytest.mark.unit
@pytest.mark.parametrize("alpha", [0.0, 1.0, -1.0, 2.5, -0.5])
def test_scale(sample_projection_indices, sample_vectors, alpha):
    """Test the scale method with various scaling factors."""
    seminorm = CoordinateProjectionSeminorm(sample_projection_indices)
    x = sample_vectors[0]  # Use the first sample vector
    
    # Direct evaluation of scaled vector
    direct_result = seminorm.evaluate(alpha * x)
    
    # Using the scale method
    scale_result = seminorm.scale(x, alpha)
    
    assert np.isclose(direct_result, scale_result)
    
    # Verify scalar homogeneity: p(αx) = |α|p(x)
    assert np.isclose(direct_result, abs(alpha) * seminorm.evaluate(x))

@pytest.mark.unit
@pytest.mark.parametrize("idx1, idx2", [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
def test_triangle_inequality(sample_projection_indices, sample_vectors, idx1, idx2):
    """Test that the triangle inequality holds for different vector pairs."""
    seminorm = CoordinateProjectionSeminorm(sample_projection_indices)
    x = sample_vectors[idx1]
    y = sample_vectors[idx2]
    
    # Verify p(x + y) <= p(x) + p(y)
    sum_norm = seminorm.evaluate(x + y)
    x_norm = seminorm.evaluate(x)
    y_norm = seminorm.evaluate(y)
    
    assert sum_norm <= x_norm + y_norm + 1e-10  # Adding small tolerance
    assert seminorm.triangle_inequality(x, y) is True

@pytest.mark.unit
@pytest.mark.parametrize("vector_idx, expected", [
    (0, False),  # Non-zero vector
    (1, True),   # Zero vector
])
def test_is_zero(sample_projection_indices, sample_vectors, vector_idx, expected):
    """Test the is_zero method for different vectors."""
    seminorm = CoordinateProjectionSeminorm(sample_projection_indices)
    x = sample_vectors[vector_idx]
    
    assert seminorm.is_zero(x) == expected

@pytest.mark.unit
def test_is_zero_with_tolerance():
    """Test the is_zero method with different tolerance values."""
    # Create a vector with very small values
    small_vector = np.array([1e-11, 1e-11, 1e-11, 1e-11, 1e-11])
    
    seminorm = CoordinateProjectionSeminorm([0, 1, 2, 3, 4])
    
    # With default tolerance (1e-10), this should be considered zero
    assert seminorm.is_zero(small_vector) is True
    
    # With smaller tolerance, it should not be considered zero
    assert seminorm.is_zero(small_vector, tolerance=1e-12) is False

@pytest.mark.unit
def test_is_definite():
    """Test the is_definite method."""
    # Empty projection indices
    seminorm_empty = CoordinateProjectionSeminorm([])
    assert seminorm_empty.is_definite() is False
    
    # Non-empty projection indices
    seminorm_nonempty = CoordinateProjectionSeminorm([0, 1, 2])
    # By default, is_definite returns False unless explicitly configured
    assert seminorm_nonempty.is_definite() is False

@pytest.mark.unit
def test_serialization(sample_projection_indices):
    """Test serialization and deserialization."""
    seminorm = CoordinateProjectionSeminorm(sample_projection_indices)
    
    # Serialize to JSON
    json_data = seminorm.model_dump_json()
    
    # Deserialize from JSON
    deserialized = CoordinateProjectionSeminorm.model_validate_json(json_data)
    
    # Check that the deserialized object has the same properties
    assert deserialized.projection_indices == seminorm.projection_indices
    assert deserialized.type == seminorm.type

@pytest.mark.unit
def test_edge_cases():
    """Test edge cases and potential issues."""
    # Test with indices out of range
    seminorm = CoordinateProjectionSeminorm([10, 20])
    vector = np.array([1.0, 2.0, 3.0])
    
    # Should not raise an error, just ignore the out-of-range indices
    norm_value = seminorm.evaluate(vector)
    assert norm_value == 0.0  # No valid indices to project onto
    
    # Test with empty projection indices
    empty_seminorm = CoordinateProjectionSeminorm([])
    assert empty_seminorm.evaluate(vector) == 0.0