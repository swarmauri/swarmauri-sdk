import logging
from typing import Callable, Dict

import numpy as np
import pytest

from swarmauri_standard.pseudometrics.FunctionDifferencePseudometric import (
    FunctionDifferencePseudometric,
)


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def simple_functions() -> Dict[str, Callable]:
    """
    Fixture providing simple test functions.

    Returns
    -------
    Dict[str, Callable]
        Dictionary of test functions
    """
    return {
        "f1": lambda x: x**2 if isinstance(x, (int, float)) else sum(x.values()),
        "f2": lambda x: 2 * x**2
        if isinstance(x, (int, float))
        else 2 * sum(x.values()),
        "f3": lambda x: x**3
        if isinstance(x, (int, float))
        else sum(v**2 for v in x.values()),
        "f4": lambda x: 0 if isinstance(x, (int, float)) else 0,
        "f5": lambda x: 1 if isinstance(x, (int, float)) else 1,
    }


@pytest.fixture
def fixed_points_pseudometric() -> FunctionDifferencePseudometric:
    """
    Fixture providing a FunctionDifferencePseudometric with fixed evaluation points.

    Returns
    -------
    FunctionDifferencePseudometric
        Pseudometric configured with fixed evaluation points
    """
    return FunctionDifferencePseudometric(
        evaluation_points=[-2, -1, 0, 1, 2], sampling_strategy="fixed", norm_type="l2"
    )


@pytest.fixture
def random_points_pseudometric() -> FunctionDifferencePseudometric:
    """
    Fixture providing a FunctionDifferencePseudometric with random sampling.

    Returns
    -------
    FunctionDifferencePseudometric
        Pseudometric configured with random sampling
    """
    return FunctionDifferencePseudometric(
        num_samples=10,
        sampling_strategy="random",
        domain_bounds={"x": (-5, 5)},
        norm_type="l2",
    )


@pytest.fixture
def grid_points_pseudometric() -> FunctionDifferencePseudometric:
    """
    Fixture providing a FunctionDifferencePseudometric with grid sampling.

    Returns
    -------
    FunctionDifferencePseudometric
        Pseudometric configured with grid sampling
    """
    return FunctionDifferencePseudometric(
        num_samples=9,
        sampling_strategy="grid",
        domain_bounds={"x": (-2, 2), "y": (-2, 2)},
        norm_type="l2",
    )


@pytest.mark.unit
def test_type(fixed_points_pseudometric):
    """Test the type attribute of FunctionDifferencePseudometric."""
    assert fixed_points_pseudometric.type == "FunctionDifferencePseudometric"


@pytest.mark.unit
def test_initialization_fixed_points():
    """Test initialization with fixed evaluation points."""
    pseudometric = FunctionDifferencePseudometric(
        evaluation_points=[1, 2, 3, 4, 5], sampling_strategy="fixed", norm_type="l2"
    )
    assert pseudometric.evaluation_points == [1, 2, 3, 4, 5]
    assert pseudometric.sampling_strategy == "fixed"
    assert pseudometric.norm_type == "l2"


@pytest.mark.unit
def test_initialization_random_points():
    """Test initialization with random sampling."""
    pseudometric = FunctionDifferencePseudometric(
        num_samples=20,
        sampling_strategy="random",
        domain_bounds={"x": (-10, 10)},
        norm_type="l1",
    )
    assert pseudometric.num_samples == 20
    assert pseudometric.sampling_strategy == "random"
    assert pseudometric.domain_bounds == {"x": (-10, 10)}
    assert pseudometric.norm_type == "l1"

    # Check that sample points were generated
    assert pseudometric._sample_points is not None
    assert len(pseudometric._sample_points) == 20


@pytest.mark.unit
def test_initialization_grid_points():
    """Test initialization with grid sampling."""
    pseudometric = FunctionDifferencePseudometric(
        num_samples=16,
        sampling_strategy="grid",
        domain_bounds={"x": (-1, 1), "y": (-1, 1)},
        norm_type="max",
    )
    assert pseudometric.num_samples == 16
    assert pseudometric.sampling_strategy == "grid"
    assert pseudometric.domain_bounds == {"x": (-1, 1), "y": (-1, 1)}
    assert pseudometric.norm_type == "max"

    # Check that sample points were generated
    assert pseudometric._sample_points is not None
    assert (
        len(pseudometric._sample_points) <= 16
    )  # Could be less if we have fewer grid points


@pytest.mark.unit
def test_initialization_validation():
    """Test validation during initialization."""
    # Missing evaluation_points with fixed sampling
    with pytest.raises(ValueError):
        FunctionDifferencePseudometric(sampling_strategy="fixed", norm_type="l2")

    # Missing domain_bounds with random sampling
    with pytest.raises(ValueError):
        FunctionDifferencePseudometric(sampling_strategy="random", norm_type="l2")

    # Invalid norm_type
    with pytest.raises(ValueError):
        FunctionDifferencePseudometric(
            evaluation_points=[1, 2, 3], sampling_strategy="fixed", norm_type="invalid"
        )


