from typing import TypeVar, Union, Sequence, Optional, Literal, Iterable
import logging
import numpy as np

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for input types
InputTypes = TypeVar('InputTypes', Sequence[float], Sequence[Sequence[float]], str, callable)
DistanceInput = TypeVar('DistanceInput', InputTypes, Iterable[InputTypes])

@ComponentBase.register_model()
class LpPseudometric(IPseudometric, ComponentBase):
    """
    A concrete implementation of the PseudometricBase class for Lp-style pseudometrics.

    This class provides an Lp-style pseudometric implementation that operates on function spaces.
    It allows for specifying particular domains or coordinates for the pseudometric computation.

    Attributes:
        p: float
            The order of the Lp space. Must satisfy p >= 1.
        domain: Optional[Union[int, float, Sequence[int], Sequence[float]]]
            The domain or coordinates over which to compute the pseudometric.
            If not provided, the entire space is considered.
        resource: str = ResourceTypes.PSEUDOMETRIC.value
            The resource type identifier for this component.
    """
    resource: str = ComponentBase.ResourceTypes.PSEUDOMETRIC.value
    type: Literal["LpPseudometric"] = "LpPseudometric"

    def __init__(self, p: float, domain: Optional[Union[int, float, Sequence[int], Sequence[float]]] = None):
        """
        Initialize the LpPseudometric instance.

        Args:
            p: float
                The order of the Lp space. Must satisfy p >= 1.
            domain: Optional[Union[int, float, Sequence[int], Sequence[float]]] = None
                The domain or coordinates over which to compute the pseudometric.
                If not provided, the entire space is considered.

        Raises:
            ValueError:
                If p is less than 1.
        """
        super().__init__()
        if p < 1:
            raise ValueError("p must be >= 1")
        self.p = p
        self.domain = domain

    def distance(self, x: InputTypes, y: InputTypes) -> float:
        """
        Compute the Lp-style pseudometric distance between two points x and y.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            float:
                The computed Lp pseudometric distance between x and y

        Raises:
            ValueError:
                If inputs cannot be processed
        """
        logger.debug("Computing Lp pseudometric distance between inputs of types %s and %s", type(x), type(y))
        
        try:
            # Convert inputs to numpy arrays if they're not already
            if not isinstance(x, np.ndarray):
                x = np.asarray(x)
            if not isinstance(y, np.ndarray):
                y = np.asarray(y)
            
            # Handle domain specification
            if self.domain is not None:
                x = x[self.domain]
                y = y[self.domain]
            
            # Compute absolute difference
            difference = np.abs(x - y)
            
            # Compute Lp norm of the difference
            if self.p == np.inf:
                distance = np.max(difference)
            else:
                # Compute sum of powered differences
                powered_diff = np.power(difference, self.p)
                if self.domain is not None:
                    # Sum over the specified domain
                    sum_diff = np.sum(powered_diff, axis=0)
                else:
                    # Flatten and sum
                    sum_diff = np.sum(powered_diff)
                
                # Take the p-root
                distance = np.power(sum_diff, 1.0 / self.p)
            
            return float(distance)
            
        except Exception as e:
            logger.error("Failed to compute Lp pseudometric distance: %s", str(e))
            raise ValueError(f"Failed to compute Lp pseudometric distance: {str(e)}")

    def distances(self, x: InputTypes, ys: Iterable[InputTypes]) -> Iterable[float]:
        """
        Compute distances from point x to multiple points ys.

        Args:
            x: InputTypes
                The reference point
            ys: Iterable[InputTypes]
                The collection of points to compute distances to

        Returns:
            Iterable[float]:
                An iterable of distances from x to each point in ys

        Raises:
            ValueError:
                If any input cannot be processed
        """
        logger.debug("Computing distances from input of type %s to %d other inputs", type(x), len(ys))
        
        try:
            return [self.distance(x, y) for y in ys]
            
        except Exception as e:
            logger.error("Failed to compute distances: %s", str(e))
            raise ValueError(f"Failed to compute distances: {str(e)}")

    def check_non_negativity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies non-negativity.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) >= 0, False otherwise
        """
        logger.debug("Checking non-negativity of distance between %s and %s", x, y)
        distance = self.distance(x, y)
        return distance >= 0.0

    def check_symmetry(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies symmetry.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) == distance(y, x), False otherwise
        """
        logger.debug("Checking symmetry between %s and %s", x, y)
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(self, x: InputTypes, y: InputTypes, z: InputTypes) -> bool:
        """
        Check if the distance satisfies the triangle inequality.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point
            z: InputTypes
                The third point

        Returns:
            bool:
                True if distance(x, z) <= distance(x, y) + distance(y, z), False otherwise
        """
        logger.debug("Checking triangle inequality for points %s, %s, %s", x, y, z)
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz

    def check_weak_identity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if x == y implies distance(x, y) == 0, False otherwise
        """
        logger.debug("Checking weak identity between %s and %s", x, y)
        # For weak identity, we only check if distance is zero when x and y are identical
        # Note: This is a weak form of identity - x and y may be different but have zero distance
        return self.distance(x, y) == 0.0