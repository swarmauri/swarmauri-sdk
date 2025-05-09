from typing import Union, Sequence, List, Callable, Optional
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "EquivalenceRelationPseudometric")
class EquivalenceRelationPseudometric(PseudometricBase):
    """
    A concrete implementation of PseudometricBase that defines a pseudometric based on equivalence relations.
    
    This class creates a quotient space where the distance between points is 0 if they are equivalent under
    the given equivalence relation and 1 otherwise. The equivalence relation must satisfy reflexivity,
    symmetry, and transitivity.

    Inherits:
        PseudometricBase: Base class for pseudometric implementations
    """
    def __init__(self,
                 equivalence_function: Callable[[Union[str, Sequence, object], Union[str, Sequence, object]], bool] = None):
        """
        Initializes the EquivalenceRelationPseudometric instance.

        Args:
            equivalence_function: A callable that takes two arguments and returns True if they are considered
                equivalent under the equivalence relation. Defaults to a simple equality check if not provided.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.equivalence_function = equivalence_function if equivalence_function is not None else self._default_equivalence

    def _default_equivalence(self, x: object, y: object) -> bool:
        """
        Default equivalence function that checks for equality.

        Args:
            x: The first object to compare
            y: The second object to compare

        Returns:
            bool: True if x == y, False otherwise
        """
        return x == y

    def equivalence_function(self, x: object, y: object) -> bool:
        """
        Checks whether two objects are equivalent under the equivalence relation.

        Args:
            x: The first object to compare
            y: The second object to compare

        Returns:
            bool: True if x and y are equivalent, False otherwise
        """
        return self._equivalence_function(x, y)

    def distance(self, x: Union[str, Sequence, object], y: Union[str, Sequence, object]) -> float:
        """
        Computes the pseudometric distance between two elements based on equivalence.

        Args:
            x: The first element to compute distance between
            y: The second element to compute distance between

        Returns:
            float: 0.0 if x and y are equivalent, 1.0 otherwise
        """
        if self.equivalence_function(x, y):
            return 0.0
        else:
            return 1.0

    def distances(self, xs: Sequence[Union[str, Sequence, object]], ys: Sequence[Union[str, Sequence, object]]) -> List[float]:
        """
        Computes pairwise pseudometric distances between two sequences of elements.

        Args:
            xs: The first sequence of elements
            ys: The second sequence of elements

        Returns:
            List[float]: A list of distances where each element is the distance between corresponding elements in xs and ys
        """
        return [self.distance(x, y) for x, y in zip(xs, ys)]