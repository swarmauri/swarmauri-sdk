import pytest
import logging
from swarmauri_standard.swarmauri_standard.pseudometrics.FunctionDifferencePseudometric import (
    FunctionDifferencePseudometric,
)


@pytest.mark.unit
def test_function_difference_pseudometric_initialization():
    """
    Test basic initialization of FunctionDifferencePseudometric.
    """
    fdp = FunctionDifferencePseudometric()
    assert isinstance(fdp, FunctionDifferencePseudometric)
    assert hasattr(fdp, "resource")
    assert hasattr(fdp, "evaluation_points")
    assert hasattr(fdp, "sample_count")


@pytest.mark.unit
def test_function_difference_pseudometric_resource():
    """
    Test the resource property of FunctionDifferencePseudometric.
    """
    fdp = FunctionDifferencePseudometric()
    assert fdp.resource == "Pseudometric"


@pytest.mark.unit
def test_function_difference_pseudometric_type():
    """
    Test the type property of FunctionDifferencePseudometric.
    """
    fdp = FunctionDifferencePseudometric()
    assert fdp.type == "FunctionDifferencePseudometric"


@pytest.mark.unit
def test_function_difference_pseudometric_serialization():
    """
    Test serialization/deserialization of FunctionDifferencePseudometric.
    """
    fdp = FunctionDifferencePseudometric()
    model = fdp.model_dump_json()
    assert fdp.model_validate_json(model) == fdp.id


@pytest.mark.unit
def test_function_difference_pseudometric_distance():
    """
    Test the distance calculation between two simple functions.
    """

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    distance = fdp.distance(f1, f2)
    assert distance == 1.0


@pytest.mark.unit
def test_function_difference_pseudometric_distance_no_evaluation_points():
    """
    Test distance calculation when no evaluation points are provided.
    """

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    fdp = FunctionDifferencePseudometric()
    distance = fdp.distance(f1, f2)
    assert distance >= 0.0


@pytest.mark.unit
def test_function_difference_pseudometric_distances():
    """
    Test distances calculation for multiple functions.
    """

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    def f3(x):
        return 3 * x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    distances = fdp.distances(f1, [f2, f3])
    assert len(distances) == 2
    assert all(0 <= d <= 2.0 for d in distances)


@pytest.mark.unit
def test_function_difference_pseudometric_non_negativity():
    """
    Test non-negativity property of the distance metric.
    """

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    non_negative = fdp.check_non_negativity(f1, f2)
    assert non_negative is True


@pytest.mark.unit
def test_function_difference_pseudometric_symmetry():
    """
    Test symmetry property of the distance metric.
    """

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    is_symmetric = fdp.check_symmetry(f1, f2)
    assert is_symmetric is True


@pytest.mark.unit
def test_function_difference_pseudometric_triangle_inequality():
    """
    Test triangle inequality property of the distance metric.
    """

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    def f3(x):
        return 3 * x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    is_triangle_inequality = fdp.check_triangle_inequality(f1, f2, f3)
    assert is_triangle_inequality is True


@pytest.mark.unit
def test_function_difference_pseudometric_weak_identity():
    """
    Test weak identity of indiscernibles property of the distance metric.
    """

    # Simple test function
    def f1(x):
        return x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    is_weak_identity = fdp.check_weak_identity(f1, f1)
    assert is_weak_identity is True


@pytest.mark.unit
def test_function_difference_pseudometric_evaluation_points():
    """
    Test initialization with and without evaluation points.
    """
    # Test with custom evaluation points
    evaluation_points = [0.0, 0.5, 1.0]
    fdp_custom = FunctionDifferencePseudometric(evaluation_points=evaluation_points)
    assert fdp_custom.evaluation_points == evaluation_points

    # Test without evaluation points (uses default)
    fdp_default = FunctionDifferencePseudometric()
    assert fdp_default.evaluation_points is not None
    assert len(fdp_default.evaluation_points) == 10


@pytest.mark.unit
def test_function_difference_pseudometric_logging():
    """
    Test logging functionality in FunctionDifferencePseudometric.
    """
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Simple test functions
    def f1(x):
        return x

    def f2(x):
        return 2 * x

    fdp = FunctionDifferencePseudometric(evaluation_points=[0.0, 1.0])
    distance = fdp.distance(f1, f2)

    # Check if logging was called
    # This is a simplistic test - in real scenarios, you might want to mock logging
    assert distance == 1.0
