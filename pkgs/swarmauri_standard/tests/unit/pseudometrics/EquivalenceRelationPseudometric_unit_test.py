import pytest
from swarmauri_standard.swarmauri_standard.pseudometrics.EquivalenceRelationPseudometric import (
    EquivalenceRelationPseudometric,
)
import logging


@pytest.mark.unit
class TestEquivalenceRelationPseudometric:
    """Unit tests for the EquivalenceRelationPseudometric class."""

    @pytest.fixture
    def equivalence_relation(self):
        """Fixture providing a simple equivalence relation."""

        def equality_relation(x, y):
            return x == y

        return equality_relation

    @pytest.fixture
    def non_integer_equivalence_relation(self):
        """Fixture providing an equivalence relation for non-integer values."""

        def string_case_insensitive_relation(x, y):
            return (
                x.lower() == y.lower()
                if isinstance(x, str) and isinstance(y, str)
                else x == y
            )

        return string_case_insensitive_relation

    @pytest.fixture
    def test_equivalence_relation_pseudometric(self, equivalence_relation):
        """Fixture providing an instance of EquivalenceRelationPseudometric."""
        return EquivalenceRelationPseudometric(equivalence_relation)

    def test_distance_method(self, test_equivalence_relation_pseudometric):
        """Test the distance method of EquivalenceRelationPseudometric."""
        # Test equivalent elements
        assert test_equivalence_relation_pseudometric.distance(1, 1) == 0.0
        assert test_equivalence_relation_pseudometric.distance("Test", "Test") == 0.0

        # Test non-equivalent elements
        assert test_equivalence_relation_pseudometric.distance(1, 2) == 1.0
        assert test_equivalence_relation_pseudometric.distance("Test", "test") == 1.0

    def test_distances_method(self, test_equivalence_relation_pseudometric):
        """Test the distances method of EquivalenceRelationPseudometric."""
        # Test with list of elements
        distances = test_equivalence_relation_pseudometric.distances(1, [1, 2, 3])
        assert distances == [0.0, 1.0, 1.0]

        # Test with tuple of elements
        distances = test_equivalence_relation_pseudometric.distances(
            "Test", ("Test", "test", "Different")
        )
        assert distances == [0.0, 1.0, 1.0]

    def test_check_non_negativity(self, test_equivalence_relation_pseudometric):
        """Test the check_non_negativity method."""
        # Test with equivalent elements
        assert test_equivalence_relation_pseudometric.check_non_negativity(1, 1) == True

        # Test with non-equivalent elements
        assert test_equivalence_relation_pseudometric.check_non_negativity(1, 2) == True

    def test_check_symmetry(self, test_equivalence_relation_pseudometric):
        """Test the check_symmetry method."""
        # Test with numbers
        assert test_equivalence_relation_pseudometric.check_symmetry(1, 2) == True

        # Test with strings
        assert (
            test_equivalence_relation_pseudometric.check_symmetry("Test", "test")
            == True
        )

    def test_check_triangle_inequality(self, test_equivalence_relation_pseudometric):
        """Test the check_triangle_inequality method."""
        # Test with all equivalent elements
        assert (
            test_equivalence_relation_pseudometric.check_triangle_inequality(1, 1, 1)
            == True
        )

        # Test with some equivalent and some non-equivalent elements
        assert (
            test_equivalence_relation_pseudometric.check_triangle_inequality(1, 1, 2)
            == True
        )

        # Test with all non-equivalent elements
        assert (
            test_equivalence_relation_pseudometric.check_triangle_inequality(1, 2, 3)
            == True
        )

    def test_check_weak_identity(self, test_equivalence_relation_pseudometric):
        """Test the check_weak_identity method."""
        # Test with equivalent elements
        assert test_equivalence_relation_pseudometric.check_weak_identity(1, 1) == True

        # Test with non-equivalent elements
        assert test_equivalence_relation_pseudometric.check_weak_identity(1, 2) == True

    @pytest.mark.parametrize(
        "x,y,expected_distance",
        [
            (1, 1, 0.0),
            (1, 2, 1.0),
            ("Test", "Test", 0.0),
            ("Test", "test", 1.0),
        ],
    )
    def test_distance_parametrized(self, equivalence_relation, x, y, expected_distance):
        """Parametrized test for the distance method."""
        pseudometric = EquivalenceRelationPseudometric(equivalence_relation)
        assert pseudometric.distance(x, y) == expected_distance

    @pytest.mark.parametrize(
        "x,y,z,expected_result",
        [
            (1, 1, 1, True),
            (1, 1, 2, True),
            (1, 2, 3, True),
        ],
    )
    def test_triangle_inequality_parametrized(
        self, equivalence_relation, x, y, z, expected_result
    ):
        """Parametrized test for the triangle inequality check."""
        pseudometric = EquivalenceRelationPseudometric(equivalence_relation)
        assert pseudometric.check_triangle_inequality(x, y, z) == expected_result
