import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.pseudometrics.LpPseudometric import (
    LpPseudometric,
)


@pytest.fixture
def lp_pseudometric():
    """Fixture to create an LpPseudometric instance with default parameters"""
    return LpPseudometric(p=2)


@pytest.mark.unit
def test_resource(lp_pseudometric):
    """Test that the resource attribute is correctly set"""
    assert lp_pseudometric.resource == "PSEUDOMETRIC"


@pytest.mark.unit
def test_type(lp_pseudometric):
    """Test that the type attribute is correctly set"""
    assert lp_pseudometric.type == "LpPseudometric"


@pytest.mark.unit
def test_initialization():
    """Test that the LpPseudometric class initializes correctly"""
    # Test with valid p
    pseudometric = LpPseudometric(p=2)
    assert pseudometric.p == 2
    assert pseudometric.domain is None

    # Test with invalid p
    with pytest.raises(ValueError):
        LpPseudometric(p=0)


@pytest.mark.unit
def test_distance(lp_pseudometric):
    """Test the distance method with various inputs"""
    # Test with identical points
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3])
    assert lp_pseudometric.distance(x, y) == 0.0

    # Test with different points
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    assert lp_pseudometric.distance(x, y) == 5.0

    # Test with p=1
    pseudometric_p1 = LpPseudometric(p=1)
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert pseudometric_p1.distance(x, y) == 3.0

    # Test with p=inf
    pseudometric_pinfinity = LpPseudometric(p=np.inf)
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert pseudometric_pinfinity.distance(x, y) == 3.0

    # Test with domain specified
    pseudometric_domain = LpPseudometric(p=2, domain=[0, 2])
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert pseudometric_domain.distance(x, y) == 2.0


@pytest.mark.unit
def test_distances(lp_pseudometric):
    """Test the distances method"""
    x = [1, 2, 3]
    ys = [[4, 5, 6], [7, 8, 9]]
    distances = lp_pseudometric.distances(x, ys)
    assert isinstance(distances, list)
    assert len(distances) == 2
    assert all(isinstance(d, float) for d in distances)


@pytest.mark.unit
def test_distance_non_numeric_input(lp_pseudometric):
    """Test distance method with non-numeric input"""
    x = "test_string"
    y = "test_string"
    with pytest.raises(ValueError):
        lp_pseudometric.distance(x, y)
