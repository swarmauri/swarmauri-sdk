from typing import Union, List, Literal, Optional, Callable, Sequence
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
import logging
import numpy as np

logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "SupremumMetric")
class SupremumMetric(MetricBase):
    """
    Concrete implementation of the MetricBase class for computing the supremum metric.

    The supremum metric (L∞ metric) measures the maximum absolute difference between 
    corresponding components of two vectors. This implementation handles both vector 
    and callable inputs, evaluating callables at a specified number of points.

    Inherits From:
        MetricBase: Base class providing the interface for metric computations
        ComponentBase: Base class for all components in the system

    Attributes:
        resource: Type of resource this component represents
    """
    resource: Optional[str] = Field(default="metric")

    def __init__(self):
        """Initialize the SupremumMetric instance."""
        super().__init__()
        logger.debug("Initialized SupremumMetric")

    def distance(
        self, 
        x: Union[Callable, Sequence, np.ndarray, str, bytes], 
        y: Union[Callable, Sequence, np.ndarray, str, bytes]
    ) -> float:
        """
        Compute the supremum distance between two points.

        For vectors/arrays: Computes the maximum absolute difference between corresponding elements.
        For callables: Evaluates both functions at multiple points and takes the maximum difference.

        Args:
            x: The first point. Can be a vector, array, callable, string, or bytes.
            y: The second point. Can be a vector, array, callable, string, or bytes.

        Returns:
            float: The computed supremum distance between x and y.

        Raises:
            ValueError: If input types are not compatible
            TypeError: If input types are not supported
        """
        logger.debug("Computing supremum distance")

        try:
            if callable(x) and callable(y):
                # Evaluate both functions at multiple points
                x_eval = cast(Callable, x)
                y_eval = cast(Callable, y)
                # Use a default set of evaluation points (could be parameterized)
                eval_points = np.linspace(0, 1, 1000)
                x_values = x_eval(eval_points)
                y_values = y_eval(eval_points)
                differences = np.abs(x_values - y_values)
                return np.max(differences)

            elif isinstance(x, (Sequence, np.ndarray)) and isinstance(y, (Sequence, np.ndarray)):
                # Compute element-wise differences for arrays
                x_array = np.asarray(x)
                y_array = np.asarray(y)
                differences = np.abs(x_array - y_array)
                return np.max(differences)

            elif isinstance(x, (str, bytes)) and isinstance(y, (str, bytes)):
                # Handle string/bytes input as sequences of characters
                x_seq = [ord(c) for c in x]
                y_seq = [ord(c) for c in y]
                differences = np.abs(np.array(x_seq) - np.array(y_seq))
                return np.max(differences)

            else:
                raise ValueError(f"Incompatible input types: {type(x).__name__} and {type(y).__name__}")

        except Exception as e:
            logger.error(f"Error computing supremum distance: {str(e)}")
            raise TypeError("Failed to compute distance due to invalid input types") from e

    def distances(
        self, 
        x: Union[Callable, Sequence, np.ndarray, str, bytes], 
        ys: List[Union[Callable, Sequence, np.ndarray, str, bytes]]
    ) -> List[float]:
        """
        Compute distances from a single point x to multiple points ys.

        Args:
            x: The reference point. Can be a vector, array, callable, string, or bytes.
            ys: List of points to compute distances to. Each can be a vector, array, 
                callable, string, or bytes.

        Returns:
            List[float]: List of distances from x to each point in ys.

        Raises:
            ValueError: If input types are not compatible
            TypeError: If input types are not supported
        """
        logger.debug("Computing multiple supremum distances")
        
        distances = []
        for y in ys:
            distances.append(self.distance(x, y))
        return distances

    def check_non_negativity(
        self, 
        x: Union[Callable, Sequence, np.ndarray, str, bytes], 
        y: Union[Callable, Sequence, np.ndarray, str, bytes]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: distance(x, y) ≥ 0.

        Args:
            x: The first point. Can be a vector, array, callable, string, or bytes.
            y: The second point. Can be a vector, array, callable, string, or bytes.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            AssertionError: If non-negativity property is violated.
        """
        logger.debug("Checking non-negativity property")
        distance_value = self.distance(x, y)
        assert distance_value >= 0, "Non-negativity violation: Negative distance value"
        return True

    def check_identity(
        self, 
        x: Union[Callable, Sequence, np.ndarray, str, bytes], 
        y: Union[Callable, Sequence, np.ndarray, str, bytes]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: distance(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be a vector, array, callable, string, or bytes.
            y: The second point. Can be a vector, array, callable, string, or bytes.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            AssertionError: If identity property is violated.
        """
        logger.debug("Checking identity property")
        if x == y:
            distance_value = self.distance(x, y)
            assert distance_value == 0, "Identity violation: x == y but distance != 0"
        else:
            distance_value = self.distance(x, y)
            assert distance_value > 0, "Identity violation: x != y but distance == 0"
        return True

    def check_symmetry(
        self, 
        x: Union[Callable, Sequence, np.ndarray, str, bytes], 
        y: Union[Callable, Sequence, np.ndarray, str, bytes]
    ) -> Literal[True]:
        """
        Verify the symmetry property: distance(x, y) = distance(y, x).

        Args:
            x: The first point. Can be a vector, array, callable, string, or bytes.
            y: The second point. Can be a vector, array, callable, string, or bytes.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            AssertionError: If symmetry property is violated.
        """
        logger.debug("Checking symmetry property")
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        assert np.isclose(distance_xy, distance_yx), "Symmetry violation: distance(x, y) != distance(y, x)"
        return True

    def check_triangle_inequality(
        self, 
        x: Union[Callable, Sequence, np.ndarray, str, bytes], 
        y: Union[Callable, Sequence, np.ndarray, str, bytes], 
        z: Union[Callable, Sequence, np.ndarray, str, bytes]
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: distance(x, z) ≤ distance(x, y) + distance(y, z).

        Args:
            x: The first point. Can be a vector, array, callable, string, or bytes.
            y: The second point. Can be a vector, array, callable, string, or bytes.
            z: The third point. Can be a vector, array, callable, string, or bytes.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            AssertionError: If triangle inequality property is violated.
        """
        logger.debug("Checking triangle inequality property")
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)
        assert distance_xz <= (distance_xy + distance_yz), "Triangle inequality violation"
        return True