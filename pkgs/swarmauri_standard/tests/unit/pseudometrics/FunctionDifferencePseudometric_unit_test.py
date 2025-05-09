import pytest
import logging
from swarmauri_standard.swarmauri_standard.pseudometrics.FunctionDifferencePseudometric import FunctionDifferencePseudometric

@pytest.mark.unit
def test_function_difference_pseudometric_resource() -> None:
    """Tests that the FunctionDifferencePseudometric resource is correctly set."""
    assert FunctionDifferencePseudometric.resource == "PSEUDOMETRIC"

@pytest.mark.unit
def test_function_difference_pseudometric_type() -> None:
    """Tests that the FunctionDifferencePseudometric type is correctly set."""
    assert FunctionDifferencePseudometric.type == "FunctionDifferencePseudometric"

@pytest.mark.unit
def test_function_difference_pseudometric_distance() -> None:
    """Tests the distance calculation between two functions."""
    # Define test functions
    def f1(x: float) -> float:
        return x
        
    def f2(x: float) -> float:
        return 2 * x
        
    # Initialize pseudometric with evaluation points
    pseudometric = FunctionDifferencePseudometric(evaluation_points=[1.0, 2.0, 3.0])
    
    # Compute distance
    distance = pseudometric.distance(f1, f2)
    
    # Expected average difference
    expected_average = (abs(1 - 2) + abs(2 - 4) + abs(3 - 6)) / 3
    assert distance == expected_average

@pytest.mark.unit
def test_function_difference_pseudometric_distances() -> None:
    """Tests pairwise distance calculations for multiple function pairs."""
    # Define test functions
    def f1(x: float) -> float:
        return x
        
    def f2(x: float) -> float:
        return 2 * x
        
    def f3(x: float) -> float:
        return 3 * x
        
    # Initialize pseudometric
    pseudometric = FunctionDifferencePseudometric(evaluation_points=[1.0, 2.0])
    
    # Compute pairwise distances
    distances = pseudometric.distances([f1, f2], [f2, f3])
    
    # Expected distances
    expected_distances = [
        (abs(1 - 2) + abs(2 - 4)) / 2,
        (abs(2 - 4) + abs(4 - 6)) / 2
    ]
    
    assert len(distances) == 2
    assert distances == expected_distances

@pytest.mark.unit
def test_function_difference_pseudometric_evaluation_points_generation() -> None:
    """Tests that evaluation points are generated when not provided."""
    # Initialize without evaluation points
    pseudometric = FunctionDifferencePseudometric(num_evaluation_points=3)
    
    # Define test function
    def f(x: float) -> float:
        return x
        
    # Compute distance to ensure points are generated
    distance = pseudometric.distance(f, f)
    
    # The distance should be 0 since both functions are identical
    assert distance == 0.0

@pytest.mark.unit
def test_function_difference_pseudometric_invalid_evaluation_points() -> None:
    """Tests that invalid evaluation points raise appropriate errors."""
    # Initialize with invalid evaluation points
    pseudometric = FunctionDifferencePseudometric(evaluation_points=[-1.0, 2.0])
    
    # Define function that raises error for negative inputs
    def f(x: float) -> float:
        if x < 0:
            raise ValueError("Negative input not allowed")
        return x
        
    # Compute distance which should raise ValueError
    with pytest.raises(ValueError):
        pseudometric.distance(f, f)

@pytest.mark.unit
def test_function_difference_pseudometric_invalid_input() -> None:
    """Tests that invalid input during initialization raises ValueError."""
    # Test case where both evaluation_points and num_evaluation_points are None
    with pytest.raises(ValueError):
        FunctionDifferencePseudometric()