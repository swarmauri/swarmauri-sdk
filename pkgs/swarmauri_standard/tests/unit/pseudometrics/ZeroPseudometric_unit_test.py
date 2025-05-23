import logging

import pytest
from unittest.mock import MagicMock
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.pseudometrics.ZeroPseudometric import ZeroPseudometric

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def zero_pseudometric() -> ZeroPseudometric:
    """
    Create a ZeroPseudometric instance for testing.

    Returns
    -------
    ZeroPseudometric
        An instance of ZeroPseudometric
    """
    return ZeroPseudometric()


@pytest.mark.unit
def test_type_attribute(zero_pseudometric):
    """
    Test that the type attribute is correctly set.
    """
    assert zero_pseudometric.type == "ZeroPseudometric"


@pytest.mark.unit
def test_distance_always_returns_zero(zero_pseudometric):
    """
    Test that the distance method always returns zero regardless of input.
    """
    # Test with various input types
    test_cases = [
        ([], []),  # Empty lists
        ([1, 2, 3], [4, 5, 6]),  # Lists with elements
        ("hello", "world"),  # Strings
        (lambda x: x, lambda x: x * 2),  # Functions
        (None, None),  # None values
        (0, 0),  # Integers
        (0.0, 1.0),  # Floats
    ]

    for x, y in test_cases:
        assert zero_pseudometric.distance(x, y) == 0.0


@pytest.mark.unit
def test_distances_returns_matrix_of_zeros(zero_pseudometric):
    """
    Test that the distances method returns a matrix of zeros with correct dimensions.
    """
    # Test cases with different collection sizes
    test_cases = [
        ([], []),  # Empty collections
        ([1], [2]),  # Single element collections
        ([1, 2, 3], [4, 5]),  # Different sized collections
        (["a", "b", "c"], ["d", "e", "f"]),  # String collections
    ]

    for xs, ys in test_cases:
        result = zero_pseudometric.distances(xs, ys)

        # Check dimensions
        assert len(result) == len(xs)
        if len(result) > 0:
            assert len(result[0]) == len(ys)

        # Check all values are zero
        for row in result:
            for val in row:
                assert val == 0.0


@pytest.mark.unit
def test_check_non_negativity(zero_pseudometric):
    """
    Test that check_non_negativity always returns True.
    """
    # Test with arbitrary inputs
    assert zero_pseudometric.check_non_negativity("any", "input") is True
    assert zero_pseudometric.check_non_negativity(123, 456) is True
    assert zero_pseudometric.check_non_negativity(None, None) is True


@pytest.mark.unit
def test_check_symmetry(zero_pseudometric):
    """
    Test that check_symmetry always returns True.
    """
    # Test with arbitrary inputs
    assert zero_pseudometric.check_symmetry("any", "input") is True
    assert zero_pseudometric.check_symmetry(123, 456) is True
    assert zero_pseudometric.check_symmetry(None, None) is True

    # Test with custom tolerance
    assert zero_pseudometric.check_symmetry("x", "y", tolerance=0.001) is True


@pytest.mark.unit
def test_check_triangle_inequality(zero_pseudometric):
    """
    Test that check_triangle_inequality always returns True.
    """
    # Test with arbitrary inputs
    assert zero_pseudometric.check_triangle_inequality("x", "y", "z") is True
    assert zero_pseudometric.check_triangle_inequality(1, 2, 3) is True
    assert zero_pseudometric.check_triangle_inequality(None, None, None) is True

    # Test with custom tolerance
    assert (
        zero_pseudometric.check_triangle_inequality("x", "y", "z", tolerance=0.001)
        is True
    )


@pytest.mark.unit
def test_check_weak_identity(zero_pseudometric):
    """
    Test that check_weak_identity always returns True.
    """
    # Test with arbitrary inputs
    assert zero_pseudometric.check_weak_identity("same", "same") is True
    assert zero_pseudometric.check_weak_identity("different1", "different2") is True
    assert zero_pseudometric.check_weak_identity(None, None) is True


@pytest.mark.unit
def test_string_representation(zero_pseudometric):
    """
    Test the string representation of ZeroPseudometric.
    """
    expected = "ZeroPseudometric (trivial pseudometric that returns 0 for all inputs)"
    assert str(zero_pseudometric) == expected


@pytest.mark.unit
def test_repr_representation(zero_pseudometric):
    """
    Test the repr representation of ZeroPseudometric.
    """
    expected = "ZeroPseudometric()"
    assert repr(zero_pseudometric) == expected


@pytest.mark.unit
def test_logging(zero_pseudometric, caplog):
    """
    Test that the class logs appropriate messages.
    """
    caplog.set_level(logging.DEBUG)

    # Call methods that should log
    zero_pseudometric.distance("a", "b")

    # Check that appropriate log messages were generated
    assert "Computing ZeroPseudometric distance" in caplog.text


@pytest.mark.unit
def test_with_mock_vector_and_matrix():
    """
    Test with mocked IVector and IMatrix objects to ensure compatibility.
    """
    zero_pseudometric = ZeroPseudometric()

    # Create proper mock objects using unittest.mock
    mock_vector1 = MagicMock(spec=IVector)
    mock_vector2 = MagicMock(spec=IVector)
    mock_matrix1 = MagicMock(spec=IMatrix)
    mock_matrix2 = MagicMock(spec=IMatrix)

    # Test distance with different combinations
    assert zero_pseudometric.distance(mock_vector1, mock_vector2) == 0.0
    assert zero_pseudometric.distance(mock_matrix1, mock_matrix2) == 0.0
    assert zero_pseudometric.distance(mock_vector1, mock_matrix1) == 0.0

    # Test distances with collections
    vectors = [mock_vector1, mock_vector2]
    matrices = [mock_matrix1, mock_matrix2]

    result = zero_pseudometric.distances(vectors, matrices)
    assert len(result) == 2
    assert len(result[0]) == 2
    assert all(val == 0.0 for row in result for val in row)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y",
    [
        ([], []),
        ([1, 2, 3], [4, 5, 6]),
        ("hello", "world"),
        (lambda x: x, lambda x: x * 2),
        (None, None),
    ],
)
def test_distance_parametrized(zero_pseudometric, x, y):
    """
    Test distance method with various input types using parameterization.

    Parameters
    ----------
    zero_pseudometric : ZeroPseudometric
        Instance of ZeroPseudometric
    x : Any
        First test input
    y : Any
        Second test input
    """
    assert zero_pseudometric.distance(x, y) == 0.0


@pytest.mark.unit
def test_serialization_deserialization():
    """
    Test that the ZeroPseudometric can be serialized and deserialized correctly.
    """
    zero_pseudometric = ZeroPseudometric()

    # Serialize to JSON
    json_data = zero_pseudometric.model_dump_json()

    # Deserialize from JSON
    deserialized = ZeroPseudometric.model_validate_json(json_data)

    # Check that the deserialized object has the correct type
    assert deserialized.type == "ZeroPseudometric"

    # Check that the deserialized object behaves the same
    assert deserialized.distance("a", "b") == 0.0
