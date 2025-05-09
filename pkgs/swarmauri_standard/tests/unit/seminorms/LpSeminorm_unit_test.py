import pytest
from swarmauri_standard.swarmauri_standard.seminorms.LpSeminorm import LpSeminorm
import logging

logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_l2_seminorm_init():
    """
    Test initialization of LpSeminorm with p=2.0.
    """
    seminorm = LpSeminorm()
    assert seminorm.p == 2.0
    assert seminorm.type == "LpSeminorm"

@pytest.mark.unit
def test_l1_seminorm_init():
    """
    Test initialization of LpSeminorm with p=1.0.
    """
    seminorm = LpSeminorm(p=1.0)
    assert seminorm.p == 1.0
    assert seminorm.type == "LpSeminorm"

@pytest.mark.unit
def test_invalid_p_init():
    """
    Test initialization of LpSeminorm with invalid p values.
    """
    with pytest.raises(ValueError):
        LpSeminorm(p=-1.0)
    with pytest.raises(ValueError):
        LpSeminorm(p=0.0)
    with pytest.raises(ValueError):
        LpSeminorm(p=-5.0)

@pytest.mark.unit
def test_compute_seminorm_vector():
    """
    Test compute method with vector input.
    """
    seminorm = LpSeminorm(p=2.0)
    vector = [1.0, 2.0, 3.0]
    result = seminorm.compute(vector)
    expected = (1**2 + 2**2 + 3**2) ** 0.5
    assert result == expected

@pytest.mark.unit
def test_compute_seminorm_matrix():
    """
    Test compute method with matrix input.
    """
    seminorm = LpSeminorm(p=2.0)
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    result = seminorm.compute(matrix)
    expected = ((1**2 + 2**2) ** 0.5 + (3**2 + 4**2) ** 0.5) ** 0.5
    assert result == expected

@pytest.mark.unit
def test_compute_seminorm_empty():
    """
    Test compute method with empty input.
    """
    seminorm = LpSeminorm(p=2.0)
    result = seminorm.compute([])
    assert result == 0.0

@pytest.mark.unit
def test_triangle_inequality():
    """
    Test triangle inequality for LpSeminorm.
    """
    seminorm = LpSeminorm(p=2.0)
    vector_a = [1.0, 0.0]
    vector_b = [0.0, 1.0]
    
    seminorm_a = seminorm.compute(vector_a)
    seminorm_b = seminorm.compute(vector_b)
    seminorm_sum = seminorm.compute([1.0, 1.0])
    
    assert seminorm_sum <= (seminorm_a + seminorm_b)

@pytest.mark.unit
def test_scalar_homogeneity():
    """
    Test scalar homogeneity for LpSeminorm.
    """
    seminorm = LpSeminorm(p=2.0)
    vector = [2.0, 4.0]
    scalar = 0.5
    
    scaled_vector = [1.0, 2.0]
    seminorm_scaled = seminorm.compute(scaled_vector)
    seminorm_original = seminorm.compute(vector)
    
    assert seminorm_scaled == scalar * seminorm_original

@pytest.mark.unit
def test_compute_seminorm_callable():
    """
    Test compute method with callable input.
    """
    seminorm = LpSeminorm(p=2.0)
    
    def callable_input():
        return [1.0, 2.0, 3.0]
    
    result = seminorm.compute(callable_input)
    expected = (1**2 + 2**2 + 3**2) ** 0.5
    assert result == expected

@pytest.mark.unit
def test_compute_seminorm_string():
    """
    Test compute method with string input.
    """
    seminorm = LpSeminorm(p=2.0)
    with pytest.raises(NotImplementedError):
        seminorm.compute("test_string")