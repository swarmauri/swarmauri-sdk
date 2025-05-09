from typing import Union, List, Sequence, Optional, Literal
import logging
import math
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm

T = TypeVar('T', Sequence[float], Union[float, Sequence[float]])

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LpMetric")
class LpMetric(MetricBase):
    """
    A concrete implementation of the MetricBase class for computing distances 
    using the Lp norm. This class provides the functionality to compute 
    distances between vectors or sequences using any Lp norm where p > 1.

    Attributes:
        p: The parameter of the Lp norm. Must be finite and greater than 1.
    """
    type: Literal["LpMetric"] = "LpMetric"
    p: float

    def __init__(self, p: float = 2.0):
        """
        Initializes the LpMetric instance with specified p value.

        Args:
            p: The parameter of the Lp norm. Must be finite and greater than 1.

        Raises:
            ValueError: If p is not finite or p <= 1.
        """
        super().__init__()
        if not (math.isfinite(p) and p > 1):
            raise ValueError(f"p must be finite and greater than 1, got {p}")
        self.p = p
        self.norm = GeneralLpNorm(p=p)

    def distance(self, x: Union[Sequence[float], float], y: Union[Sequence[float], float]) -> float:
        """
        Computes the Lp distance between two points x and y.

        Args:
            x: First point (vector or scalar)
            y: Second point (vector or scalar)

        Returns:
            float: The Lp distance between x and y

        Raises:
            ValueError: If inputs are invalid or cannot be processed.
        """
        logger.debug(f"Calculating L{self.p} distance between {x} and {y}")
        
        # Ensure inputs are sequences
        if not isinstance(x, Sequence):
            x = [x]
        if not isinstance(y, Sequence):
            y = [y]
            
        # Check equal length
        if len(x) != len(y):
            raise ValueError("Vectors must have the same length")
            
        difference = [x_i - y_i for x_i, y_i in zip(x, y)]
        return self.norm.compute(difference)

    def distances(self, xs: List[Union[Sequence[float], float]], 
                  ys: List[Union[Sequence[float], float]]) -> List[List[float]]:
        """
        Computes pairwise distances between two lists of points using Lp norm.

        Args:
            xs: First list of points
            ys: Second list of points

        Returns:
            List[List[float]]: Matrix of pairwise distances between points in xs and ys

        Raises:
            ValueError: If inputs are invalid or cannot be processed.
        """
        logger.debug(f"Calculating pairwise L{self.p} distances")
        
        if not isinstance(xs, list) or not isinstance(ys, list):
            raise ValueError("Inputs must be lists of points")
            
        distance_matrix = []
        for x in xs:
            row = []
            for y in ys:
                row.append(self.distance(x, y))
            distance_matrix.append(row)
            
        return distance_matrix

    def check_non_negativity(self, x: Union[Sequence[float], float], 
                            y: Union[Sequence[float], float]) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) < 0
        """
        logger.debug("Checking non-negativity axiom for LpMetric")
        distance = self.distance(x, y)
        if distance < 0:
            raise MetricViolationError(f"Non-negativity violated: distance = {distance}")

    def check_identity(self, x: Union[Sequence[float], float], 
                      y: Union[Sequence[float], float]) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        logger.debug("Checking identity of indiscernibles axiom for LpMetric")
        distance = self.distance(x, y)
        if distance == 0:
            if x != y:
                raise MetricViolationError(f"Identity violation: d(x,y)=0 but x≠y")
        else:
            if x == y:
                raise MetricViolationError(f"Identity violation: d(x,y)≠0 but x=y")

    def check_symmetry(self, x: Union[Sequence[float], float], 
                     y: Union[Sequence[float], float]) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) ≠ d(y,x)
        """
        logger.debug("Checking symmetry axiom for LpMetric")
        if self.distance(x, y) != self.distance(y, x):
            raise MetricViolationError(f"Symmetry violation: d(x,y)={self.distance(x,y)} ≠ d(y,x)={self.distance(y,x)}")

    def check_triangle_inequality(self, x: Union[Sequence[float], float], 
                                   y: Union[Sequence[float], float], 
                                   z: Union[Sequence[float], float]) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First point
            y: Second point
            z: Third point

        Raises:
            MetricViolationError: If d(x,z) > d(x,y) + d(y,z)
        """
        logger.debug("Checking triangle inequality axiom for LpMetric")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        
        if d_xz > d_xy + d_yz:
            raise MetricViolationError(f"Triangle inequality violation: {d_xz} > {d_xy} + {d_yz}")

    def __repr__(self) -> str:
        """
        Returns a string representation of the LpMetric instance.
        
        Returns:
            str: String representation showing the class name and p value.
        """
        return f"LpMetric(p={self.p})"