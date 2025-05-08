import pytest
import logging
import numpy as np
from typing import Callable, List, Tuple, Any
from unittest.mock import Mock, patch
from swarmauri_standard.pseudometrics.FunctionDifferencePseudometric import FunctionDifferencePseudometric

# Setup logging
logger = logging.getLogger(__name__)

# Define test functions
def linear_func(x: float) -> float:
    return x

def squared_func(x: float) -> float:
    return x * x

def constant_func(x: float) -> float:
    return 5.0

def custom_sampler() -> List[float]:
    return [0.1, 0.2, 0.3, 0.4, 0.5]

# Fixtures
@pytest.fixture
def default_pseudometric():
    """Fixture for default FunctionDifferencePseudometric instance."""
    return FunctionDifferencePseudometric()

@pytest.fixture
def custom_pseudometric():
    """Fixture for customized FunctionDifferencePseudometric instance."""
    return FunctionDifferencePseudometric(
        evaluation_points=[0.0, 0.5, 1.0],
        norm_type=1,
        seed=42
    )

@pytest.fixture
def custom_sampling_pseudometric():
    """Fixture for FunctionDifferencePseudometric with custom sampling."""
    return FunctionDifferencePseudometric(
        sampling_strategy="custom",
        custom_sampler=custom_sampler,
        seed=42
    )

# Unit tests
@pytest.mark.unit
def test_initialization_default():
    """Test default initialization of FunctionDifferencePseudometric."""
    metric = FunctionDifferencePseudometric()
    assert metric.type == "FunctionDifferencePseudometric"
    assert metric.norm_type == 2
    assert metric.sample_size == 100
    assert metric.sampling_strategy == "uniform"
    assert metric.domain_bounds == (0, 1)
    assert len(metric.evaluation_points) == 100

@pytest.mark.unit
def test_initialization_with_params():
    """Test initialization with custom parameters."""
    eval_points = [0.1, 0.2, 0.3]
    metric = FunctionDifferencePseudometric(
        evaluation_points=eval_points,
        norm_type="inf",
        sample_size=50,
        domain_bounds=(-1, 1),
        seed=42
    )
    assert metric.norm_type == "inf"
    assert metric.sample_size == 50
    assert metric.domain_bounds == (-1, 1)
    assert metric.evaluation_points == tuple(eval_points)

@pytest.mark.unit
@pytest.mark.parametrize("sampling_strategy,domain_bounds,expected_length", [
    ("uniform", (0, 1), 100),
    ("random", (-10, 10), 100),
])
def test_generate_evaluation_points(sampling_strategy, domain_bounds, expected_length):
    """Test generation of evaluation points with different strategies."""
    metric = FunctionDifferencePseudometric(
        sampling_strategy=sampling_strategy,
        domain_bounds=domain_bounds,
        sample_size=expected_length,
        seed=42
    )
    assert len(metric.evaluation_points) == expected_length
    # Check that points are within domain bounds
    assert all(domain_bounds[0] <= p <= domain_bounds[1] for p in metric.evaluation_points)

@pytest.mark.unit
def test_custom_sampling_strategy():
    """Test custom sampling strategy."""
    metric = FunctionDifferencePseudometric(
        sampling_strategy="custom",
        custom_sampler=custom_sampler,
        seed=42
    )
    assert metric.evaluation_points == tuple(custom_sampler())

@pytest.mark.unit
def test_invalid_sampling_strategy():
    """Test that invalid sampling strategy raises ValueError."""
    with pytest.raises(ValueError):
        FunctionDifferencePseudometric(sampling_strategy="invalid")

@pytest.mark.unit
def test_missing_custom_sampler():
    """Test that missing custom sampler raises ValueError."""
    with pytest.raises(ValueError):
        FunctionDifferencePseudometric(sampling_strategy="custom")

@pytest.mark.unit
def test_distance_identical_functions(default_pseudometric):
    """Test distance between identical functions is zero."""
    distance = default_pseudometric.distance(linear_func, linear_func)
    assert distance == 0.0

@pytest.mark.unit
@pytest.mark.parametrize("norm_type,expected", [
    (1, 25.0),  # Sum of absolute differences
    (2, 5.0),   # Euclidean distance (square root of sum of squares)
    ("inf", 1.0)  # Maximum absolute difference
])
def test_distance_with_different_norms(norm_type, expected):
    """Test distance calculation with different norm types."""
    # Use fixed evaluation points for predictable results
    metric = FunctionDifferencePseudometric(
        evaluation_points=[0.0, 0.5, 1.0, 1.5, 2.0],
        norm_type=norm_type
    )
    
    # For these functions and points, we can calculate expected values:
    # Points: [0.0, 0.5, 1.0, 1.5, 2.0]
    # linear_func outputs: [0.0, 0.5, 1.0, 1.5, 2.0]
    # constant_func outputs: [5.0, 5.0, 5.0, 5.0, 5.0]
    # Differences: [5.0, 4.5, 4.0, 3.5, 3.0]
    # L1 norm: 5.0 + 4.5 + 4.0 + 3.5 + 3.0 = 20.0
    # L2 norm: sqrt(5.0² + 4.5² + 4.0² + 3.5² + 3.0²) ≈ 9.0
    # L∞ norm: max(5.0, 4.5, 4.0, 3.5, 3.0) = 5.0
    
    distance = metric.distance(linear_func, constant_func)
    assert pytest.approx(distance, rel=1e-5) == expected

