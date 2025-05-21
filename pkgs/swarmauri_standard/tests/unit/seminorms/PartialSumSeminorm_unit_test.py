import logging

import numpy as np
import pytest

from swarmauri_standard.seminorms.PartialSumSeminorm import PartialSumSeminorm

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def default_seminorm():
    """
    Fixture for a default PartialSumSeminorm instance.

    Returns
    -------
    PartialSumSeminorm
        A default instance with no specific configuration
    """
    return PartialSumSeminorm()


@pytest.fixture
def range_seminorm():
    """
    Fixture for a PartialSumSeminorm with a specific range.

    Returns
    -------
    PartialSumSeminorm
        An instance configured to use elements from index 1 to 3
    """
    return PartialSumSeminorm(start_idx=1, end_idx=3)


@pytest.fixture
def indices_seminorm():
    """
    Fixture for a PartialSumSeminorm with specific indices.

    Returns
    -------
    PartialSumSeminorm
        An instance configured to use elements at indices 0, 2, and 4
    """
    return PartialSumSeminorm(indices=[0, 2, 4])


@pytest.mark.unit
def test_initialization():
    """Test the initialization of PartialSumSeminorm with various parameters."""
    # Test default initialization
    seminorm1 = PartialSumSeminorm()
    assert seminorm1.start_idx is None
    assert seminorm1.end_idx is None
    assert seminorm1.indices is None

    # Test initialization with range
    seminorm2 = PartialSumSeminorm(start_idx=1, end_idx=5)
    assert seminorm2.start_idx == 1
    assert seminorm2.end_idx == 5
    assert seminorm2.indices is None

    # Test initialization with indices
    seminorm3 = PartialSumSeminorm(indices=[0, 2, 4])
    assert seminorm3.start_idx is None
    assert seminorm3.end_idx is None
    assert seminorm3.indices == [0, 2, 4]

    # Test initialization with both range and indices (indices should take precedence)
    seminorm4 = PartialSumSeminorm(start_idx=1, end_idx=5, indices=[0, 2, 4])
    assert seminorm4.start_idx == 1
    assert seminorm4.end_idx == 5
    assert seminorm4.indices == [0, 2, 4]


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    seminorm = PartialSumSeminorm()
    assert seminorm.type == "PartialSumSeminorm"


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_vector, expected_output",
    [
        ([1, 2, 3, 4, 5], 15),  # Sum of all elements
        ([-1, 2, -3, 4, -5], 15),  # Sum of absolute values
        ([0, 0, 0, 0, 0], 0),  # Zero vector
    ],
)
def test_compute_default(default_seminorm, input_vector, expected_output):
    """Test computation with default seminorm (no range or indices specified)."""
    result = default_seminorm.compute(input_vector)
    assert result == expected_output


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_vector, expected_output",
    [
        ([1, 2, 3, 4, 5], 5),  # Sum of elements at indices 1 and 2 (2+3)
        ([-1, 2, -3, 4, -5], 5),  # Sum of absolute values at indices 1 and 2 (2+3)
        ([0, 0, 0, 0, 0], 0),  # Zero vector
    ],
)
def test_compute_range(range_seminorm, input_vector, expected_output):
    """Test computation with range-based seminorm."""
    result = range_seminorm.compute(input_vector)
    assert result == expected_output


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_vector, expected_output",
    [
        ([1, 2, 3, 4, 5], 9),  # Sum of elements at indices 0, 2, 4 (1+3+5)
        ([-1, 2, -3, 4, -5], 9),  # Sum of absolute values at indices 0, 2, 4 (1+3+5)
        ([0, 0, 0, 0, 0], 0),  # Zero vector
    ],
)
def test_compute_indices(indices_seminorm, input_vector, expected_output):
    """Test computation with indices-based seminorm."""
    result = indices_seminorm.compute(input_vector)
    assert result == expected_output


@pytest.mark.unit
def test_compute_with_matrix():
    """Test computation with matrix input."""
    # Create a matrix
    matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    # Test with default seminorm
    default_seminorm = PartialSumSeminorm()
    result = default_seminorm.compute(matrix)
    assert result == 45  # Sum of all elements

    # Test with range seminorm
    range_seminorm = PartialSumSeminorm(start_idx=1, end_idx=5)
    result = range_seminorm.compute(matrix)
    # Matrix flattened: [1,2,3,4,5,6,7,8,9], so indices 1-4 are [2,3,4,5]
    assert result == 14

    # Test with indices seminorm
    indices_seminorm = PartialSumSeminorm(indices=[0, 4, 8])
    result = indices_seminorm.compute(matrix)
    # Indices 0, 4, 8 correspond to elements 1, 5, 9
    assert result == 15


@pytest.mark.unit
def test_compute_with_string():
    """Test computation with string input."""
    # Create a string
    test_string = "hello"

    # ASCII values: h=104, e=101, l=108, l=108, o=111
    # Total sum: 532

    # Test with default seminorm
    default_seminorm = PartialSumSeminorm()
    result = default_seminorm.compute(test_string)
    assert result == 532

    # Test with range seminorm
    range_seminorm = PartialSumSeminorm(start_idx=1, end_idx=3)
    result = range_seminorm.compute(test_string)
    # Elements at indices 1-2: e=101, l=108
    assert result == 209

    # Test with indices seminorm
    indices_seminorm = PartialSumSeminorm(indices=[0, 4])
    result = indices_seminorm.compute(test_string)
    # Elements at indices 0, 4: h=104, o=111
    assert result == 215


