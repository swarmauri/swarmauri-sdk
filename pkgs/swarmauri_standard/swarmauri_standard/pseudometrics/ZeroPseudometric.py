from typing import Union, List, Any
from abc import ABC
import logging

logger = logging.getLogger(__name__)


class ZeroPseudometric(PseudometricBase):
    """
    A trivial pseudometric that assigns zero distance between all pairs of points.

    This class implements a pseudometric space where the distance between any two
    points is always zero. This satisfies all the pseudometric axioms trivially.

    Inherits:
        PseudometricBase: Base class for pseudometric implementations
    """

    type: Literal["ZeroPseudometric"] = "ZeroPseudometric"

    def distance(self, x: Union[Any], y: Union[Any]) -> float:
        """
        Calculate the distance between two elements in the pseudometric space.

        Since this is a zero pseudometric, the distance will always be 0.0
        regardless of the input.

        Args:
            x: The first element to measure distance from
            y: The second element to measure distance to

        Returns:
            float: The distance between x and y, which is always 0.0
        """
        logger.debug("Calculating zero distance between two points")
        return 0.0

    def distances(
        self, x: Union[Any], y_list: Union[List[Union[Any]], Tuple[Union[Any]]]
    ) -> List[float]:
        """
        Calculate distances from a single element to a list of elements.

        Since this is a zero pseudometric, all distances will be 0.0
        regardless of the input.

        Args:
            x: The reference element
            y_list: List or tuple of elements to measure distances to

        Returns:
            List[float]: List of distances from x to each element in y_list,
                         which will all be 0.0
        """
        logger.debug("Calculating zero distances from one point to multiple points")
        return [0.0] * len(y_list)

    def check_non_negativity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies non-negativity: d(x,y) ≥ 0.

        Since the distance is always 0.0, this condition is always satisfied.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True, as distance is always non-negative
        """
        logger.debug("Checking non-negativity condition")
        return True

    def check_symmetry(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies symmetry: d(x,y) = d(y,x).

        Since the distance is always 0.0, this condition is always satisfied.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True, as distance is symmetric
        """
        logger.debug("Checking symmetry condition")
        return True

    def check_triangle_inequality(
        self, x: Union[Any], y: Union[Any], z: Union[Any]
    ) -> bool:
        """
        Check if the distance satisfies triangle inequality: d(x,z) ≤ d(x,y) + d(y,z).

        Since all distances are 0.0, this condition is always satisfied:
        0.0 ≤ 0.0 + 0.0

        Args:
            x: The first element
            y: The second element
            z: The third element

        Returns:
            bool: True, as triangle inequality holds
        """
        logger.debug("Checking triangle inequality condition")
        return True

    def check_weak_identity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles:
        d(x,y) = 0 if and only if x and y are not distinguishable.

        Since the distance is always 0.0, this condition is trivially satisfied.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True, as distance is always zero
        """
        logger.debug("Checking weak identity condition")
        return True
