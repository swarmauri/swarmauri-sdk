import logging
import math

import numpy as np
import pytest
from unittest.mock import Mock
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase

from swarmauri_standard.pseudometrics.LpPseudometric import LpPseudometric

# Configure logging
logger = logging.getLogger(__name__)


@pytest.fixture
def default_pseudometric():
    """
    Fixture that returns a default LpPseudometric instance with p=2.

    Returns
    -------
    LpPseudometric
        A default LpPseudometric instance
    """
    return LpPseudometric()


@pytest.fixture
def custom_pseudometrics():
    """
    Fixture that returns various LpPseudometric instances with different parameters.

    Returns
    -------
    List[LpPseudometric]
        A list of LpPseudometric instances with different configurations
    """
    return [
        LpPseudometric(p=1),
        LpPseudometric(p=2),
        LpPseudometric(p=float("inf")),
        LpPseudometric(p=3, coordinates=[0, 1]),
        LpPseudometric(p=2, domain=(0, 1)),
    ]


@pytest.mark.unit
def test_inheritance():
    """Test that LpPseudometric inherits from PseudometricBase."""
    pseudometric = LpPseudometric()
    assert isinstance(pseudometric, PseudometricBase)


@pytest.mark.unit
def test_type_property():
    """Test that the type property is correctly set."""
    pseudometric = LpPseudometric()
    assert pseudometric.type == "LpPseudometric"


@pytest.mark.unit
def test_init_default_parameters(default_pseudometric):
    """Test that initialization with default parameters works correctly."""
    assert default_pseudometric.p == 2.0
    assert default_pseudometric.domain is None
    assert default_pseudometric.coordinates is None
    assert default_pseudometric.epsilon == 1e-10


@pytest.mark.unit
@pytest.mark.parametrize(
    "p,domain,coordinates,epsilon",
    [
        (1.0, None, None, 1e-10),
        (2.0, (0, 1), None, 1e-10),
        (3.0, None, [0, 1, 2], 1e-10),
        (float("inf"), (-1, 1), [0], 1e-8),
    ],
)
def test_init_custom_parameters(p, domain, coordinates, epsilon):
    """Test that initialization with custom parameters works correctly."""
    pseudometric = LpPseudometric(
        p=p, domain=domain, coordinates=coordinates, epsilon=epsilon
    )
    assert pseudometric.p == p
    assert pseudometric.domain == domain
    assert pseudometric.coordinates == coordinates
    assert pseudometric.epsilon == epsilon


@pytest.mark.unit
@pytest.mark.parametrize("invalid_p", [0.0, -1.0, 0.5])
def test_init_invalid_p(invalid_p):
    """Test that initialization with invalid p values raises ValueError."""
    with pytest.raises(ValueError, match="Parameter p must be at least 1"):
        LpPseudometric(p=invalid_p)


@pytest.mark.unit
@pytest.mark.parametrize("invalid_domain", [(1, 0), (0, 0), (1, 1)])
def test_init_invalid_domain(invalid_domain):
    """Test that initialization with invalid domain raises ValueError."""
    with pytest.raises(ValueError, match="Domain must be a valid interval"):
        LpPseudometric(domain=invalid_domain)


@pytest.mark.unit
def test_init_invalid_coordinates():
    """Test that initialization with invalid coordinates raises ValueError."""
    with pytest.raises(
        ValueError, match="Coordinates must contain non-negative indices"
    ):
        LpPseudometric(coordinates=[-1, 0, 1])


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y,expected",
    [
        ([0, 0, 0], [0, 0, 0], 0.0),
        ([1, 0, 0], [0, 0, 0], 1.0),
        ([1, 1, 0], [0, 0, 0], math.sqrt(2)),
        ([1, 1, 1], [0, 0, 0], math.sqrt(3)),
        ([3, 4], [0, 0], 5.0),
    ],
)
def test_distance_euclidean(default_pseudometric, x, y, expected):
    """Test the Euclidean distance (p=2) calculation."""
    assert math.isclose(default_pseudometric.distance(x, y), expected, abs_tol=1e-10)


