from typing import Union, Sequence, TypeVar, Any
import logging
import math
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_standard.swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', int, float, Sequence, str, bytes)

@ComponentBase.register_type(MetricBase, "LpMetric")
class LpMetric(MetricBase):
    """
    Provides a concrete implementation of the MetricBase class for computing 
    distances using the Lp norm. This class allows for parameterized 
    distance calculations across vector spaces and sequences.

    Inherits From:
        MetricBase: Abstract base class for metric spaces.
        ComponentBase: Base class for components in the system.

    Attributes:
        p: float
            The parameter for the Lp norm. Must be greater than 1.
        norm: GeneralLpNorm
            Instance of GeneralLpNorm for computing Lp norms.

    Provides:
        - Implementation of the distance method using Lp norm
        - Parameterized distance calculations
        - Validation of input types and parameters
    """
    p: float = Field(..., gt=1, le=math.inf)
    norm: GeneralLpNorm
    type: Literal["LpMetric"] = "LpMetric"
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)

    def __init__(self, p: float):
        """
        Initializes the LpMetric instance with the specified p value.

        Args:
            p: float
                The parameter for the Lp norm. Must be greater than 1 and finite.

        Raises:
            ValueError: If p is not greater than 1 or not finite.
        """
        super().__init__()
        self.p = p
        self.norm = GeneralLpNorm(p)
        logger.debug("LpMetric instance initialized with p = %s", p)

    def distance(self, x: T, y: T) -> float:
        """
        Compute the Lp distance between two points.

        Args:
            x: T
                The first point to compare
            y: T
                The second point to compare

        Returns:
            float:
                The computed Lp distance between x and y

        Raises:
            ValueError:
                If the input types are not supported or have different lengths
            TypeError:
                If the input types are incompatible
        """
        logger.debug("Computing Lp distance with p = %s", self.p)
        try:
            if isinstance(x, (int, float) and isinstance(y, (int, float))):
                return abs(x - y) ** self.p ** (1.0 / self.p)
            
            if len(x) != len(y):
                raise ValueError("Input vectors must have the same length")
            
            differences = (abs(a - b) for a, b in zip(x, y))
            return self.norm.compute(differences)
            
        except Exception as e:
            logger.error("Failed to compute Lp distance: %s", str(e))
            raise ValueError("Failed to compute Lp distance") from e

    def distances(self, x: T, y_list: Union[T, Sequence[T]]) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a point and one or more points.

        Args:
            x: T
                The reference point
            y_list: Union[T, Sequence[T]]
                Either a single point or a sequence of points

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single point: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            ValueError:
                If the input types are not supported
            TypeError:
                If the input types are incompatible
        """
        logger.debug("Computing Lp distances with p = %s", self.p)
        try:
            if not isinstance(y_list, Sequence):
                return self.distance(x, y_list)
            
            return [self.distance(x, y) for y in y_list]
            
        except Exception as e:
            logger.error("Failed to compute Lp distances: %s", str(e))
            raise ValueError("Failed to compute Lp distances") from e

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking non-negativity axiom")
        try:
            distance = self.distance(x, y)
            return distance >= 0
        except Exception as e:
            logger.error("Failed to check non-negativity: %s", str(e))
            raise ValueError("Failed to check non-negativity") from e

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the identity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking identity axiom")
        try:
            distance = self.distance(x, y)
            return distance == 0
        except Exception as e:
            logger.error("Failed to check identity: %s", str(e))
            raise ValueError("Failed to check identity") from e

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking symmetry axiom")
        try:
            d_xy = self.distance(x, y)
            d_yx = self.distance(y, x)
            return d_xy == d_yx
        except Exception as e:
            logger.error("Failed to check symmetry: %s", str(e))
            raise ValueError("Failed to check symmetry") from e

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first point
            y: T
                The second point
            z: T
                The third point

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        logger.debug("Checking triangle inequality axiom")
        try:
            d_xz = self.distance(x, z)
            d_xy = self.distance(x, y)
            d_yz = self.distance(y, z)
            return d_xz <= d_xy + d_yz
        except Exception as e:
            logger.error("Failed to check triangle inequality: %s", str(e))
            raise ValueError("Failed to check triangle inequality") from e