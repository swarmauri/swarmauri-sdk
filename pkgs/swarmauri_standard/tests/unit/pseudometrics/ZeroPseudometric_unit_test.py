import pytest
import logging
from swarmauri_standard.pseudometrics.ZeroPseudometric import ZeroPseudometric

logger = logging.getLogger(__name__)


@pytest.mark.unit
def test_zero_pseudometric_resource():
    """Test that the resource type is correctly set."""
    assert ZeroPseudometric.resource == "PSEUDOMETRIC"


@pytest.mark.unit
def test_zero_pseudometric_type():
    """Test that the type is correctly set to 'ZeroPseudometric'."""
    assert ZeroPseudometric.type == "ZeroPseudometric"


@pytest.mark.unit
def test_zero_distance():
    """Test that the distance between any two elements is zero."""
    zero_pseudometric = ZeroPseudometric()

    # Test with vectors
    assert zero_pseudometric.distance([1, 2, 3], [4, 5, 6]) == 0.0

    # Test with matrices
    assert zero_pseudometric.distance([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == 0.0

    # Test with strings
    assert zero_pseudometric.distance("test1", "test2") == 0.0

    # Test with callables
    assert zero_pseudometric.distance(lambda x: x, lambda x: x) == 0.0


@pytest.mark.unit
def test_zero_distances():
    """Test that distances to multiple elements are all zero."""
    zero_pseudometric = ZeroPseudometric()

    reference = "test"
    elements = ["a", "b", "c"]

    distances = zero_pseudometric.distances(reference, elements)
    assert all(d == 0.0 for d in distances)
    assert len(distances) == len(elements)


@pytest.mark.unit
def test_non_negativity():
    """Test that non-negativity property holds."""
    zero_pseudometric = ZeroPseudometric()

    # Test with vectors
    assert zero_pseudometric.check_non_negativity([1, 2], [3, 4]) is True

    # Test with strings
    assert zero_pseudometric.check_non_negativity("a", "b") is True

    # Test with mixed types
    assert zero_pseudometric.check_non_negativity(123, "test") is True


@pytest.mark.unit
def test_symmetry():
    """Test that symmetry property holds."""
    zero_pseudometric = ZeroPseudometric()

    # Test with vectors
    assert zero_pseudometric.check_symmetry([1, 2], [3, 4]) is True

    # Test with matrices
    assert zero_pseudometric.check_symmetry([[1, 2], [3, 4]], [[5, 6], [7, 8]]) is True

    # Test with different types
    assert zero_pseudometric.check_symmetry("a", 123) is True


@pytest.mark.unit
def test_triangle_inequality():
    """Test that triangle inequality property holds."""
    zero_pseudometric = ZeroPseudometric()

    # Test with vectors
    assert zero_pseudometric.check_triangle_inequality([1], [2], [3]) is True

    # Test with strings
    assert zero_pseudometric.check_triangle_inequality("a", "b", "c") is True

    # Test with mixed types
    assert zero_pseudometric.check_triangle_inequality(123, "test", [1, 2]) is True


@pytest.mark.unit
def test_weak_identity():
    """Test that weak identity property holds."""
    zero_pseudometric = ZeroPseudometric()

    # Test with identical elements
    assert zero_pseudometric.check_weak_identity("a", "a") is True

    # Test with different elements
    assert zero_pseudometric.check_weak_identity(123, "test") is True

    # Test with mixed types
    assert zero_pseudometric.check_weak_identity([1, 2], "test") is True


@pytest.mark.unit
def test_serialization():
    """Test that serialization works correctly."""
    zero_pseudometric = ZeroPseudometric()
    dumped_json = zero_pseudometric.model_dump_json()
    assert zero_pseudometric.model_validate_json(dumped_json) == ZeroPseudometric.id
