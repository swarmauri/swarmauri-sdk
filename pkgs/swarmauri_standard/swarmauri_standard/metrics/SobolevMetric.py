from typing import Union, List, Literal, Callable, Optional
from pydantic import Field
import numpy as np
import math
import logging

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from base.swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_standard.swarmauri_standard.norms.SobolevNorm import SobolevNorm

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "SobolevMetric")
class SobolevMetric(MetricBase):
    """
    Implementation of the Sobolev metric, which combines both function values and
    their derivatives in the distance calculation.

    Inherits From:
        MetricBase: Base implementation for metric spaces

    Attributes:
        resource: Type of resource this component represents
        order: The highest derivative order to consider in the Sobolev metric
    """

    resource: Literal["Metric"] = ResourceTypes.METRIC.value
    order: int = Field(default=2, description="Highest derivative order to consider")

    def __init__(self, order: int = 2):
        """
        Initialize the SobolevMetric with specified parameters.

        Args:
            order: The highest derivative order to include in the metric calculation
        """
        super().__init__()
        self.order = order

    def distance(
        self,
        x: Union[Callable, List[float], np.ndarray, str],
        y: Union[Callable, List[float], np.ndarray, str],
    ) -> float:
        """
        Compute the Sobolev distance between two functions.

        The distance is computed using the Sobolev norm, which combines the L2
        norms of the function values and their derivatives up to the specified order.

        Args:
            x: The first function. Can be a callable, list of values, or numpy array.
            y: The second function. Can be a callable, list of values, or numpy array.

        Returns:
            float: The computed Sobolev distance between x and y.

        Raises:
            ValueError: If input types are not compatible
        """
        logger.debug("Computing Sobolev distance")

        # Initialize total distance
        total_distance = 0.0

        # If inputs are callables (functions), evaluate at multiple points
        if callable(x) and callable(y):
            points = np.linspace(0, 1, 100)  # Evaluate at 100 points
            x_values = [x(p) for p in points]
            y_values = [y(p) for p in points]

            # Compute function values difference
            func_diff = np.array(x_values) - np.array(y_values)
            func_norm = np.linalg.norm(func_diff, 2)

            # Compute derivatives numerically for both functions
            x_derivs = self._compute_derivatives(x, points, self.order)
            y_derivs = self._compute_derivatives(y, points, self.order)

            # Compute norms for each derivative order
            for i in range(self.order):
                x_deriv = x_derivs[i]
                y_deriv = y_derivs[i]
                deriv_diff = x_deriv - y_deriv
                deriv_norm = np.linalg.norm(deriv_diff, 2)
                total_distance += deriv_norm

            total_distance += func_norm  # Add function norm

        elif isinstance(x, (np.ndarray, list)) and isinstance(y, (np.ndarray, list)):
            # Assume x and y are arrays containing function and derivative values
            # Split into function and derivatives
            if len(x) < 1 or len(y) < 1:
                raise ValueError("Insufficient elements in input arrays")

            func_x = x[0]
            func_y = y[0]
            func_diff = func_x - func_y
            func_norm = np.linalg.norm(func_diff, 2)

            # Sum derivatives up to specified order
            for i in range(1, min(self.order + 1, len(x))):
                deriv_x = x[i]
                deriv_y = y[i]
                deriv_diff = deriv_x - deriv_y
                deriv_norm = np.linalg.norm(deriv_diff, 2)
                total_distance += deriv_norm

            total_distance += func_norm

        elif isinstance(x, str) or isinstance(y, str):
            raise ValueError("String inputs not supported for Sobolev metric")

        else:
            raise ValueError(f"Unsupported input type(s): {type(x)}, {type(y)}")

        logger.debug(f"Computed Sobolev distance: {total_distance}")
        return total_distance

    def _compute_derivatives(
        self, func: Callable, points: np.ndarray, order: int
    ) -> List[np.ndarray]:
        """
        Compute numerical derivatives of a function at specified points up to given order.

        Args:
            func: The function to compute derivatives for
            points: Points where to evaluate the function and its derivatives
            order: Highest derivative order to compute

        Returns:
            List[np.ndarray]: List containing function values and its derivatives
        """
        derivs = []

        # Function values
        func_vals = np.array([func(p) for p in points])
        derivs.append(func_vals)

        # First derivative
        first_deriv = np.zeros_like(func_vals)
        h = 1e-8
        for i, p in enumerate(points):
            f_plus = func(p + h)
            f_minus = func(p - h)
            first_deriv[i] = (f_plus - f_minus) / (2 * h)
        derivs.append(first_deriv)

        # Higher-order derivatives
        for o in range(2, order + 1):
            prev_deriv = derivs[-1]
            current_deriv = np.zeros_like(prev_deriv)
            for i in range(len(points)):
                # Use central difference for better accuracy
                h = 1e-8
                prev_val = prev_deriv[i]
                f_plus = prev_deriv[i + 1] if i + 1 < len(prev_deriv) else prev_val
                f_minus = prev_deriv[i - 1] if i - 1 >= 0 else prev_val
                current_deriv[i] = (f_plus - f_minus) / (2 * h)
            derivs.append(current_deriv)

        return derivs

    def distances(
        self,
        x: Union[Callable, List[float], np.ndarray, str],
        ys: List[Union[Callable, List[float], np.ndarray, str]],
    ) -> List[float]:
        """
        Compute distances from a single point to multiple points.

        Args:
            x: The reference point. Can be a callable, list of values, or numpy array.
            ys: List of points to compute distances to. Each can be a callable,
                list of values, or numpy array.

        Returns:
            List[float]: List of distances from x to each point in ys.
        """
        return [self.distance(x, y) for y in ys]

    def check_non_negativity(
        self,
        x: Union[Callable, List[float], np.ndarray, str],
        y: Union[Callable, List[float], np.ndarray, str],
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be a callable, list of values, or numpy array.
            y: The second point. Can be a callable, list of values, or numpy array.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            AssertionError: If non-negativity is not satisfied.
        """
        distance = self.distance(x, y)
        if distance < 0:
            raise AssertionError(f"Non-negativity violated: distance = {distance}")
        return True

    def check_identity(
        self,
        x: Union[Callable, List[float], np.ndarray, str],
        y: Union[Callable, List[float], np.ndarray, str],
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be a callable, list of values, or numpy array.
            y: The second point. Can be a callable, list of values, or numpy array.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            AssertionError: If identity property is not satisfied.
        """
        distance = self.distance(x, y)
        if distance != 0:
            raise AssertionError(
                f"Identity property violated: d(x, y) = {distance} != 0"
            )
        return True

    def check_symmetry(
        self,
        x: Union[Callable, List[float], np.ndarray, str],
        y: Union[Callable, List[float], np.ndarray, str],
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be a callable, list of values, or numpy array.
            y: The second point. Can be a callable, list of values, or numpy array.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            AssertionError: If symmetry property is not satisfied.
        """
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        if not math.isclose(distance_xy, distance_yx, rel_tol=1e-9, abs_tol=1e-9):
            raise AssertionError(
                f"Symmetry violated: d(x, y) = {distance_xy}, d(y, x) = {distance_yx}"
            )
        return True

    def check_triangle_inequality(
        self,
        x: Union[Callable, List[float], np.ndarray, str],
        y: Union[Callable, List[float], np.ndarray, str],
        z: Union[Callable, List[float], np.ndarray, str],
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be a callable, list of values, or numpy array.
            y: The second point. Can be a callable, list of values, or numpy array.
            z: The third point. Can be a callable, list of values, or numpy array.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            AssertionError: If triangle inequality is not satisfied.
        """
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)

        if distance_xz > distance_xy + distance_yz + 1e-9:
            raise AssertionError(
                f"Triangle inequality violated: {distance_xz} > {distance_xy} + {distance_yz}"
            )
        return True
