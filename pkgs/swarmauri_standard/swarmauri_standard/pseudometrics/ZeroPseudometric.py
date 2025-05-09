from typing import TypeVar, Union, Sequence, Callable, Literal
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', Union[Sequence, str, Callable])

@ComponentBase.register_type(PseudometricBase, "ZeroPseudometric")
class ZeroPseudometric(PseudometricBase):
    """
    A trivial pseudometric that assigns zero distance between all pairs of points.

    This implementation satisfies all pseudometric axioms trivially by always
    returning a distance of 0.0, regardless of the input. It provides a valid
    mathematical structure but does not distinguish between different points.

    Inherits:
        PseudometricBase: Base class for pseudometric implementations
        ComponentBase: Base class for components in the system

    Attributes:
        type: Literal["ZeroPseudometric"] = "ZeroPseudometric"
            The type identifier for this pseudometric implementation
        resource: Literal["PSEUDOMETRIC"] = ResourceTypes.PSEUDOMETRIC.value
            The resource type identifier for this component
    """
    type: Literal["ZeroPseudometric"] = "ZeroPseudometric"
    resource: Literal["PSEUDOMETRIC"] = ResourceTypes.PSEUDOMETRIC.value

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def distance(self, x: Union[T, Callable], y: Union[T, Callable]) -> float:
        """
        Computes the pseudometric distance between two elements.

        Since this is a trivial pseudometric, the distance between any two
        points is always 0.0 regardless of their actual values.

        Args:
            x: Union[T, Callable]
                The first element to compute distance between
            y: Union[T, Callable]
                The second element to compute distance between

        Returns:
            float: The computed pseudometric distance, which is always 0.0
        """
        logger.debug("Computing ZeroPseudometric distance")
        return 0.0

    def distances(self, xs: Sequence[Union[T, Callable]], ys: Sequence[Union[T, Callable]]) -> list[float]:
        """
        Computes pairwise pseudometric distances between two sequences of elements.

        Since this is a trivial pseudometric, all distances in the resulting
        list will be 0.0 regardless of the input sequences.

        Args:
            xs: Sequence[Union[T, Callable]]
                The first sequence of elements
            ys: Sequence[Union[T, Callable]]
                The second sequence of elements

        Returns:
            list[float]: A list of computed pseudometric distances, all 0.0
        """
        logger.debug(f"Computing ZeroPseudometric distances for {len(xs)} elements")
        return [0.0] * len(xs)