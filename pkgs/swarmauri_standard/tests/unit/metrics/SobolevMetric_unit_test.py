import pytest
import logging
from swarmauri_standard.swarmauri_standard.metrics import SobolevMetric

@pytest.mark.unit
class TestSobolevMetric:
    """
    Unit test cases for the SobolevMetric class.
    
    This class provides comprehensive unit tests for the SobolevMetric class, 
    covering initialization, attribute validation, and core functionality.
    """

    @pytest.mark.parametrize("order,weight,expected_order,expected_weight", [
        (1, 1.0, 1, 1.0),
        (2, 0.5, 2, 0.5),
        (0, 1.0, 0, 1.0)
    ])
    def test_initialization(self, order, weight, expected_order, expected_weight):
        """
        Test initialization of SobolevMetric with valid parameters.
        
        Args:
            order: int
                The order parameter to test
            weight: float
                The weight parameter to test
            expected_order: int
                The expected order value after initialization
            expected_weight: float
                The expected weight value after initialization
                
        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Testing initialization with order={order}, weight={weight}")
        
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric(order=order, weight=weight)
        
        # Assert the order and weight were set correctly
        assert sobolev.order == expected_order
        assert sobolev.weight == expected_weight

    def test_type_attribute(self):
        """
        Test the type attribute of SobolevMetric.
        
        The type attribute should be "SobolevMetric".
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing type attribute")
        
        # Assert the type is correct
        assert SobolevMetric.type == "SobolevMetric"

    def test_resource_attribute(self):
        """
        Test the resource attribute of SobolevMetric.
        
        The resource attribute should be "Metric".
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing resource attribute")
        
        # Assert the resource is correct
        assert SobolevMetric.resource == "Metric"

    @pytest.mark.parametrize("order,weight", [
        (-1, 1.0),
        (1, -1.0),
        (0, 0.0)
    ])
    def test_invalid_initialization(self, order, weight):
        """
        Test initialization of SobolevMetric with invalid parameters.
        
        Args:
            order: int
                Invalid order parameter
            weight: float
                Invalid weight parameter
                
        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Testing invalid initialization with order={order}, weight={weight}")
        
        # Expect ValueError to be raised
        with pytest.raises(ValueError):
            SobolevMetric(order=order, weight=weight)

    def test_distance(self):
        """
        Test the distance method with simple functions.
        
        Uses simple functions to compute distance and verify basic properties.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing distance method")
        
        # Define test functions
        def f(x):
            return x
            
        def g(x):
            return x + 1
            
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric()
        
        # Compute distance
        distance = sobolev.distance(f, g)
        
        # Assert distance is non-negative
        assert distance >= 0.0
        
        # Test identity
        assert sobolev.distance(f, f) == 0.0
        
        # Test symmetry (distance should be same either way)
        assert sobolev.distance(f, g) == sobolev.distance(g, f)

    def test_distances(self):
        """
        Test the distances method with multiple functions.
        
        Verify that the method can handle both single and multiple functions.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing distances method")
        
        # Define test functions
        def f(x):
            return x
            
        def g(x):
            return x + 1
            
        def h(x):
            return x + 2
            
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric()
        
        # Test single function distance
        distance_single = sobolev.distances(f, g)
        assert isinstance(distance_single, float)
        
        # Test multiple functions
        distance_list = sobolev.distances(f, [g, h])
        assert isinstance(distance_list, list)
        assert len(distance_list) == 2

    def test_non_negativity(self):
        """
        Test the non-negativity property of the metric.
        
        For any functions x and y, distance(x, y) should be >= 0.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing non-negativity")
        
        # Define test functions
        def f(x):
            return x
            
        def g(x):
            return x + 1
            
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric()
        
        # Compute distance
        distance = sobolev.distance(f, g)
        
        # Assert non-negativity
        assert distance >= 0.0

    def test_identity(self):
        """
        Test the identity property of the metric.
        
        For any function x, distance(x, x) should be 0.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing identity property")
        
        # Define test function
        def f(x):
            return x
            
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric()
        
        # Compute distance
        distance = sobolev.distance(f, f)
        
        # Assert identity
        assert distance == 0.0

    def test_symmetry(self):
        """
        Test the symmetry property of the metric.
        
        For any functions x and y, distance(x, y) should equal distance(y, x).
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing symmetry property")
        
        # Define test functions
        def f(x):
            return x
            
        def g(x):
            return x + 1
            
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric()
        
        # Compute distances
        distance_xy = sobolev.distance(f, g)
        distance_yx = sobolev.distance(g, f)
        
        # Assert symmetry
        assert distance_xy == distance_yx

    def test_triangle_inequality(self):
        """
        Test the triangle inequality property of the metric.
        
        For any functions x, y, z, distance(x, z) <= distance(x, y) + distance(y, z).
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing triangle inequality")
        
        # Define test functions
        def f(x):
            return x
            
        def g(x):
            return x + 1
            
        def h(x):
            return x + 2
            
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric()
        
        # Compute distances
        distance_xz = sobolev.distance(f, h)
        distance_xy = sobolev.distance(f, g)
        distance_yz = sobolev.distance(g, h)
        
        # Assert triangle inequality
        assert distance_xz <= distance_xy + distance_yz

    def test_serialization(self):
        """
        Test serialization and deserialization of SobolevMetric instance.
        
        Verify that the instance can be serialized to a dictionary and
        reconstructed back to an equivalent instance.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Testing serialization")
        
        # Initialize SobolevMetric instance
        sobolev = SobolevMetric(order=2, weight=0.5)
        
        # Serialize to dictionary
        serialized = sobolev.to_dict()
        
        # Recreate from serialized data
        deserialized = SobolevMetric(**serialized)
        
        # Assert that the deserialized instance matches the original
        assert sobolev.order == deserialized.order
        assert sobolev.weight == deserialized.weight