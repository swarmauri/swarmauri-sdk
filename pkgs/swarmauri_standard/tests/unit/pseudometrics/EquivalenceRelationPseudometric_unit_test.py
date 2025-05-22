import logging
from typing import Any, List

import pytest

from swarmauri_standard.pseudometrics.EquivalenceRelationPseudometric import (
    EquivalenceRelationPseudometric,
)

# Set up logging
logger = logging.getLogger(__name__)


# Define simple equivalence relations for testing
def mod3_equivalence(x: int, y: int) -> bool:
    """Equivalence relation where numbers are equivalent if they have the same remainder when divided by 3."""
    return x % 3 == y % 3


def string_length_equivalence(x: str, y: str) -> bool:
    """Equivalence relation where strings are equivalent if they have the same length."""
    return len(x) == len(y)


def list_length_equivalence(x: List[Any], y: List[Any]) -> bool:
    """Equivalence relation where lists are equivalent if they have the same length."""
    return len(x) == len(y)


def always_equivalent(x: Any, y: Any) -> bool:
    """Equivalence relation where everything is equivalent."""
    return True


def never_equivalent(x: Any, y: Any) -> bool:
    """Equivalence relation where nothing is equivalent (except to itself)."""
    return x is y


@pytest.fixture
def mod3_pseudometric():
    """Fixture for a pseudometric based on mod3 equivalence."""
    return EquivalenceRelationPseudometric(equivalence_relation=mod3_equivalence)


@pytest.fixture
def string_length_pseudometric():
    """Fixture for a pseudometric based on string length equivalence."""
    return EquivalenceRelationPseudometric(
        equivalence_relation=string_length_equivalence
    )


@pytest.fixture
def list_length_pseudometric():
    """Fixture for a pseudometric based on list length equivalence."""
    return EquivalenceRelationPseudometric(equivalence_relation=list_length_equivalence)


@pytest.fixture
def always_equivalent_pseudometric():
    """Fixture for a pseudometric where everything is equivalent."""
    return EquivalenceRelationPseudometric(equivalence_relation=always_equivalent)


@pytest.fixture
def never_equivalent_pseudometric():
    """Fixture for a pseudometric where nothing is equivalent (except to itself)."""
    return EquivalenceRelationPseudometric(equivalence_relation=never_equivalent)


@pytest.mark.unit
def test_type():
    """Test that the type property is correctly set."""
    pseudometric = EquivalenceRelationPseudometric(
        equivalence_relation=lambda x, y: True
    )
    assert pseudometric.type == "EquivalenceRelationPseudometric"


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (0, 0, 0.0),  # Same number, equivalent
        (0, 3, 0.0),  # Different numbers, but both mod 3 = 0
        (1, 4, 0.0),  # Different numbers, but both mod 3 = 1
        (2, 5, 0.0),  # Different numbers, but both mod 3 = 2
        (0, 1, 1.0),  # Different mod 3 values
        (1, 2, 1.0),  # Different mod 3 values
        (0, 2, 1.0),  # Different mod 3 values
    ],
)
def test_mod3_distance(mod3_pseudometric, x, y, expected):
    """Test the distance method with mod3 equivalence relation."""
    assert mod3_pseudometric.distance(x, y) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ("hello", "world", 0.0),  # Both length 5
        ("a", "b", 0.0),  # Both length 1
        ("", "", 0.0),  # Both length 0
        ("a", "bc", 1.0),  # Different lengths
        ("abc", "defg", 1.0),  # Different lengths
    ],
)
def test_string_length_distance(string_length_pseudometric, x, y, expected):
    """Test the distance method with string length equivalence relation."""
    assert string_length_pseudometric.distance(x, y) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 2, 3], [4, 5, 6], 0.0),  # Both length 3
        ([], [], 0.0),  # Both length 0
        ([1], [2], 0.0),  # Both length 1
        ([1, 2], [3, 4, 5], 1.0),  # Different lengths
        ([], [1, 2, 3, 4], 1.0),  # Different lengths
    ],
)
def test_list_length_distance(list_length_pseudometric, x, y, expected):
    """Test the distance method with list length equivalence relation."""
    assert list_length_pseudometric.distance(x, y) == expected


@pytest.mark.unit
def test_always_equivalent_distance(always_equivalent_pseudometric):
    """Test the distance method with always equivalent relation."""
    assert always_equivalent_pseudometric.distance(1, 2) == 0.0
    assert always_equivalent_pseudometric.distance("a", "b") == 0.0
    assert always_equivalent_pseudometric.distance([1, 2], [3, 4, 5]) == 0.0


@pytest.mark.unit
def test_never_equivalent_distance(never_equivalent_pseudometric):
    """Test the distance method with never equivalent relation."""
    # Different objects should have distance 1
    assert never_equivalent_pseudometric.distance(1, 2) == 1.0
    assert never_equivalent_pseudometric.distance("a", "b") == 1.0

    # Same object references should have distance 0
    x = [1, 2, 3]
    assert never_equivalent_pseudometric.distance(x, x) == 0.0