@pytest.mark.unit
@pytest.mark.parametrize(
    "p,x,y,expected",
    [
        (1, [1, 1, 1], [0, 0, 0], 3.0),
        (1, [5, 3, 2], [2, 1, 1], 6.0),
        (2, [1, 1, 1], [0, 0, 0], math.sqrt(3)),
        (2, [3, 4], [0, 0], 5.0),
        (float("inf"), [1, 2, 3], [0, 0, 0], 3.0),
        (float("inf"), [5, 3, 8], [2, 1, 1], 7.0),
        (3, [1, 1, 1], [0, 0, 0], 3 ** (1 / 3)),
    ],
)
def test_distance_with_different_p(p, x, y, expected):
    """Test distance calculation with different p values."""
    pseudometric = LpPseudometric(p=p)
    assert math.isclose(pseudometric.distance(x, y), expected, abs_tol=1e-10)


@pytest.mark.unit
def test_distance_with_coordinates():
    """Test distance calculation with specific coordinates."""
    pseudometric = LpPseudometric(p=2, coordinates=[0, 2])
    x = [1, 10, 2]
    y = [0, 5, 0]
    # Only coordinates 0 and 2 are considered, so distance = sqrt(1^2 + 2^2) = sqrt(5)
    expected = math.sqrt(5)
    assert math.isclose(pseudometric.distance(x, y), expected, abs_tol=1e-10)


@pytest.mark.unit
def test_distance_with_callable():
    """Test distance calculation with callable functions."""

    def f(t):
        return t**2

    def g(t):
        return 2 * t**2

    pseudometric = LpPseudometric(p=2, domain=(0, 1))
    # Approximation of the L2 distance between f and g over [0,1]
    # The exact value would be sqrt(integral of (t^2 - 2*t^2)^2 dt from 0 to 1) = sqrt(1/5)
    # But the implementation uses sampling, so we allow for some error
    distance = pseudometric.distance(f, g)
    assert 0.4 < distance < 0.5


@pytest.mark.unit
def test_distance_with_strings():
    """Test distance calculation with strings."""
    pseudometric = LpPseudometric(p=2)
    s1 = "abc"
    s2 = "abd"
    # ASCII values: a=97, b=98, c=99, d=100
    # Distance = sqrt((97-97)^2 + (98-98)^2 + (99-100)^2) = 1
    assert math.isclose(pseudometric.distance(s1, s2), 1.0, abs_tol=1e-10)


@pytest.mark.unit
def test_distances_matrix():
    """Test the distances method that computes a distance matrix."""
    pseudometric = LpPseudometric(p=2)
    xs = [[0, 0], [1, 0], [0, 1]]
    ys = [[0, 0], [1, 1], [2, 0]]

    expected = [[0.0, math.sqrt(2), 2.0], [1.0, 1.0, 1.0], [1.0, 1.0, math.sqrt(5)]]

    result = pseudometric.distances(xs, ys)

    assert len(result) == len(xs)
    assert all(len(row) == len(ys) for row in result)

    for i in range(len(xs)):
        for j in range(len(ys)):
            assert math.isclose(result[i][j], expected[i][j], abs_tol=1e-10)


@pytest.mark.unit
def test_check_non_negativity(default_pseudometric):
    """Test the check_non_negativity method."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert default_pseudometric.check_non_negativity(x, y) is True


@pytest.mark.unit
def test_check_symmetry(default_pseudometric):
    """Test the check_symmetry method."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert default_pseudometric.check_symmetry(x, y) is True


@pytest.mark.unit
def test_check_triangle_inequality(default_pseudometric):
    """Test the check_triangle_inequality method."""
    x = [0, 0]
    y = [1, 0]
    z = [1, 1]
    assert default_pseudometric.check_triangle_inequality(x, y, z) is True


@pytest.mark.unit
def test_check_weak_identity_same_point(default_pseudometric):
    """Test the check_weak_identity method with the same point."""
    x = [1, 2, 3]
    assert default_pseudometric.check_weak_identity(x, x) is True


@pytest.mark.unit
def test_check_weak_identity_different_points_with_coordinates():
    """Test the check_weak_identity method with different points but same selected coordinates."""
    pseudometric = LpPseudometric(p=2, coordinates=[0, 1])
    x = [1, 2, 3]
    y = [
        1,
        2,
        4,
    ]  # Different in coordinate 2, but that's not included in the measurement
    assert pseudometric.check_weak_identity(x, y) is True


@pytest.mark.unit
def test_convert_to_array_ivector():
    """Test _convert_to_array method with IVector."""
    pseudometric = LpPseudometric()
    mock_vector = Mock()
    mock_vector.to_array.return_value = [1, 2, 3]

    result = pseudometric._convert_to_array(mock_vector)
    assert np.array_equal(result, np.array([1, 2, 3]))
    mock_vector.to_array.assert_called_once()


