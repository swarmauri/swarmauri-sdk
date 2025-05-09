import logging
import numpy as np
from typing import TypeVar, Union, Sequence, Callable, Optional, List
from abc import abstractmethod
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric

logger = logging.getLogger(__name__)

T = TypeVar('T', Sequence, Union[Sequence, Callable], str, Callable)

@ComponentBase.register_type(PseudometricBase, "LpPseudometric")
class LpPseudometric(PseudometricBase):
    """
    A concrete implementation of an Lp-style pseudometric without point separation.

    This class provides the implementation for computing the Lp pseudometric
    distance between elements in function space. The distance is computed using
    Lp integration over a specified domain or subset of coordinates.

    Inherits From:
        PseudometricBase: The base class for all pseudometric implementations.

    Attributes:
        p: float
            The parameter of the Lp pseudometric, must be in [1, ∞].
        domain: Optional[Union[List, Tuple, np.ndarray]]
            The domain or coordinates over which to compute the pseudometric.
            If None, the entire domain is used.
    """
    type: Literal["LpPseudometric"] = "LpPseudometric"
    resource: str = ResourceTypes.PSEUDOMETRIC.value
    
    def __init__(self, p: float = 2.0, domain: Optional[Union[List, Tuple, np.ndarray]] = None):
        """
        Initializes the LpPseudometric instance with the given parameters.

        Args:
            p: float, optional
                The parameter for the Lp pseudometric. Must be in [1, ∞).
                Defaults to 2.0.
            domain: Optional[Union[List, Tuple, np.ndarray]], optional
                The domain or coordinates to use for computing the pseudometric.
                If None, the entire domain is used. Defaults to None.

        Raises:
            ValueError: If p is not in [1, ∞).
        """
        super().__init__()
        if p < 1:
            logger.error("Invalid value for p. p must be in [1, ∞).")
            raise ValueError("p must be in [1, ∞)")
        self.p = p
        self.domain = np.asarray(domain) if domain is not None else None
        self.logger = logging.getLogger(__name__)

    def distance(self, x: Union[T, str, Callable], y: Union[T, str, Callable]) -> float:
        """
        Computes the Lp pseudometric distance between two elements.

        Args:
            x: Union[T, str, Callable]
                The first element to compute distance between
            y: Union[T, str, Callable]
                The second element to compute distance between

        Returns:
            float: The computed pseudometric distance

        Raises:
            NotImplementedError: If the input type is not supported
            ValueError: If the inputs cannot be processed
        """
        logger.info("Computing Lp pseudometric distance between elements of type %s and %s",
                  type(x).__name__, type(y).__name__)

        try:
            # Convert inputs to appropriate types
            x_vec = self._convert_to_array(x)
            y_vec = self._convert_to_array(y)

            # Apply domain restriction if specified
            if self.domain is not None:
                x_vec = x_vec[self.domain]
                y_vec = y_vec[self.domain]

            # Compute absolute difference
            diff = np.abs(x_vec - y_vec)

            # Compute Lp norm
            if self.p == np.inf:
                distance = np.max(diff)
            else:
                distance = np.power(np.sum(np.power(diff, self.p)), 1.0 / self.p)

            logger.info("Computed Lp pseudometric distance: %s", distance)
            return distance

        except Exception as e:
            logger.error("Error computing Lp pseudometric distance: %s", str(e))
            raise e

    def distances(self, xs: Sequence[Union[T, str, Callable]],
                  ys: Sequence[Union[T, str, Callable]]) -> List[float]:
        """
        Computes pairwise Lp pseudometric distances between two sequences of elements.

        Args:
            xs: Sequence[Union[T, str, Callable]]
                The first sequence of elements
            ys: Sequence[Union[T, str, Callable]]
                The second sequence of elements

        Returns:
            List[float]: A list of computed pseudometric distances

        Raises:
            ValueError: If the input sequences are not of the same length
        """
        logger.info("Computing pairwise Lp pseudometric distances")
        
        if len(xs) != len(ys):
            logger.error("Input sequences must be of the same length")
            raise ValueError("Input sequences must be of the same length")

        try:
            return [self.distance(x, y) for x, y in zip(xs, ys)]
        except Exception as e:
            logger.error("Error computing pairwise distances: %s", str(e))
            raise e

    def _convert_to_array(self, input: Union[T, str, Callable]) -> np.ndarray:
        """
        Converts the input to a numpy array.

        Args:
            input: Union[T, str, Callable]
                The input to convert

        Returns:
            np.ndarray: The converted numpy array

        Raises:
            NotImplementedError: If the input type is not supported
        """
        logger.info("Converting input of type %s to numpy array", type(input).__name__)

        try:
            if isinstance(input, (str, Callable)):
                # Handle special cases for strings or callables
                # This would need specific handling based on requirements
                # For now, convert to array via numpy
                return np.asarray(input)
            else:
                return np.asarray(input)
        except Exception as e:
            logger.error("Error converting input to array: %s", str(e))
            raise NotImplementedError(f"Input type {type(input).__name__} is not supported")