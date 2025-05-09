from typing import Iterable, TypeVar, Optional
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.swarmauri_standard.pseudometrics import PseudometricBase
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for input types
InputTypes = TypeVar("InputTypes")
DistanceInput = TypeVar("DistanceInput", InputTypes, Iterable[InputTypes])


@ComponentBase.register_type(PseudometricBase, "EquivalenceRelationPseudometric")
class EquivalenceRelationPseudometric(PseudometricBase):
    """
    A concrete implementation of the PseudometricBase class that defines a pseudometric
    based on an equivalence relation. Points are considered at distance 0 if they
    are equivalent under the relation and 1 otherwise.
    """

    type: str = "EquivalenceRelationPseudometric"

    def are_equivalent(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Checks if two points are equivalent under the equivalence relation.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if x and y are equivalent, False otherwise
        """
        return x == y  # Default equivalence based on object equality

    def distance(self, x: InputTypes, y: InputTypes) -> float:
        """
        Computes the distance between two points based on equivalence.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            float:
                0.0 if x and y are equivalent, 1.0 otherwise
        """
        if self.are_equivalent(x, y):
            return 0.0
        else:
            return 1.0

    def distances(self, x: InputTypes, ys: Iterable[InputTypes]) -> Iterable[float]:
        """
        Computes distances from a single point x to multiple points ys.

        Args:
            x: InputTypes
                The reference point
            ys: Iterable[InputTypes]
                Collection of points to compute distances to

        Returns:
            Iterable[float]:
                Iterable containing distances from x to each point in ys
        """
        return [self.distance(x, y) for y in ys]

    def check_non_negativity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Checks if the distance satisfies non-negativity.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) >= 0, False otherwise
        """
        return self.distance(x, y) >= 0

    def check_symmetry(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Checks if the distance satisfies symmetry.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) == distance(y, x), False otherwise
        """
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self, x: InputTypes, y: InputTypes, z: InputTypes
    ) -> bool:
        """
        Checks if the distance satisfies the triangle inequality.

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
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)

    def check_weak_identity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Checks if the distance satisfies weak identity of indiscernibles.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if x == y implies distance(x, y) == 0, False otherwise
        """
        return x == y if self.distance(x, y) == 0 else False
