import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.pseudometrics.LpPseudometric import LpPseudometric
import logging

@pytest.mark.unit
class TestLpPseudometric:
    """
    A test class for the LpPseudometric class.
    """
    
    @pytest.mark.parametrize("p,expected_type", [
        (2.0, "LpPseudometric"),
        (1.0, "LpPseudometric"),
        (float('inf'), "LpPseudometric")
    ])
    def test_type(self, p, expected_type):
        """
        Test the type property of the LpPseudometric class.
        """
        lpp = LpPseudometric(p=p)
        assert lpp.type == expected_type
    
    @pytest.mark.parametrize("p,resource", [
        (2.0, "PSEUDOMETRIC"),
        (1.0, "PSEUDOMETRIC"),
        (float('inf'), "PSEUDOMETRIC")
    ])
    def test_resource(self, p, resource):
        """
        Test the resource property of the LpPseudometric class.
        """
        lpp = LpPseudometric(p=p)
        assert lpp.resource == resource
    
    @pytest.mark.parametrize("p,domain", [
        (2.0, None),
        (2.0, np.array([0, 1])),
        (1.0, np.array([0, 1, 2]))
    ])
    def test_initialization(self, p, domain):
        """
        Test the initialization of the LpPseudometric class.
        """
        lpp = LpPseudometric(p=p, domain=domain)
        assert lpp.p == p
        assert np.array_equal(lpp.domain, domain)
    
    @pytest.mark.parametrize("p,x,y,expected_distance", [
        (2.0, np.array([1, 2, 3]), np.array([1, 2, 3]), 0.0),
        (2.0, np.array([1, 2, 3]), np.array([4, 5, 6]), np.sqrt(3**2 + 3**2 + 3**2)/3),
        (1.0, np.array([1, 2, 3]), np.array([4, 5, 6]), 3.0),
        (float('inf'), np.array([1, 2, 3]), np.array([4, 5, 6]), 3.0)
    ])
    def test_distance(self, p, x, y, expected_distance):
        """
        Test the distance method of the LpPseudometric class.
        """
        lpp = LpPseudometric(p=p)
        distance = lpp.distance(x, y)
        assert np.isclose(distance, expected_distance)
    
    @pytest.mark.parametrize("p,xs,ys,expected_distances", [
        (2.0, [np.array([1, 2]), np.array([3, 4])], [np.array([5, 6]), np.array([7, 8])], [np.sqrt(32), np.sqrt(32)]),
        (1.0, [np.array([1, 2]), np.array([3, 4])], [np.array([5, 6]), np.array([7, 8])], [7.0, 7.0]),
        (float('inf'), [np.array([1, 2]), np.array([3, 4])], [np.array([5, 6]), np.array([7, 8])], [4.0, 4.0])
    ])
    def test_distances(self, p, xs, ys, expected_distances):
        """
        Test the distances method of the LpPseudometric class.
        """
        lpp = LpPseudometric(p=p)
        distances = lpp.distances(xs, ys)
        assert np.allclose(distances, expected_distances)
    
    def test_invalid_p(self):
        """
        Test that initializing with invalid p raises ValueError.
        """
        with pytest.raises(ValueError):
            LpPseudometric(p=0.5)
    
    def test_distance_with_domain(self):
        """
        Test the distance method with a specified domain.
        """
        domain = np.array([0, 1])
        x = np.array([1, 2, 3])
        y = np.array([3, 4, 5])
        lpp = LpPseudometric(p=2.0, domain=domain)
        distance = lpp.distance(x, y)
        assert np.isclose(distance, np.sqrt((2**2 + 2**2)/2))