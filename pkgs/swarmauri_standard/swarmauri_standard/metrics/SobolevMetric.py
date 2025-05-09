from typing import Any, TypeVar, Union, Optional
from pydantic import Field
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.metrics import MetricBase
from swarmauri_standard.norms import SobolevNorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', Callable, Sequence, str)
S = TypeVar('S', int, float, bool, str)

@ComponentBase.register_type(MetricBase, "SobolevMetric")
class SobolevMetric(MetricBase):
    """
    Provides a concrete implementation of the MetricBase class for computing distances 
    based on the Sobolev norm. This metric considers both the function values and 
    their derivatives up to a specified order, promoting smoothness in the comparison.

    Inherits From:
        MetricBase: Base class providing template logic for metric computations.
        
    Attributes:
        order: int
            The highest derivative order to include in the metric computation.
            Defaults to 1.
        weight: float
            Weighting factor for the derivative norms. Defaults to 1.0.
        sobolev_norm: SobolevNorm
            Instance of SobolevNorm used for norm computations.
            
    Provides:
        - Implementation of distance metric combining function values and derivatives
        - Logging functionality
        - Type hints and comprehensive docstrings
        - Compliance with PEP 8 and PEP 484 guidelines
    """
    type: Literal["SobolevMetric"] = "SobolevMetric"
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)
    order: int = 1
    weight: float = 1.0
    sobolev_norm: SobolevNorm
    
    def __init__(self, order: int = 1, weight: float = 1.0):
        """
        Initializes the SobolevMetric instance with specified parameters.
        
        Args:
            order: int
                The highest derivative order to include in the metric. Must be >= 0.
                Defaults to 1.
            weight: float
                Weighting factor for the derivative norms. Must be positive.
                Defaults to 1.0.
                
        Raises:
            ValueError: If order is negative or weight is non-positive.
        """
        super().__init__()
        if order < 0:
            raise ValueError("Order must be a non-negative integer")
        if weight <= 0:
            raise ValueError("Weight must be positive")
            
        self.order = order
        self.weight = weight
        self.sobolev_norm = SobolevNorm(order=order, weight=weight)
        logger.debug("SobolevMetric instance initialized with order=%d, weight=%f",
                    self.order, self.weight)
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two functions using the Sobolev norm.
        
        The distance is computed as the Sobolev norm of the difference between
        the two functions. This includes both the function values and their derivatives
        up to the specified order.
        
        Args:
            x: T
                The first function to compare
            y: T
                The second function to compare
                
        Returns:
            float:
                The computed distance between x and y
                
        Raises:
            ValueError:
                If the input types are not supported
            NotImplementedError:
                If derivative computation is not implemented
        """
        logger.debug("Computing Sobolev distance")
        
        # Create a difference function
        def difference(x_val: Any) -> Any:
            return x(x_val) - y(x_val)
        
        # Compute the Sobolev norm of the difference
        return self.sobolev_norm.compute(difference)
    
    def distances(self, x: T, y_list: Union[T, Sequence[T]]) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a function and one or more functions.
        
        Args:
            x: T
                The reference function
            y_list: Union[T, Sequence[T]]
                Either a single function or a sequence of functions
                
        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single function: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances
                
        Raises:
            ValueError:
                If the input types are not supported
            NotImplementedError:
                If derivative computation is not implemented
        """
        logger.debug("Computing Sobolev distances")
        
        if not isinstance(y_list, Sequence):
            return self.distance(x, y_list)
            
        return [self.distance(x, y) for y in y_list]
    
    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.
        
        Args:
            x: T
                The first function
            y: T
                The second function
                
        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise
                
        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking non-negativity")
        distance = self.distance(x, y)
        return distance >= 0.0
    
    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: T
                The first function
            y: T
                The second function
                
        Returns:
            bool:
                True if x and y are identical, False otherwise
                
        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking identity")
        return self.distance(x, y) == 0.0
    
    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).
        
        Args:
            x: T
                The first function
            y: T
                The second function
                
        Returns:
            bool:
                True if the symmetry condition holds, False otherwise
                
        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking symmetry")
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        return distance_xy == distance_yx
    
    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: T
                The first function
            y: T
                The second function
            z: T
                The third function
                
        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise
                
        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking triangle inequality")
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)
        return distance_xz <= distance_xy + distance_yz