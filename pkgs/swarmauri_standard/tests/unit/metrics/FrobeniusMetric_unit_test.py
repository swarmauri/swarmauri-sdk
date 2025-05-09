import pytest
import numpy as np
import logging
from swarmauri_standard.swarmauri_standard.metrics.FrobeniusMetric import FrobeniusMetric

@pytest.mark.unit
class TestFrobeniusMetric:
    """
    Unit tests for the FrobeniusMetric class.
    """

    @pytest.mark.unit
    def test_initialization(self):
        """
        Test that the FrobeniusMetric can be initialized.
        """
        fm = FrobeniusMetric()
        assert isinstance(fm, FrobeniusMetric)

    @pytest.mark.unit
    def test_resource_attribute(self):
        """
        Test that the resource attribute is correctly set.
        """
        assert FrobeniusMetric.resource == "Metric"

    @pytest.mark.unit
    def test_type_attribute(self):
        """
        Test that the type attribute is correctly set.
        """
        assert FrobeniusMetric.type == "FrobeniusMetric"

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y", [
        (np.array([[1, 2], [3, 4]]), np.array([[1, 2], [3, 4]])),
        ([1, 2, 3], [1, 2, 3]),
        ("test", "test"),
        (lambda: np.array([1, 2, 3]), lambda: np.array([1, 2, 3]))
    ])
    def test_valid_input_types(self, x, y):
        """
        Test that valid input types are accepted and processed correctly.
        """
        fm = FrobeniusMetric()
        result = fm.distance(x, y)
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_invalid_input(self):
        """
        Test that invalid input types raise a ValueError.
        """
        fm = FrobeniusMetric()
        with pytest.raises(ValueError):
            fm.distance(object(), object())

    @pytest.mark.unit
    def test_distance_calculation(self):
        """
        Test that the Frobenius distance is calculated correctly.
        """
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])
        fm = FrobeniusMetric()
        
        # Test identical matrices
        distance = fm.distance(x, y)
        assert distance == 0.0

        # Test different matrices
        y = np.array([[2, 3], [4, 5]])
        distance = fm.distance(x, y)
        expected = np.sum((x - y)**2)
        assert distance == expected

    @pytest.mark.unit
    def test_non_negativity(self):
        """
        Test that the distance is non-negative.
        """
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])
        fm = FrobeniusMetric()
        distance = fm.distance(x, y)
        assert distance >= 0

    @pytest.mark.unit
    def test_identity_property(self):
        """
        Test the identity property (d(x, y) = 0 if and only if x = y).
        """
        x = np.array([[1, 2], [3, 4]])
        fm = FrobeniusMetric()
        
        # Test identical inputs
        distance = fm.distance(x, x)
        assert distance == 0
        
        # Test different inputs
        y = np.array([[2, 3], [4, 5]])
        distance = fm.distance(x, y)
        assert distance != 0

    @pytest.mark.unit
    def test_symmetry(self):
        """
        Test that d(x, y) = d(y, x).
        """
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[2, 3], [4, 5]])
        fm = FrobeniusMetric()
        
        distance_xy = fm.distance(x, y)
        distance_yx = fm.distance(y, x)
        assert distance_xy == distance_yx

    @pytest.mark.unit
    def test_triangle_inequality(self):
        """
        Test the triangle inequality (d(x, z) <= d(x, y) + d(y, z)).
        """
        x = np.array([[1, 1], [1, 1]])
        y = np.array([[2, 2], [2, 2]])
        z = np.array([[3, 3], [3, 3]])
        fm = FrobeniusMetric()
        
        d_xz = fm.distance(x, z)
        d_xy = fm.distance(x, y)
        d_yz = fm.distance(y, z)
        
        assert d_xz <= d_xy + d_yz

    @pytest.mark.unit
    def test_string_input(self):
        """
        Test that string inputs are properly converted to ASCII arrays.
        """
        x = "test"
        y = "test"
        fm = FrobeniusMetric()
        
        distance = fm.distance(x, y)
        assert distance == 0.0

    @pytest.mark.unit
    def test_callable_input(self):
        """
        Test that callable inputs returning valid types work correctly.
        """
        x = lambda: np.array([[1, 2], [3, 4]])
        y = lambda: np.array([[1, 2], [3, 4]])
        fm = FrobeniusMetric()
        
        distance = fm.distance(x, y)
        assert distance == 0.0