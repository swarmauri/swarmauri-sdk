import logging
from typing import List, Set

import numpy as np
import pytest
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.seminorms.CoordinateProjectionSeminorm import (
    CoordinateProjectionSeminorm,
)

# Configure logging
logger = logging.getLogger(__name__)


# Mock classes for testing
class MockVector(IVector):
    def __init__(self, components):
        self._components = components

    @property
    def components(self):
        return self._components

    def __add__(self, other):
        if isinstance(other, MockVector):
            return MockVector(
                [a + b for a, b in zip(self.components, other.components)]
            )
        return NotImplemented

    def __mul__(self, scalar):
        return MockVector([c * scalar for c in self.components])


class MockMatrix(IMatrix):
    def __init__(self, rows):
        self._rows = rows

    @property
    def rows(self):
        return self._rows

    def __add__(self, other):
        if isinstance(other, MockMatrix):
            return MockMatrix(
                [
                    [a + b for a, b in zip(row1, row2)]
                    for row1, row2 in zip(self.rows, other.rows)
                ]
            )
        return NotImplemented

    def __mul__(self, scalar):
        return MockMatrix([[c * scalar for c in row] for row in self.rows])

    # Add missing methods
    def __getitem__(self, index):
        return self._rows[index]

    def __iter__(self):
        return iter(self._rows)

    def __eq__(self, other):
        if not isinstance(other, MockMatrix):
            return NotImplemented
        return self._rows == other._rows

    def __neg__(self):
        return MockMatrix([[-c for c in row] for row in self._rows])

    def __sub__(self, other):
        if not isinstance(other, MockMatrix):
            return NotImplemented
        return MockMatrix(
            [
                [a - b for a, b in zip(row1, row2)]
                for row1, row2 in zip(self._rows, other._rows)
            ]
        )

    def __truediv__(self, scalar):
        return MockMatrix([[c / scalar for c in row] for row in self._rows])

    def __matmul__(self, other):
        # Simple matrix multiplication implementation
        if not isinstance(other, MockMatrix):
            return NotImplemented
        result = []
        for i in range(len(self._rows)):
            row = []
            for j in range(len(other._rows[0])):
                value = sum(
                    self._rows[i][k] * other._rows[k][j]
                    for k in range(len(other._rows))
                )
                row.append(value)
            result.append(row)
        return MockMatrix(result)

    def __setitem__(self, index, value):
        self._rows[index] = value

    def __array__(self):
        import numpy as np

        return np.array(self._rows)

    @property
    def shape(self):
        if not self._rows:
            return (0, 0)
        return (len(self._rows), len(self._rows[0]) if self._rows[0] else 0)

    @property
    def dtype(self):
        import numpy as np

        return np.array(self._rows).dtype

    def tolist(self):
        return self._rows.copy()

    def transpose(self):
        if not self._rows:
            return MockMatrix([])
        return MockMatrix(
            [[row[i] for row in self._rows] for i in range(len(self._rows[0]))]
        )

    def row(self, index):
        return self._rows[index]

    def column(self, index):
        return [row[index] for row in self._rows]

    def reshape(self, shape):
        import numpy as np

        flat = [item for row in self._rows for item in row]
        reshaped = np.reshape(flat, shape).tolist()
        return MockMatrix(reshaped)


# Fixtures
@pytest.fixture
def projection_indices() -> Set[int]:
    return {0, 2, 4}


@pytest.fixture
def seminorm(projection_indices) -> CoordinateProjectionSeminorm:
    return CoordinateProjectionSeminorm(projection_indices)


@pytest.fixture
def vector_data() -> List[float]:
    return [1.0, 2.0, 3.0, 4.0, 5.0]


@pytest.fixture
def mock_vector(vector_data) -> MockVector:
    return MockVector(vector_data)


@pytest.fixture
def matrix_data() -> List[List[float]]:
    return [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]


@pytest.fixture
def mock_matrix(matrix_data) -> MockMatrix:
    return MockMatrix(matrix_data)


# Test cases
@pytest.mark.unit
def test_initialization(projection_indices):
    """Test the initialization of CoordinateProjectionSeminorm."""
    seminorm = CoordinateProjectionSeminorm(projection_indices)
    assert seminorm.projection_indices == projection_indices
    assert seminorm.type == "CoordinateProjectionSeminorm"


@pytest.mark.unit
def test_initialization_with_empty_indices():
    """Test that initialization with empty indices raises ValueError."""
    with pytest.raises(ValueError, match="Projection indices set cannot be empty"):
        CoordinateProjectionSeminorm(set())


@pytest.mark.unit
@pytest.mark.parametrize(
    "indices,expected",
    [
        ({0, 2, 4}, np.sqrt(1**2 + 3**2 + 5**2)),  # Only consider indices 0, 2, 4
        ({1, 3}, np.sqrt(2**2 + 4**2)),  # Only consider indices 1, 3
        ({0}, 1.0),  # Only consider index 0
        ({0, 1, 2, 3, 4}, np.sqrt(55)),  # Consider all indices
    ],
)
def test_compute_vector(indices, expected, vector_data):
    """Test computing the seminorm for a vector with different projection indices."""
    seminorm = CoordinateProjectionSeminorm(indices)
    vector = MockVector(vector_data)
    result = seminorm.compute(vector)
    assert pytest.approx(result) == expected


@pytest.mark.unit
def test_compute_vector_out_of_bounds(vector_data):
    """Test computing the seminorm with out-of-bounds projection indices."""
    seminorm = CoordinateProjectionSeminorm({10})  # Index 10 is out of bounds
    vector = MockVector(vector_data)
    with pytest.raises(ValueError, match="Projection index 10 out of bounds"):
        seminorm.compute(vector)


