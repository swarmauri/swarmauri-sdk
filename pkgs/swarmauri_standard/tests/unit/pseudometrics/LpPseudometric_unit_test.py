import pytest
from swarmauri_standard.pseudometrics.LpPseudometric import LpPseudometric
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestLpPseudometric:
    """Unit tests for the LpPseudometric class."""

    def test_init(self):
        """Test initialization of LpPseudometric with valid parameters."""
        p = 2.0
        domain = "test_domain"
        coordinates = ["x", "y"]

        lpp = LpPseudometric(p, domain, coordinates)

        assert lpp.p == p
        assert lpp.domain == domain
        assert lpp.coordinates == set(coordinates)

    def test_distance_vector(self):
        """Test computing distance between vector elements."""
        x = IVector([1, 2, 3])
        y = IVector([4, 5, 6])
        lpp = LpPseudometric(p=2.0)

        distance = lpp.distance(x, y)
        expected = (3**2 + 3**2 + 3**2) ** 0.5
        assert distance == expected

    def test_distance_matrix(self):
        """Test computing distance between matrix elements."""
        x = IMatrix([[1, 2], [3, 4]])
        y = IMatrix([[5, 6], [7, 8]])
        lpp = LpPseudometric(p=2.0)

        distance = lpp.distance(x, y)
        elements = [4, 4, 4, 4]
        expected = (sum(e**2 for e in elements)) ** 0.5
        assert distance == expected

    def test_distance_scalar(self):
        """Test computing distance between scalar elements."""
        x = 5.0
        y = 3.0
        lpp = LpPseudometric(p=2.0)

        distance = lpp.distance(x, y)
        assert distance == 2.0

    def test_distances(self):
        """Test computing distances to multiple elements."""
        x = IVector([1, 2])
        y_list = [IVector([3, 4]), IVector([5, 6])]
        lpp = LpPseudometric(p=2.0)

        distances = lpp.distances(x, y_list)
        assert len(distances) == 2
        assert all(isinstance(d, float) for d in distances)

    def test_check_non_negativity(self):
        """Test non-negativity property."""
        x = IVector([1, 2])
        y = IVector([3, 4])
        lpp = LpPseudometric(p=2.0)

        result = lpp.check_non_negativity(x, y)
        assert result is True

    def test_check_symmetry(self):
        """Test symmetry property."""
        x = IVector([1, 2])
        y = IVector([3, 4])
        lpp = LpPseudometric(p=2.0)

        result = lpp.check_symmetry(x, y)
        assert result is True

    def test_check_triangle_inequality(self):
        """Test triangle inequality property."""
        x = IVector([1, 2])
        y = IVector([3, 4])
        z = IVector([5, 6])
        lpp = LpPseudometric(p=2.0)

        result = lpp.check_triangle_inequality(x, y, z)
        assert result is True

    def test_check_weak_identity(self):
        """Test weak identity property."""
        x = IVector([1, 2])
        y = IVector([1, 2])
        lpp = LpPseudometric(p=2.0)

        result = lpp.check_weak_identity(x, y)
        assert result is True

    def test_invalid_p_value(self):
        """Test initialization with invalid p value."""
        with pytest.raises(ValueError):
            LpPseudometric(p=0.5)

    def test_invalid_input_types(self):
        """Test distance with invalid input types."""
        lpp = LpPseudometric(p=2.0)
        with pytest.raises((TypeError, ValueError)):
            lpp.distance("invalid_type", "another_invalid_type")