@pytest.mark.unit
def test_generate_random_points():
    """Test generation of random sample points."""
    pseudometric = FunctionDifferencePseudometric(
        num_samples=30,
        sampling_strategy="random",
        domain_bounds={"x": (-5, 5)},
        norm_type="l2",
    )

    # Check that all points are within bounds
    for point in pseudometric._sample_points:
        assert -5 <= point <= 5

    # Test with multi-dimensional domain
    pseudometric = FunctionDifferencePseudometric(
        num_samples=30,
        sampling_strategy="random",
        domain_bounds={"x": (-5, 5), "y": (0, 10)},
        norm_type="l2",
    )

    # Check that all points are within bounds
    for point in pseudometric._sample_points:
        assert -5 <= point["x"] <= 5
        assert 0 <= point["y"] <= 10


@pytest.mark.unit
def test_generate_grid_points():
    """Test generation of grid sample points."""
    # 1D grid
    pseudometric = FunctionDifferencePseudometric(
        num_samples=5,
        sampling_strategy="grid",
        domain_bounds={"x": (0, 4)},
        norm_type="l2",
    )

    # Check that we have the expected points
    assert len(pseudometric._sample_points) == 5
    assert min(pseudometric._sample_points) == 0
    assert max(pseudometric._sample_points) == 4

    # 2D grid
    pseudometric = FunctionDifferencePseudometric(
        num_samples=9,
        sampling_strategy="grid",
        domain_bounds={"x": (0, 2), "y": (0, 2)},
        norm_type="l2",
    )

    # Check that we have the expected number of points and they're within bounds
    assert len(pseudometric._sample_points) <= 9
    for point in pseudometric._sample_points:
        assert 0 <= point["x"] <= 2
        assert 0 <= point["y"] <= 2


@pytest.mark.unit
def test_distance_calculation(fixed_points_pseudometric, simple_functions):
    """Test distance calculation between functions."""
    f1 = simple_functions["f1"]
    f2 = simple_functions["f2"]
    f3 = simple_functions["f3"]

    # Calculate distances
    d12 = fixed_points_pseudometric.distance(f1, f2)
    d13 = fixed_points_pseudometric.distance(f1, f3)
    d23 = fixed_points_pseudometric.distance(f2, f3)

    # Check that the distances are reasonable
    assert d12 > 0
    assert d13 > 0
    assert d23 > 0

    # Distance to self should be 0
    assert fixed_points_pseudometric.distance(f1, f1) == 0

    # Check that the triangle inequality holds
    assert d13 <= d12 + d23 + 1e-10


@pytest.mark.unit
def test_different_norm_types(simple_functions):
    """Test distance calculation with different norm types."""
    f1 = simple_functions["f1"]
    f2 = simple_functions["f2"]

    # Create pseudometrics with different norms
    l1_metric = FunctionDifferencePseudometric(
        evaluation_points=[-2, -1, 0, 1, 2], sampling_strategy="fixed", norm_type="l1"
    )

    l2_metric = FunctionDifferencePseudometric(
        evaluation_points=[-2, -1, 0, 1, 2], sampling_strategy="fixed", norm_type="l2"
    )

    max_metric = FunctionDifferencePseudometric(
        evaluation_points=[-2, -1, 0, 1, 2], sampling_strategy="fixed", norm_type="max"
    )

    # Calculate distances with different norms
    d_l1 = l1_metric.distance(f1, f2)
    d_l2 = l2_metric.distance(f1, f2)
    d_max = max_metric.distance(f1, f2)

    # Verify that the distances are different
    assert d_l1 != d_l2
    assert d_l1 != d_max
    assert d_l2 != d_max

    # Check that the distances follow the expected relationships
    # For the given functions and points, we expect l1 >= l2 >= max
    assert d_l1 >= d_l2
    assert d_l2 >= d_max


@pytest.mark.unit
def test_distances_pairwise(fixed_points_pseudometric, simple_functions):
    """Test pairwise distance calculation."""
    functions = [simple_functions["f1"], simple_functions["f2"], simple_functions["f3"]]

    # Calculate pairwise distances
    distances = fixed_points_pseudometric.distances(functions, functions)

    # Check dimensions
    assert len(distances) == 3
    assert len(distances[0]) == 3

    # Check diagonal elements (distance to self should be 0)
    for i in range(3):
        assert distances[i][i] == 0

    # Check symmetry
    for i in range(3):
        for j in range(3):
            assert abs(distances[i][j] - distances[j][i]) < 1e-10


@pytest.mark.unit
def test_pseudometric_properties(fixed_points_pseudometric, simple_functions):
    """Test that the pseudometric satisfies the required properties."""
    f1 = simple_functions["f1"]
    f2 = simple_functions["f2"]
    f3 = simple_functions["f3"]

    # Non-negativity
    assert fixed_points_pseudometric.check_non_negativity(f1, f2)

    # Symmetry
    assert fixed_points_pseudometric.check_symmetry(f1, f2)

    # Triangle inequality
    assert fixed_points_pseudometric.check_triangle_inequality(f1, f2, f3)

    # Weak identity (functions that are equal at evaluation points)
    assert fixed_points_pseudometric.check_weak_identity(f1, f1)


