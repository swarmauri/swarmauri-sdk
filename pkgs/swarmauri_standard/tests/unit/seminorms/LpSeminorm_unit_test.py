import logging

import numpy as np
import pytest
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.seminorms.LpSeminorm import LpSeminorm

# Configure logging
logger = logging.getLogger(__name__)


# Mock classes for testing
class MockVector(IVector):
    def __init__(self, data):
        self._data = data

    def to_array(self):
        return self._data

    def dimension(self) -> int:
        return len(self._data)


class MockMatrix(IMatrix):
    def __init__(self, data):
        self._data = data

    def to_array(self):
        return self._data

    # Add required implementations
    @property
    def rows(self):
        return self._data

    def __add__(self, other):
        if isinstance(other, MockMatrix):
            return MockMatrix(
                [
                    [a + b for a, b in zip(row1, row2)]
                    for row1, row2 in zip(self._data, other._data)
                ]
            )
        return NotImplemented

    def __mul__(self, scalar):
        return MockMatrix([[c * scalar for c in row] for row in self._data])

    def __getitem__(self, index):
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def __eq__(self, other):
        if not isinstance(other, MockMatrix):
            return NotImplemented
        return self._data == other._data

    def __neg__(self):
        return MockMatrix([[-c for c in row] for row in self._data])

    def __sub__(self, other):
        if not isinstance(other, MockMatrix):
            return NotImplemented
        return MockMatrix(
            [
                [a - b for a, b in zip(row1, row2)]
                for row1, row2 in zip(self._data, other._data)
            ]
        )

    def __truediv__(self, scalar):
        return MockMatrix([[c / scalar for c in row] for row in self._data])

    def __matmul__(self, other):
        if not isinstance(other, MockMatrix):
            return NotImplemented
        result = []
        for i in range(len(self._data)):
            row = []
            for j in range(len(other._data[0])):
                value = sum(
                    self._data[i][k] * other._data[k][j]
                    for k in range(len(other._data))
                )
                row.append(value)
            result.append(row)
        return MockMatrix(result)

    def __setitem__(self, index, value):
        self._data[index] = value

    def __array__(self):
        import numpy as np

        return np.array(self._data)

    @property
    def shape(self):
        if not self._data:
            return (0, 0)
        return (len(self._data), len(self._data[0]) if self._data else 0)

    @property
    def dtype(self):
        import numpy as np

        return np.array(self._data).dtype

    def tolist(self):
        return self._data.copy()

    def transpose(self):
        if not self._data:
            return MockMatrix([])
        return MockMatrix(
            [[row[i] for row in self._data] for i in range(len(self._data[0]))]
        )

    def row(self, index):
        return self._data[index]

    def column(self, index):
        return [row[index] for row in self._data]

    def reshape(self, shape):
        import numpy as np

        flat = [item for row in self._data for item in row]
        reshaped = np.reshape(flat, shape).tolist()
        return MockMatrix(reshaped)


@pytest.fixture
def lp_seminorm_default():
    """Fixture for default LpSeminorm instance with p=2."""
    return LpSeminorm()


@pytest.fixture
def lp_seminorm_p1():
    """Fixture for LpSeminorm instance with p=1."""
    return LpSeminorm(p=1.0)


@pytest.fixture
def lp_seminorm_p3():
    """Fixture for LpSeminorm instance with p=3."""
    return LpSeminorm(p=3.0)


@pytest.fixture
def test_data():
    """Fixture providing various test data formats."""
    return {
        "array": np.array([1.0, 2.0, 3.0]),
        "list": [1.0, 2.0, 3.0],
        "tuple": (1.0, 2.0, 3.0),
        "vector": MockVector([1.0, 2.0, 3.0]),
        "matrix": MockMatrix([[1.0, 2.0], [3.0, 4.0]]),
        "string": "abc",
        "zero_array": np.zeros(3),
    }


@pytest.mark.unit
def test_initialization():
    """Test initialization of LpSeminorm with different parameters."""
    # Test default initialization
    lp = LpSeminorm()
    assert lp.p == 2.0
    assert lp.epsilon == 1e-10

    # Test custom initialization
    lp = LpSeminorm(p=3.0, epsilon=1e-8)
    assert lp.p == 3.0
    assert lp.epsilon == 1e-8

    # Test initialization with invalid p
    with pytest.raises(ValueError):
        LpSeminorm(p=0)

    with pytest.raises(ValueError):
        LpSeminorm(p=-1)


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    lp = LpSeminorm()
    assert lp.type == "LpSeminorm"


@pytest.mark.unit
@pytest.mark.parametrize(
    "p,input_data,expected",
    [
        (1.0, [1.0, 2.0, 3.0], 6.0),  # L1 norm: sum of absolute values
        (2.0, [1.0, 2.0, 3.0], 3.7416573867739413),  # L2 norm: sqrt(sum of squares)
        (3.0, [1.0, 2.0, 3.0], 3.3019272488946263),  # L3 norm: (sum of cubes)^(1/3)
        (1.0, [0.0, 0.0, 0.0], 0.0),  # Zero vector
        (2.0, [-1.0, -2.0, -3.0], 3.7416573867739413),  # Negative values
    ],
)
def test_compute_with_different_p(p, input_data, expected):
    """Test compute method with different p values and input data."""
    lp = LpSeminorm(p=p)
    result = lp.compute(input_data)
    assert pytest.approx(result, abs=1e-10) == expected