@pytest.mark.unit
def test_compute_with_callable():
    """Test computation with callable input."""

    # Create a callable function
    def test_function(x):
        return x**2

    # Test with default seminorm
    default_seminorm = PartialSumSeminorm()
    result = default_seminorm.compute(test_function)
    # This should evaluate the function at 100 points and sum the absolute values
    assert result > 0  # The exact value depends on the implementation details

    # Test with range seminorm
    range_seminorm = PartialSumSeminorm(start_idx=10, end_idx=20)
    result = range_seminorm.compute(test_function)
    assert result > 0

    # Test with indices seminorm
    indices_seminorm = PartialSumSeminorm(indices=[0, 50, 99])
    result = indices_seminorm.compute(test_function)
    assert result > 0


@pytest.mark.unit
def test_extract_partial_data():
    """Test the _extract_partial_data private method."""
    data = [1, 2, 3, 4, 5]

    # Test with default seminorm
    default_seminorm = PartialSumSeminorm()
    result = default_seminorm._extract_partial_data(data)
    np.testing.assert_array_equal(result, np.array([1, 2, 3, 4, 5]))

    # Test with range seminorm
    range_seminorm = PartialSumSeminorm(start_idx=1, end_idx=3)
    result = range_seminorm._extract_partial_data(data)
    np.testing.assert_array_equal(result, np.array([2, 3]))

    # Test with indices seminorm
    indices_seminorm = PartialSumSeminorm(indices=[0, 2, 4])
    result = indices_seminorm._extract_partial_data(data)
    np.testing.assert_array_equal(result, np.array([1, 3, 5]))


@pytest.mark.unit
def test_extract_partial_data_out_of_bounds():
    """Test that _extract_partial_data raises ValueError for out-of-bounds indices."""
    data = [1, 2, 3, 4, 5]

    # Test with out-of-bounds range
    range_seminorm = PartialSumSeminorm(start_idx=1, end_idx=10)
    with pytest.raises(ValueError):
        range_seminorm._extract_partial_data(data)

    # Test with out-of-bounds indices
    indices_seminorm = PartialSumSeminorm(indices=[0, 10])
    with pytest.raises(ValueError):
        indices_seminorm._extract_partial_data(data)


@pytest.mark.unit
def test_triangle_inequality():
    """Test the triangle inequality property of the seminorm."""
    # Create test vectors
    x = [1, 2, 3, 4, 5]
    y = [5, 4, 3, 2, 1]

    # Test with different seminorm configurations
    default_seminorm = PartialSumSeminorm()
    assert default_seminorm.check_triangle_inequality(x, y)

    range_seminorm = PartialSumSeminorm(start_idx=1, end_idx=3)
    assert range_seminorm.check_triangle_inequality(x, y)

    indices_seminorm = PartialSumSeminorm(indices=[0, 2, 4])
    assert indices_seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_scalar_homogeneity():
    """Test the scalar homogeneity property of the seminorm."""
    # Create test vector
    x = [1, 2, 3, 4, 5]
    alpha = 2.5

    # Test with different seminorm configurations
    default_seminorm = PartialSumSeminorm()
    assert default_seminorm.check_scalar_homogeneity(x, alpha)

    range_seminorm = PartialSumSeminorm(start_idx=1, end_idx=3)
    assert range_seminorm.check_scalar_homogeneity(x, alpha)

    indices_seminorm = PartialSumSeminorm(indices=[0, 2, 4])
    assert indices_seminorm.check_scalar_homogeneity(x, alpha)


@pytest.mark.unit
def test_incompatible_inputs_triangle_inequality():
    """Test that check_triangle_inequality raises TypeError for incompatible inputs."""
    seminorm = PartialSumSeminorm()

    # Different types
    with pytest.raises(TypeError):
        seminorm.check_triangle_inequality([1, 2, 3], "abc")

    # Different lengths
    with pytest.raises(ValueError):
        seminorm.check_triangle_inequality([1, 2, 3], [1, 2, 3, 4])


@pytest.mark.unit
def test_unsupported_input_type():
    """Test that compute raises TypeError for unsupported input types."""
    seminorm = PartialSumSeminorm()

    # Complex object that's not handled
    class UnsupportedType:
        pass

    with pytest.raises(TypeError):
        seminorm.compute(UnsupportedType())


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of PartialSumSeminorm."""
    # Create a seminorm with specific configuration
    original = PartialSumSeminorm(start_idx=1, end_idx=5, indices=[0, 2, 4])

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize from JSON
    deserialized = PartialSumSeminorm.model_validate_json(json_data)

    # Check that all attributes are preserved
    assert deserialized.start_idx == original.start_idx
    assert deserialized.end_idx == original.end_idx
    assert deserialized.indices == original.indices
    assert deserialized.type == original.type
