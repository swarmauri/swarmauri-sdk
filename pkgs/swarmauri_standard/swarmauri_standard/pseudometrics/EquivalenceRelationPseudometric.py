from typing import Union, List, Any, Tuple, Literal
from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "EquivalenceRelationPseudometric")
class EquivalenceRelationPseudometric(PseudometricBase):
    """
    A pseudometric implementation based on an equivalence relation.

    This class implements a pseudometric where the distance between two points is 0 if they are
    equivalent under the given equivalence relation, and 1 otherwise. This creates a quotient space
    where equivalent points are not distinguishable.

    Implements:
    - distance()
    - distances()
    - check_non_negativity()
    - check_symmetry()
    - check_triangle_inequality()
    - check_weak_identity()

    Attributes:
        equivalence_relation: A function that determines if two elements are equivalent.
            Must satisfy reflexivity, symmetry, and transitivity.
    """

    type: Literal["EquivalenceRelationPseudometric"] = "EquivalenceRelationPseudometric"
    equivalence_relation: callable
    resource: str = ResourceTypes.PSEUDOMETRIC.value

    def __init__(self, equivalence_relation: callable):
        """
        Initialize the equivalence relation pseudometric.

        Args:
            equivalence_relation: A function that takes two arguments and returns True
                if they are equivalent, False otherwise. Must satisfy reflexivity,
                symmetry, and transitivity.

        Raises:
            ValueError: If the equivalence_relation is not callable
        """
        super().__init__()
        if not callable(equivalence_relation):
            raise ValueError("equivalence_relation must be callable")
        self.equivalence_relation = equivalence_relation
        logger.debug("Initialized EquivalenceRelationPseudometric")

    def distance(self, x: Union[Any], y: Union[Any]) -> float:
        """
        Calculate the distance between two elements based on equivalence.

        Args:
            x: The first element to measure distance from
            y: The second element to measure distance to

        Returns:
            float: 0 if x and y are equivalent, 1 otherwise
        """
        logger.debug(f"Calculating distance between {x} and {y}")
        if self.equivalence_relation(x, y):
            return 0.0
        else:
            return 1.0

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
        logger.debug(f"Calculating distances from {x} to {y_list}")
        return [self.distance(x, y) for y in y_list]

    def check_non_negativity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Verify the non-negativity property of the pseudometric.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if distance is non-negative, False otherwise
        """
        distance = self.distance(x, y)
        return distance >= 0.0

    def check_symmetry(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Verify the symmetry property of the pseudometric.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if distance is symmetric, False otherwise
        """
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self, x: Union[Any], y: Union[Any], z: Union[Any]
    ) -> bool:
        """
        Verify the triangle inequality property of the pseudometric.

        Args:
            x: The first element
            y: The second element
            z: The third element

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        d_xz = self.distance(x, z)
        return d_xz <= d_xy + d_yz

    def check_weak_identity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Verify the weak identity of indiscernibles property of the pseudometric.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if weak identity holds, False otherwise
        """
        distance = self.distance(x, y)
        return (distance == 0.0) == self.equivalence_relation(x, y)