@pytest.mark.unit
def test_compute_with_different_input_types(test_data, lp_seminorm_default):
    """Test compute method with different input types."""
    # Calculate expected result for the reference array
    expected = np.sqrt(np.sum(np.array([1.0, 2.0, 3.0]) ** 2))

    # Test with array
    result = lp_seminorm_default.compute(test_data["array"])
    assert pytest.approx(result, abs=1e-10) == expected

    # Test with list
    result = lp_seminorm_default.compute(test_data["list"])
    assert pytest.approx(result, abs=1e-10) == expected

    # Test with tuple
    result = lp_seminorm_default.compute(test_data["tuple"])
    assert pytest.approx(result, abs=1e-10) == expected

    # Test with vector
    result = lp_seminorm_default.compute(test_data["vector"])
    assert pytest.approx(result, abs=1e-10) == expected

    # Test with zero array
    result = lp_seminorm_default.compute(test_data["zero_array"])
    assert pytest.approx(result, abs=1e-10) == 0.0

    # Test with string
    # We expect the sum of character codes
    char_codes = np.array([ord(c) for c in "abc"])
    expected_str = np.sqrt(np.sum(char_codes**2))
    result = lp_seminorm_default.compute(test_data["string"])
    assert pytest.approx(result, abs=1e-10) == expected_str

    # Test with matrix
    # For a matrix, it should flatten and compute the norm
    matrix_array = np.array([[1.0, 2.0], [3.0, 4.0]])
    expected_matrix = np.sqrt(np.sum(matrix_array**2))
    result = lp_seminorm_default.compute(test_data["matrix"])
    assert pytest.approx(result, abs=1e-10) == expected_matrix


@pytest.mark.unit
def test_compute_with_unsupported_types(lp_seminorm_default):
    """Test compute method with unsupported input types."""
    # Test with a callable
    with pytest.raises(TypeError):
        lp_seminorm_default.compute(lambda x: x)

    # Test with a complex object that cannot be converted to array
    class ComplexObject:
        pass

    with pytest.raises(TypeError):
        lp_seminorm_default.compute(ComplexObject())


@pytest.mark.unit
def test_triangle_inequality(lp_seminorm_default):
    """Test the triangle inequality property."""
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([4.0, 5.0, 6.0])

    # Verify that ||x + y|| <= ||x|| + ||y||
    assert lp_seminorm_default.check_triangle_inequality(x, y)

    # Test with different input types
    x_list = [1.0, 2.0, 3.0]
    y_list = [4.0, 5.0, 6.0]
    assert lp_seminorm_default.check_triangle_inequality(x_list, y_list)

    x_vector = MockVector([1.0, 2.0, 3.0])
    y_vector = MockVector([4.0, 5.0, 6.0])
    assert lp_seminorm_default.check_triangle_inequality(x_vector, y_vector)

    # Test with incompatible shapes
    with pytest.raises(ValueError):
        lp_seminorm_default.check_triangle_inequality([1.0, 2.0], [1.0, 2.0, 3.0])


@pytest.mark.unit
def test_scalar_homogeneity(lp_seminorm_default):
    """Test the scalar homogeneity property."""
    x = np.array([1.0, 2.0, 3.0])

    # Test with positive scalar
    alpha = 2.0
    assert lp_seminorm_default.check_scalar_homogeneity(x, alpha)

    # Test with negative scalar
    alpha = -3.0
    assert lp_seminorm_default.check_scalar_homogeneity(x, alpha)

    # Test with zero scalar
    alpha = 0.0
    assert lp_seminorm_default.check_scalar_homogeneity(x, alpha)

    # Test with complex scalar
    alpha = complex(2.0, 3.0)
    assert lp_seminorm_default.check_scalar_homogeneity(x, alpha)

    # Test with different input types
    x_list = [1.0, 2.0, 3.0]
    assert lp_seminorm_default.check_scalar_homogeneity(x_list, 2.0)

    x_vector = MockVector([1.0, 2.0, 3.0])
    assert lp_seminorm_default.check_scalar_homogeneity(x_vector, 2.0)


@pytest.mark.unit
@pytest.mark.parametrize("p", [1.0, 2.0, 3.0])
def test_special_case_optimization(p, test_data):
    """Test that special case optimizations for p=1 and p=2 give correct results."""
    lp_special = LpSeminorm(p=p)

    # Calculate using the general formula for comparison
    x_arr = np.array(test_data["list"])
    expected = float(np.sum(np.abs(x_arr) ** p) ** (1.0 / p))

    # Calculate using the LpSeminorm
    result = lp_special.compute(test_data["list"])

    # The results should be very close
    assert pytest.approx(result, abs=1e-10) == expected


@pytest.mark.unit
def test_numerical_stability():
    """Test numerical stability with very small and very large values."""
    lp = LpSeminorm(p=2.0)

    # Test with very small values
    small_values = [1e-15, 2e-15, 3e-15]
    result = lp.compute(small_values)
    expected = np.sqrt(np.sum(np.array(small_values) ** 2))
    assert pytest.approx(result, abs=1e-25) == expected

    # Test with very large values
    large_values = [1e15, 2e15, 3e15]
    result = lp.compute(large_values)
    expected = np.sqrt(np.sum(np.array(large_values) ** 2))
    assert (
        pytest.approx(result / expected, abs=1e-10) == 1.0
    )  # Compare ratio for large numbers


@pytest.mark.unit
def test_zero_norm():
    """Test that zero vectors have zero norm regardless of p value."""
    for p in [1.0, 2.0, 3.0, 10.0]:
        lp = LpSeminorm(p=p)
        zero_vector = np.zeros(5)
        assert pytest.approx(lp.compute(zero_vector), abs=1e-10) == 0.0