@pytest.mark.unit
def test_batch_distance(custom_pseudometric):
    """Test batch distance calculation."""
    funcs1 = [linear_func, squared_func]
    funcs2 = [constant_func, linear_func]
    
    distances = custom_pseudometric.batch_distance(funcs1, funcs2)
    assert len(distances) == 2
    
    # Verify by comparing with individual distance calls
    expected = [
        custom_pseudometric.distance(linear_func, constant_func),
        custom_pseudometric.distance(squared_func, linear_func)
    ]
    assert distances == expected

@pytest.mark.unit
def test_batch_distance_unequal_lengths(custom_pseudometric):
    """Test batch distance with unequal list lengths raises ValueError."""
    funcs1 = [linear_func, squared_func]
    funcs2 = [constant_func]
    
    with pytest.raises(ValueError):
        custom_pseudometric.batch_distance(funcs1, funcs2)

@pytest.mark.unit
def test_pairwise_distances(custom_pseudometric):
    """Test pairwise distance calculation."""
    funcs = [linear_func, squared_func, constant_func]
    
    distance_matrix = custom_pseudometric.pairwise_distances(funcs)
    assert len(distance_matrix) == 3
    assert all(len(row) == 3 for row in distance_matrix)
    
    # Check symmetry
    for i in range(3):
        for j in range(3):
            assert distance_matrix[i][j] == distance_matrix[j][i]
    
    # Check diagonal is zero
    for i in range(3):
        assert distance_matrix[i][i] == 0.0
    
    # Check specific values match individual distance calls
    assert distance_matrix[0][1] == custom_pseudometric.distance(linear_func, squared_func)
    assert distance_matrix[0][2] == custom_pseudometric.distance(linear_func, constant_func)
    assert distance_matrix[1][2] == custom_pseudometric.distance(squared_func, constant_func)

@pytest.mark.unit
def test_add_evaluation_points(default_pseudometric):
    """Test adding evaluation points."""
    original_count = len(default_pseudometric.evaluation_points)
    new_points = [10.0, 20.0, 30.0]
    
    default_pseudometric.add_evaluation_points(new_points)
    
    assert len(default_pseudometric.evaluation_points) == original_count + len(new_points)
    # Check that new points are included
    for point in new_points:
        assert point in default_pseudometric.evaluation_points

@pytest.mark.unit
def test_set_evaluation_points(default_pseudometric):
    """Test setting evaluation points."""
    new_points = [1.1, 2.2, 3.3]
    
    default_pseudometric.set_evaluation_points(new_points)
    
    assert default_pseudometric.evaluation_points == tuple(new_points)

@pytest.mark.unit
def test_get_evaluation_points(default_pseudometric):
    """Test getting evaluation points."""
    points = default_pseudometric.get_evaluation_points()
    assert points == default_pseudometric.evaluation_points
    assert isinstance(points, tuple)

@pytest.mark.unit
def test_function_evaluation_caching(default_pseudometric):
    """Test that function evaluations are cached."""
    # Create a mock function that counts calls
    mock_func = Mock(side_effect=linear_func)
    
    # First call should evaluate at all points
    default_pseudometric._evaluate_function(mock_func)
    first_call_count = mock_func.call_count
    assert first_call_count == len(default_pseudometric.evaluation_points)
    
    # Second call should use cached values
    default_pseudometric._evaluate_function(mock_func)
    assert mock_func.call_count == first_call_count  # No additional calls
    
    # After changing evaluation points, cache should be invalidated
    default_pseudometric.add_evaluation_points([100.0])
    default_pseudometric._evaluate_function(mock_func)
    assert mock_func.call_count > first_call_count

@pytest.mark.unit
def test_function_evaluation_error_handling(default_pseudometric):
    """Test error handling during function evaluation."""
    def problematic_func(x):
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        default_pseudometric._evaluate_function(problematic_func)

@pytest.mark.unit
def test_compute_norm_invalid_type(default_pseudometric):
    """Test that invalid norm type raises ValueError."""
    default_pseudometric.norm_type = 3  # Invalid norm type
    with pytest.raises(ValueError):
        default_pseudometric._compute_norm(np.array([1.0, 2.0, 3.0]))

@pytest.mark.unit
def test_non_negativity_validation():
    """Test non-negativity validation."""
    metric = FunctionDifferencePseudometric()
    
    # This should not raise an exception
    metric._validate_non_negativity(0.0, linear_func, squared_func)
    metric._validate_non_negativity(5.0, linear_func, squared_func)
    
    # Negative distance should log a warning but not raise an exception
    with patch.object(logging.getLogger('swarmauri_standard.pseudometrics.FunctionDifferencePseudometric'),