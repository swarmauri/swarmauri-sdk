from typing import Union, List, Any, Optional, Literal, Tuple
from abc import ABC
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from core.swarmauri_core.pseudometrics.IPseudometric import IPseudometric
from swarmauri_standard.swarmauri_standard.seminorms.LpSeminorm import LpSeminorm
import logging
import numpy as np

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "LpPseudometric")
class LpPseudometric(PseudometricBase):
    """
    A concrete implementation of the Lp-style pseudometric space.

    This class provides the implementation for computing the Lp pseudometric
    between functions or vectors. It inherits from the PseudometricBase class
    and implements the required methods for computing distances and checking
    pseudometric properties.

    The Lp pseudometric is defined as the Lp norm of the difference between
    two functions or vectors. The parameter p must be in the range [1, ∞].
    The domain or coordinates can be specified to measure the pseudometric
    over a subset of the full space.

    Attributes:
        p (float): The parameter controlling the pseudometric's sensitivity.
            Must be in the range [1, ∞].
        domain (Optional[Union[Tuple, List]]): The domain or coordinates over
            which to compute the pseudometric. If not specified, the entire
            domain is used.
    """

    type: Literal["LpPseudometric"] = "LpPseudometric"

    def __init__(self, p: float = 2.0, domain: Optional[Union[Tuple, List]] = None):
        """
        Initialize the LpPseudometric instance.

        Args:
            p (float): The parameter for the Lp pseudometric. Must be in [1, ∞].
                Defaults to 2.0.
            domain (Optional[Union[Tuple, List]]): The domain or coordinates
                over which to compute the pseudometric. Defaults to None.

        Raises:
            ValueError: If p is not in the range [1, ∞].
        """
        super().__init__()
        if p < 1:
            raise ValueError("p must be in the range [1, ∞]")
        self.p = p
        self.domain = domain
        logger.debug("Initialized LpPseudometric with p=%s and domain=%s", p, domain)

    def distance(self, x: Union[Any], y: Union[Any]) -> float:
        """
        Calculate the Lp pseudometric distance between two elements.

        Args:
            x: The first element to measure distance from
            y: The second element to measure distance to

        Returns:
            float: The non-negative distance between x and y
        """
        logger.debug("Computing Lp pseudometric distance between %s and %s", x, y)

        # Ensure the inputs are compatible
        if not self._check_compatibility(x, y):
            raise ValueError("Inputs must be compatible for distance computation")

        # Get the domain if specified
        domain = self.domain if self.domain is not None else None

        # Compute the difference
        diff = x - y

        # Compute the Lp norm of the difference
        if isinstance(diff, np.ndarray):
            return self._compute_lp_norm(diff, domain)
        else:
            raise TypeError("Unsupported input type for distance computation")

    def distances(
        self, x: Union[Any], y_list: Union[List[Union[Any]], Tuple[Union[Any]]]
    ) -> List[float]:
        """
        Calculate distances from a single element to a list of elements.

        Args:
            x: The reference element
            y_list: List or tuple of elements to measure distances to

        Returns:
            List[float]: List of distances from x to each element in y_list
        """
        logger.debug("Computing Lp pseudometric distances from %s to list", x)

        return [self.distance(x, y) for y in y_list]

    def check_non_negativity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies non-negativity: d(x,y) ≥ 0.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if distance is non-negative, False otherwise
        """
        logger.debug("Checking non-negativity for LpPseudometric")

        distance = self.distance(x, y)
        return distance >= 0

    def check_symmetry(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies symmetry: d(x,y) = d(y,x).

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if distance is symmetric, False otherwise
        """
        logger.debug("Checking symmetry for LpPseudometric")

        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self, x: Union[Any], y: Union[Any], z: Union[Any]
    ) -> bool:
        """
        Check if the distance satisfies triangle inequality: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: The first element
            y: The second element
            z: The third element

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality for LpPseudometric")

        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz

    def check_weak_identity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles:
        d(x,y) = 0 if and only if x and y are not distinguishable.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if weak identity holds, False otherwise
        """
        logger.debug("Checking weak identity for LpPseudometric")

        return self.distance(x, y) == 0

    def _check_compatibility(self, x: Any, y: Any) -> bool:
        """
        Check if the inputs are compatible for distance computation.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if inputs are compatible, False otherwise
        """
        logger.debug("Checking compatibility for distance computation")

        if not isinstance(x, type(y)):
            logger.warning("Inputs are of different types: %s and %s", type(x), type(y))
            return False
        return True

    def _compute_lp_norm(
        self, vector: np.ndarray, domain: Optional[Union[Tuple, List]] = None
    ) -> float:
        """
        Compute the Lp norm of a vector.

        Args:
            vector: The vector to compute the norm for
            domain: The domain or coordinates to consider. If None, uses the entire vector.

        Returns:
            float: The Lp norm of the vector
        """
        logger.debug("Computing Lp norm for vector with p=%s", self.p)

        if domain is not None:
            vector = vector[domain]

        return np.power(np.sum(np.abs(vector) ** self.p), 1.0 / self.p)
