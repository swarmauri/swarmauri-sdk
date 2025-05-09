from typing import Iterable, TypeVar, Optional
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for input types
InputTypes = TypeVar('InputTypes', IVector, IMatrix, Sequence, str, Callable)
DistanceInput = TypeVar('DistanceInput', InputTypes, Iterable[InputTypes])

@ComponentBase.register_model()
class PseudometricBase(IPseudometric, ComponentBase):
    """
    Base implementation of the IPseudometric interface.

    This class provides a concrete base implementation for pseudometric spaces.
    It handles generalized metric structures where the distance function is non-negative,
    symmetric, and satisfies the triangle inequality, but does not necessarily
    distinguish between distinct points.

    All methods in this class are abstract and must be implemented by subclasses.
    """
    
    resource: Optional[str] = Field(default=ResourceTypes.PSEUDOMETRIC.value)
    
    def distance(self, x: InputTypes, y: InputTypes) -> float:
        """
        Compute the distance between two points x and y.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            float:
                The distance between x and y

        Raises:
            NotImplementedError:
                This method must be implemented by subclasses
        """
        logger.error("distance method not implemented by subclass")
        raise NotImplementedError("Subclasses must implement the distance method")

    def distances(self, x: InputTypes, ys: Iterable[InputTypes]) -> Iterable[float]:
        """
        Compute distances from point x to multiple points ys.

        Args:
            x: InputTypes
                The reference point
            ys: Iterable[InputTypes]
                The collection of points to compute distances to

        Returns:
            Iterable[float]:
                An iterable of distances from x to each point in ys

        Raises:
            NotImplementedError:
                This method must be implemented by subclasses
        """
        logger.error("distances method not implemented by subclass")
        raise NotImplementedError("Subclasses must implement the distances method")

    def check_non_negativity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies non-negativity.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) >= 0, False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclasses
        """
        logger.error("check_non_negativity method not implemented by subclass")
        raise NotImplementedError("Subclasses must implement the check_non_negativity method")

    def check_symmetry(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies symmetry.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) == distance(y, x), False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclasses
        """
        logger.error("check_symmetry method not implemented by subclass")
        raise NotImplementedError("Subclasses must implement the check_symmetry method")

    def check_triangle_inequality(self, x: InputTypes, y: InputTypes, z: InputTypes) -> bool:
        """
        Check if the distance satisfies the triangle inequality.

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

        Raises:
            NotImplementedError:
                This method must be implemented by subclasses
        """
        logger.error("check_triangle_inequality method not implemented by subclass")
        raise NotImplementedError("Subclasses must implement the check_triangle_inequality method")

    def check_weak_identity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if x == y implies distance(x, y) == 0, False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclasses
        """
        logger.error("check_weak_identity method not implemented by subclass")
        raise NotImplementedError("Subclasses must implement the check_weak_identity method")