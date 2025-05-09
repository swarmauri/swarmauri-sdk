import pytest
from typing import Union
from swarmauri_standard.pseudometrics.EquivalenceRelationPseudometric import EquivalenceRelationPseudometric

@pytest.fixture
def equivalence_function():
    """Fixture providing an example equivalence function."""
    def eq_func(x: Union[IVector, IMatrix, List[float], str, Callable],
                y: Union[IVector, IMatrix, List[float], str, Callable]) -> bool:
        """Simple equivalence function that checks if x and y are the same."""
        return x == y
    return eq_func

@pytest.fixture
def equivalence_relation_pseudometric(equivalence_function):
    """Fixture providing an instance of EquivalenceRelationPseudometric."""
    return EquivalenceRelationPseudometric(equivalence_function)

@pytest.mark.unit
def test_resource(equivalence_relation_pseudometric):
    """Test that the resource property returns the correct value."""
    assert equivalence_relation_pseudometric.resource == "Pseudometric"

@pytest.mark.unit
def test_type(equivalence_relation_pseudometric):
    """Test that the type property returns the correct value."""
    assert equivalence_relation_pseudometric.type == "EquivalenceRelationPseudometric"

@pytest.mark.unit
def test_distance(equivalence_relation_pseudometric):
    """Test the distance method with equivalent and non-equivalent inputs."""
    # Test with equivalent inputs
    x = "test"
    y = "test"
    assert equivalence_relation_pseudometric.distance(x, y) == 0.0
    
    # Test with non-equivalent inputs
    x = "test1"
    y = "test2"
    assert equivalence_relation_pseudometric.distance(x, y) == 1.0

@pytest.mark.unit
def test_check_symmetry(equivalence_relation_pseudometric):
    """Test the check_symmetry method."""
    x = "test"
    y = "test"
    assert equivalence_relation_pseudometric.check_symmetry(x, y) is True

@pytest.mark.unit
def test_check_non_negativity(equivalence_relation_pseudometric):
    """Test the check_non_negativity method."""
    x = "test"
    y = "test"
    assert equivalence_relation_pseudometric.check_non_negativity(x, y) is True

@pytest.mark.unit
def test_check_triangle_inequality(equivalence_relation_pseudometric):
    """Test the check_triangle_inequality method."""
    x = "test"
    y = "test"
    z = "test"
    assert equivalence_relation_pseudometric.check_triangle_inequality(x, y, z) is True

@pytest.mark.unit
def test_check_weak_identity(equivalence_relation_pseudometric):
    """Test the check_weak_identity method."""
    x = "test"
    y = "test"
    assert equivalence_relation_pseudometric.check_weak_identity(x, y) is True