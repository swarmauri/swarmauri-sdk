import pytest
import numpy as np
import logging
from swarmauri_standard.swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm


@pytest.mark.unit
class TestL2EuclideanNorm:
    """Unit tests for the L2EuclideanNorm class."""

    @pytest.fixture
    def valid_vectors(self):
        """Fixture providing valid vectors for testing."""
        return [
            np.array([1, 2, 3]),
            np.array([4, 5, 6, 7]),
            np.array([-1, -2, -3]),
            np.array([0, 0, 0]),
            np.array([2.5, -3.5, 4.5]),
        ]

    @pytest.fixture
    def invalid_vectors(self):
        """Fixture providing invalid vectors for testing."""
        return [[], None, "invalid_string", 123]

    def test_compute(self, valid_vectors):
        """Test the compute method with valid vectors."""
        for vector in valid_vectors:
            norm = L2EuclideanNorm().compute(vector)
            assert norm >= 0.0
            assert isinstance(norm, float)

    def test_compute_edge_cases(self, invalid_vectors):
        """Test the compute method with invalid vectors."""
        for vector in invalid_vectors:
            with pytest.raises(ValueError):
                L2EuclideanNorm().compute(vector)

    def test_check_non_negativity(self, valid_vectors):
        """Test the non-negativity property."""
        for vector in valid_vectors:
            assert L2EuclideanNorm().check_non_negativity(vector) is True

    @pytest.mark.parametrize(
        "x,y",
        [
            (np.array([1, 2]), np.array([3, 4])),
            (np.array([5, 6, 7]), np.array([-1, -2, -3])),
            (np.array([0, 0]), np.array([0, 0])),
        ],
    )
    def test_check_triangle_inequality(self, x, y):
        """Test the triangle inequality property."""
        assert L2EuclideanNorm().check_triangle_inequality(x, y) is True

    @pytest.mark.parametrize(
        "x,scalar",
        [
            (np.array([1, 2, 3]), 2),
            (np.array([4, 5, 6, 7]), -1.5),
            (np.array([-1, -2, -3]), 0),
            (np.array([0, 0, 0]), 5),
        ],
    )
    def test_check_absolute_homogeneity(self, x, scalar):
        """Test the absolute homogeneity property."""
        assert L2EuclideanNorm().check_absolute_homogeneity(x, scalar) is True

    @pytest.mark.parametrize(
        "x,expected",
        [
            (np.array([1, 2, 3]), False),
            (np.array([0, 0, 0]), True),
            (np.array([]), True),
            (np.array([0.0, 0.0, 0.0]), True),
        ],
    )
    def test_check_definiteness(self, x, expected):
        """Test the definiteness property."""
        assert L2EuclideanNorm().check_definiteness(x) == expected


@pytest.fixture(scope="session", autouse=True)
def logging_setup():
    """Fixture to configure basic logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