@pytest.mark.unit
def test_convert_to_array_imatrix():
    """Test _convert_to_array method with IMatrix."""
    pseudometric = LpPseudometric()
    mock_matrix = Mock()
    mock_matrix.to_array.return_value = [[1, 2], [3, 4]]

    result = pseudometric._convert_to_array(mock_matrix)
    assert np.array_equal(result, np.array([[1, 2], [3, 4]]))
    mock_matrix.to_array.assert_called_once()


@pytest.mark.unit
def test_convert_to_array_list():
    """Test _convert_to_array method with a list."""
    pseudometric = LpPseudometric()
    result = pseudometric._convert_to_array([1, 2, 3])
    assert np.array_equal(result, np.array([1, 2, 3]))


@pytest.mark.unit
def test_convert_to_array_string():
    """Test _convert_to_array method with a string."""
    pseudometric = LpPseudometric()
    result = pseudometric._convert_to_array("abc")
    assert np.array_equal(result, np.array([97, 98, 99]))  # ASCII values


@pytest.mark.unit
def test_convert_to_array_callable():
    """Test _convert_to_array method with a callable."""
    pseudometric = LpPseudometric(domain=(0, 1))

    def f(t):
        return t**2

    result = pseudometric._convert_to_array(f)
    assert len(result) == 100  # Default number of sample points
    assert result[0] == 0.0  # f(0) = 0
    assert math.isclose(result[-1], 1.0, abs_tol=1e-10)  # f(1) = 1


@pytest.mark.unit
def test_convert_to_array_callable_without_domain():
    """Test _convert_to_array method with a callable but no domain."""
    pseudometric = LpPseudometric()

    def f(t):
        return t**2

    with pytest.raises(
        ValueError, match="Domain must be specified when using callable inputs"
    ):
        pseudometric._convert_to_array(f)


@pytest.mark.unit
def test_convert_to_array_unsupported_type():
    """Test _convert_to_array method with an unsupported type."""

    class UnsupportedType:
        pass

    pseudometric = LpPseudometric()

    with pytest.raises(TypeError, match="Unsupported input type for LpPseudometric"):
        pseudometric._convert_to_array(UnsupportedType())


@pytest.mark.unit
def test_filter_coordinates():
    """Test _filter_coordinates method."""
    pseudometric = LpPseudometric(coordinates=[0, 2])
    arr = np.array([1, 2, 3, 4])
    result = pseudometric._filter_coordinates(arr)
    assert np.array_equal(result, np.array([1, 3]))


@pytest.mark.unit
def test_filter_coordinates_2d():
    """Test _filter_coordinates method with 2D array."""
    pseudometric = LpPseudometric(coordinates=[0, 2])
    arr = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    result = pseudometric._filter_coordinates(arr)
    assert np.array_equal(result, np.array([[1, 2], [5, 6]]))


@pytest.mark.unit
def test_filter_coordinates_out_of_bounds():
    """Test _filter_coordinates method with out-of-bounds coordinates."""
    pseudometric = LpPseudometric(coordinates=[0, 5])
    arr = np.array([1, 2, 3, 4])
    with pytest.raises(ValueError, match="Coordinate index out of bounds"):
        pseudometric._filter_coordinates(arr)


@pytest.mark.unit
def test_distance_incompatible_shapes():
    """Test distance method with inputs of incompatible shapes."""
    pseudometric = LpPseudometric()
    x = [1, 2, 3]
    y = [1, 2]
    with pytest.raises(ValueError, match="Inputs must have the same shape"):
        pseudometric.distance(x, y)


@pytest.mark.unit
def test_string_representation(default_pseudometric):
    """Test the string representation of LpPseudometric."""
    assert str(default_pseudometric) == "LpPseudometric(p=2.0)"


@pytest.mark.unit
def test_repr_representation(default_pseudometric):
    """Test the repr representation of LpPseudometric."""
    expected = "LpPseudometric(p=2.0, domain=None, coordinates=None, epsilon=1e-10)"
    assert repr(default_pseudometric) == expected


@pytest.mark.unit
def test_string_representation_with_domain_and_coordinates():
    """Test the string representation with domain and coordinates."""
    pseudometric = LpPseudometric(p=3, domain=(0, 1), coordinates=[0, 1])
    assert str(pseudometric) == "LpPseudometric(p=3, domain=(0, 1), coordinates=[0, 1])"