@pytest.mark.unit
def test_distances_matrix(mod3_pseudometric):
    """Test the distances method that computes a distance matrix."""
    xs = [0, 1, 2]
    ys = [0, 3, 4, 5]

    expected = [
        [0.0, 0.0, 1.0, 1.0],  # 0 compared with [0, 3, 4, 5]
        [1.0, 1.0, 0.0, 1.0],  # 1 compared with [0, 3, 4, 5]
        [1.0, 1.0, 1.0, 0.0],  # 2 compared with [0, 3, 4, 5]
    ]

    result = mod3_pseudometric.distances(xs, ys)
    assert result == expected


@pytest.mark.unit
def test_distance_error_handling():
    """Test error handling in the distance method."""

    # Create a pseudometric with an equivalence relation that raises an exception
    def error_relation(x, y):
        raise ValueError("Test error")

    pseudometric = EquivalenceRelationPseudometric(equivalence_relation=error_relation)

    with pytest.raises(ValueError, match="Failed to calculate distance: Test error"):
        pseudometric.distance(1, 2)


@pytest.mark.unit
def test_distances_error_handling():
    """Test error handling in the distances method."""

    # Create a pseudometric with an equivalence relation that raises an exception
    def error_relation(x, y):
        raise ValueError("Test error")

    pseudometric = EquivalenceRelationPseudometric(equivalence_relation=error_relation)

    with pytest.raises(
        ValueError,
        match="Failed to calculate distances matrix: Failed to calculate distance: Test error",
    ):
        pseudometric.distances([1, 2], [3, 4])


@pytest.mark.unit
def test_check_non_negativity(mod3_pseudometric):
    """Test the check_non_negativity method."""
    # This should always be true for this pseudometric
    assert mod3_pseudometric.check_non_negativity(1, 2) is True
    assert mod3_pseudometric.check_non_negativity(0, 3) is True


@pytest.mark.unit
def test_check_symmetry(mod3_pseudometric):
    """Test the check_symmetry method."""
    # Should be symmetric for any inputs
    assert mod3_pseudometric.check_symmetry(1, 2) is True
    assert mod3_pseudometric.check_symmetry(0, 3) is True

    # Test with a non-symmetric relation (for coverage)
    def non_symmetric_relation(x, y):
        if x == 1 and y == 2:
            return True
        if x == 2 and y == 1:
            return False
        return x == y

    non_symmetric_metric = EquivalenceRelationPseudometric(
        equivalence_relation=non_symmetric_relation
    )
    assert non_symmetric_metric.check_symmetry(1, 2) is False


@pytest.mark.unit
def test_check_symmetry_error_handling():
    """Test error handling in the check_symmetry method."""

    # Create a pseudometric with an equivalence relation that raises an exception
    def error_relation(x, y):
        raise ValueError("Test error")

    pseudometric = EquivalenceRelationPseudometric(equivalence_relation=error_relation)

    with pytest.raises(
        ValueError,
        match="Failed to check symmetry: Failed to calculate distance: Test error",
    ):
        pseudometric.check_symmetry(1, 2)


@pytest.mark.unit
def test_check_triangle_inequality(mod3_pseudometric):
    """Test the check_triangle_inequality method."""
    # Should satisfy triangle inequality for any inputs
    assert mod3_pseudometric.check_triangle_inequality(0, 1, 2) is True
    assert mod3_pseudometric.check_triangle_inequality(0, 3, 6) is True
    assert mod3_pseudometric.check_triangle_inequality(1, 2, 4) is True


@pytest.mark.unit
def test_check_triangle_inequality_error_handling():
    """Test error handling in the check_triangle_inequality method."""

    # Create a pseudometric with an equivalence relation that raises an exception
    def error_relation(x, y):
        raise ValueError("Test error")

    pseudometric = EquivalenceRelationPseudometric(equivalence_relation=error_relation)

    with pytest.raises(
        ValueError,
        match="Failed to check triangle inequality: Failed to calculate distance: Test error",
    ):
        pseudometric.check_triangle_inequality(1, 2, 3)


@pytest.mark.unit
def test_check_weak_identity(mod3_pseudometric):
    """Test the check_weak_identity method."""
    # Should be consistent for any inputs
    assert mod3_pseudometric.check_weak_identity(0, 3) is True  # equivalent
    assert mod3_pseudometric.check_weak_identity(0, 1) is True  # not equivalent


@pytest.mark.unit
def test_check_weak_identity_error_handling():
    """Test error handling in the check_weak_identity method."""

    # Create a pseudometric with an equivalence relation that raises an exception
    def error_relation(x, y):
        raise ValueError("Test error")

    pseudometric = EquivalenceRelationPseudometric(equivalence_relation=error_relation)

    with pytest.raises(ValueError, match="Failed to check weak identity: Test error"):
        pseudometric.check_weak_identity(1, 2)


@pytest.mark.unit
def test_serialization(mod3_pseudometric):
    """Test that the pseudometric can be serialized and deserialized."""

    # Exclude the function field from serialization
    data = mod3_pseudometric.model_dump_json(exclude={"equivalence_relation"})

    # Just check that the serialization worked and contains expected data
    assert mod3_pseudometric.id in data
    assert "EquivalenceRelationPseudometric" in data
