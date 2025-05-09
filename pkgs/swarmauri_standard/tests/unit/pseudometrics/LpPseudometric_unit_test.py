import pytest
from swarmauri_standard.swarmauri_standard.pseudometrics.LpPseudometric import (
    LpPseudometric,
)
import logging
import numpy as np

logger = logging.getLogger(__name__)


@pytest.mark.unit
def test_LpPseudometric_initialization():
    """
    Test the initialization of the LpPseudometric class.
    """
    # Test valid initialization
    pseudometric = LpPseudometric(p=2.0)
    assert pseudometric.p == 2.0
    assert pseudometric.domain is None

    # Test with custom domain
    domain = (0, 10)
    pseudometric = LpPseudometric(p=2.0, domain=domain)
    assert pseudometric.domain == domain

    # Test invalid p value
    with pytest.raises(ValueError):
        LpPseudometric(p=0.5)


@pytest.mark.unit
def test_LpPseudometric_distance():
    """
    Test the distance calculation between vectors.
    """
    pseudometric = LpPseudometric(p=2)

    # Test with identical vectors
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3])
    distance = pseudometric.distance(x, y)
    assert distance == 0.0

    # Test with different vectors
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    distance = pseudometric.distance(x, y)
    assert distance > 0.0

    # Test with different p values
    p_values = [1, 2, np.inf]
    for p in p_values:
        pseudometric = LpPseudometric(p=p)
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        distance = pseudometric.distance(x, y)
        assert distance >= 0.0


@pytest.mark.unit
def test_LpPseudometric_distances():
    """
    Test the distances method with multiple vectors.
    """
    pseudometric = LpPseudometric(p=2)
    x = np.array([1, 2, 3])
    y_list = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])]

    distances = pseudometric.distances(x, y_list)
    assert isinstance(distances, list)
    assert len(distances) == 3
    assert all(isinstance(d, float) for d in distances)


@pytest.mark.unit
def test_LpPseudometric_check_non_negativity():
    """
    Test the non-negativity check.
    """
    pseudometric = LpPseudometric(p=2)
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])

    is_non_negative = pseudometric.check_non_negativity(x, y)
    assert is_non_negative is True


@pytest.mark.unit
def test_LpPseudometric_check_symmetry():
    """
    Test the symmetry property.
    """
    pseudometric = LpPseudometric(p=2)
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])

    is_symmetric = pseudometric.check_symmetry(x, y)
    assert is_symmetric is True


@pytest.mark.unit
def test_LpPseudometric_check_triangle_inequality():
    """
    Test the triangle inequality check.
    """
    pseudometric = LpPseudometric(p=2)
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    z = np.array([7, 8, 9])

    is_triangle_valid = pseudometric.check_triangle_inequality(x, y, z)
    assert is_triangle_valid is True


@pytest.mark.unit
def test_LpPseudometric_check_weak_identity():
    """
    Test the weak identity of indiscernibles.
    """
    pseudometric = LpPseudometric(p=2)
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3])

    is_weak_identity = pseudometric.check_weak_identity(x, y)
    assert is_weak_identity is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y,expected",
    [
        (np.array([1, 2, 3]), np.array([1, 2, 3]), True),
        (np.array([1, 2, 3]), np.array([4, 5, 6]), False),
    ],
)
def test_LpPseudometric_check_compatibility(x, y, expected):
    """
    Test the compatibility check between different vector types.
    """
    pseudometric = LpPseudometric(p=2)
    is_compatible = pseudometric._check_compatibility(x, y)
    assert is_compatible == expected


@pytest.mark.unit
def test_LpPseudometric_compute_lp_norm():
    """
    Test the Lp norm computation.
    """
    pseudometric = LpPseudometric(p=2)
    vector = np.array([3, 4])
    norm = pseudometric._compute_lp_norm(vector)
    assert norm == 5.0

    # Test with domain specification
    domain = (0,)
    norm = pseudometric._compute_lp_norm(vector, domain=domain)
    assert norm == 3.0