@pytest.mark.unit
def test_compute_matrix(seminorm, mock_matrix):
    """Test computing the seminorm for a matrix."""
    # When flattened, the matrix becomes [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    # Projection indices {0, 2, 4} correspond to elements 1.0, 3.0, 5.0
    expected = np.sqrt(1**2 + 3**2 + 5**2)
    result = seminorm.compute(mock_matrix)
    assert pytest.approx(result) == expected


@pytest.mark.unit
def test_compute_matrix_out_of_bounds():
    """Test computing the seminorm for a matrix with out-of-bounds projection indices."""
    seminorm = CoordinateProjectionSeminorm({10})  # Index 10 is out of bounds
    matrix = MockMatrix([[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(ValueError, match="Projection index 10 out of bounds"):
        seminorm.compute(matrix)


@pytest.mark.unit
@pytest.mark.parametrize(
    "data,indices,expected",
    [
        ([1.0, 2.0, 3.0, 4.0, 5.0], {0, 2, 4}, np.sqrt(1**2 + 3**2 + 5**2)),
        ([1.0, 2.0, 3.0, 4.0, 5.0], {1, 3}, np.sqrt(2**2 + 4**2)),
        (np.array([1.0, 2.0, 3.0, 4.0, 5.0]), {0, 2, 4}, np.sqrt(1**2 + 3**2 + 5**2)),
    ],
)
def test_compute_sequence(data, indices, expected):
    """Test computing the seminorm for different sequence types."""
    seminorm = CoordinateProjectionSeminorm(indices)
    result = seminorm.compute(data)
    assert pytest.approx(result) == expected


@pytest.mark.unit
def test_compute_unsupported_type(seminorm):
    """Test that computing the seminorm for an unsupported type raises TypeError."""
    with pytest.raises(TypeError, match="Unsupported input type"):
        seminorm.compute(42)  # Integer is not a supported type


@pytest.mark.unit
def test_triangle_inequality_vector(seminorm):
    """Test the triangle inequality property for vectors."""
    x = MockVector([1.0, 2.0, 3.0, 4.0, 5.0])
    y = MockVector([5.0, 4.0, 3.0, 2.0, 1.0])
    assert seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_triangle_inequality_matrix(seminorm):
    """Test the triangle inequality property for matrices."""
    x = MockMatrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    y = MockMatrix([[6.0, 5.0], [4.0, 3.0], [2.0, 1.0]])
    assert seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_triangle_inequality_list(seminorm):
    """Test the triangle inequality property for lists."""
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [5.0, 4.0, 3.0, 2.0, 1.0]
    assert seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_triangle_inequality_numpy(seminorm):
    """Test the triangle inequality property for numpy arrays."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    assert seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_triangle_inequality_incompatible_types(seminorm):
    """Test that checking triangle inequality with incompatible types raises TypeError."""
    x = MockVector([1.0, 2.0, 3.0, 4.0, 5.0])
    y = [5.0, 4.0, 3.0, 2.0, 1.0]
    with pytest.raises(TypeError, match="Unsupported or incompatible input types"):
        seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_triangle_inequality_different_lengths():
    """Test that checking triangle inequality with sequences of different lengths raises ValueError."""
    seminorm = CoordinateProjectionSeminorm({0, 1, 2})
    x = [1.0, 2.0, 3.0]
    y = [5.0, 4.0, 3.0, 2.0, 1.0]
    with pytest.raises(ValueError, match="Sequences must have the same length"):
        seminorm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_scalar_homogeneity_vector(seminorm):
    """Test the scalar homogeneity property for vectors."""
    x = MockVector([1.0, 2.0, 3.0, 4.0, 5.0])
    alpha = 2.5
    assert seminorm.check_scalar_homogeneity(x, alpha)


@pytest.mark.unit
def test_scalar_homogeneity_matrix(seminorm):
    """Test the scalar homogeneity property for matrices."""
    x = MockMatrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    alpha = 2.5
    assert seminorm.check_scalar_homogeneity(x, alpha)


@pytest.mark.unit
def test_scalar_homogeneity_list(seminorm):
    """Test the scalar homogeneity property for lists."""
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    alpha = 2.5
    assert seminorm.check_scalar_homogeneity(x, alpha)


@pytest.mark.unit
def test_scalar_homogeneity_numpy(seminorm):
    """Test the scalar homogeneity property for numpy arrays."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    alpha = 2.5
    assert seminorm.check_scalar_homogeneity(x, alpha)


@pytest.mark.unit
def test_scalar_homogeneity_unsupported_type(seminorm):
    """Test that checking scalar homogeneity with an unsupported type raises TypeError."""
    with pytest.raises(TypeError, match="Unsupported input type"):
        seminorm.check_scalar_homogeneity(42, 2.5)  # Integer is not a supported type


@pytest.mark.unit
def test_compute_with_complex_values():
    """Test computing the seminorm with complex values."""
    seminorm = CoordinateProjectionSeminorm({0, 1})
    x = [1 + 2j, 3 + 4j, 5 + 6j]
    # |1+2j|^2 + |3+4j|^2 = 5 + 25 = 30
    expected = np.sqrt(30)
    result = seminorm.compute(x)
    assert pytest.approx(result) == expected


@pytest.mark.unit
def test_zero_vector(seminorm):
    """Test computing the seminorm of a zero vector."""
    zero_vector = MockVector([0.0, 0.0, 0.0, 0.0, 0.0])
    assert seminorm.compute(zero_vector) == 0.0


@pytest.mark.unit
def test_single_index_projection():
    """Test projection onto a single coordinate."""
    seminorm = CoordinateProjectionSeminorm({2})
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert seminorm.compute(x) == 3.0