@pytest.mark.unit
def test_serialization_deserialization():
    """Test serialization and deserialization of the pseudometric."""
    original = FunctionDifferencePseudometric(
        evaluation_points=[1, 2, 3, 4, 5], sampling_strategy="fixed", norm_type="l2"
    )

    # Convert to dict
    data = original.to_dict()

    # Check dict contents
    assert data["type"] == "FunctionDifferencePseudometric"
    assert data["evaluation_points"] == [1, 2, 3, 4, 5]
    assert data["sampling_strategy"] == "fixed"
    assert data["norm_type"] == "l2"

    # Reconstruct from dict
    reconstructed = FunctionDifferencePseudometric.from_dict(data)

    # Check reconstructed object
    assert reconstructed.evaluation_points == [1, 2, 3, 4, 5]
    assert reconstructed.sampling_strategy == "fixed"
    assert reconstructed.norm_type == "l2"


@pytest.mark.unit
def test_error_handling(fixed_points_pseudometric):
    """Test error handling for invalid inputs."""
    # Non-callable inputs
    with pytest.raises(TypeError):
        fixed_points_pseudometric.distance(5, lambda x: x)

    with pytest.raises(TypeError):
        fixed_points_pseudometric.distance(lambda x: x, "not callable")

    # Functions that can't be evaluated
    def bad_function(x):
        raise ValueError("Cannot evaluate")

    with pytest.raises(ValueError):
        fixed_points_pseudometric.distance(lambda x: x, bad_function)


@pytest.mark.unit
def test_with_multidimensional_input(grid_points_pseudometric, simple_functions):
    """Test with multidimensional input points."""
    f1 = simple_functions["f1"]
    f2 = simple_functions["f2"]

    # Calculate distance
    distance = grid_points_pseudometric.distance(f1, f2)

    # Distance should be positive
    assert distance > 0

    # Distance to self should be 0
    assert grid_points_pseudometric.distance(f1, f1) == 0


@pytest.mark.unit
def test_with_constant_functions(fixed_points_pseudometric, simple_functions):
    """Test with constant functions."""
    f4 = simple_functions["f4"]  # Always returns 0
    f5 = simple_functions["f5"]  # Always returns 1

    # Distance between different constants should be positive
    assert fixed_points_pseudometric.distance(f4, f5) > 0

    # Distance to self should be 0
    assert fixed_points_pseudometric.distance(f4, f4) == 0
    assert fixed_points_pseudometric.distance(f5, f5) == 0

    # Distance between f4 and f5 should be sqrt(5) with L2 norm
    # (5 points, difference of 1 at each point)
    expected_distance = np.sqrt(5)
    actual_distance = fixed_points_pseudometric.distance(f4, f5)
    assert abs(actual_distance - expected_distance) < 1e-10


@pytest.mark.unit
def test_evaluate_function(fixed_points_pseudometric):
    """Test the internal _evaluate_function method."""

    # Simple function
    def func(x):
        return x**2

    points = [-2, -1, 0, 1, 2]

    # Expected values: [4, 1, 0, 1, 4]
    expected = [4.0, 1.0, 0.0, 1.0, 4.0]
    actual = fixed_points_pseudometric._evaluate_function(func, points)

    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert abs(a - e) < 1e-10


@pytest.mark.unit
def test_calculate_difference(fixed_points_pseudometric):
    """Test the internal _calculate_difference method."""
    # Test with L2 norm
    values1 = [1, 2, 3, 4, 5]
    values2 = [1, 3, 5, 7, 9]

    # Expected difference: sqrt((0)^2 + (1)^2 + (2)^2 + (3)^2 + (4)^2) = sqrt(30)
    expected_l2 = np.sqrt(30)
    actual_l2 = fixed_points_pseudometric._calculate_difference(values1, values2)

    assert abs(actual_l2 - expected_l2) < 1e-10

    # Test with L1 norm
    l1_metric = FunctionDifferencePseudometric(
        evaluation_points=[-2, -1, 0, 1, 2], sampling_strategy="fixed", norm_type="l1"
    )

    # Expected difference: |0| + |1| + |2| + |3| + |4| = 10
    expected_l1 = 10
    actual_l1 = l1_metric._calculate_difference(values1, values2)

    assert abs(actual_l1 - expected_l1) < 1e-10

    # Test with max norm
    max_metric = FunctionDifferencePseudometric(
        evaluation_points=[-2, -1, 0, 1, 2], sampling_strategy="fixed", norm_type="max"
    )

    # Expected difference: max(|0|, |1|, |2|, |3|, |4|) = 4
    expected_max = 4
    actual_max = max_metric._calculate_difference(values1, values2)

    assert abs(actual_max - expected_max) < 1e-10
