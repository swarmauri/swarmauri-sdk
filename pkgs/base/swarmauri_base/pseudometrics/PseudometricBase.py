from abc import ABC
from typing import Union, List, Any, Optional
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from core.swarmauri_core.pseudometrics.IPseudometric import IPseudometric
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class PseudometricBase(IPseudometric, ComponentBase):
    """
    Base implementation for pseudometric space.

    This class provides a base implementation of the IPseudometric interface.
    It is not intended to be instantiated directly but should be subclassed
    by specific pseudometric implementations.

    Implements:
    - distance()
    - distances()
    - check_non_negativity()
    - check_symmetry()
    - check_triangle_inequality()
    - check_weak_identity()

    All methods raise NotImplementedError and must be implemented by subclasses.
    """

    resource: Optional[str] = ResourceTypes.PSEUDOMETRIC.value

    def __init__(self):
        """
        Initialize the base pseudometric class.
        """
        super().__init__()
        logger.debug("Initialized PseudometricBase")

    def distance(self, x: Union[Any], y: Union[Any]) -> float:
        """
        Calculate the distance between two elements in the pseudometric space.

        Args:
            x: The first element to measure distance from
            y: The second element to measure distance to

        Returns:
            float: The non-negative distance between x and y

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the distance method")

    def distances(self, x: Union[Any], y_list: Union[List[Union[Any]], Tuple[Union[Any]]]) -> List[float]:
        """
        Calculate distances from a single element to a list of elements.

        Args:
            x: The reference element
            y_list: List or tuple of elements to measure distances to

        Returns:
            List[float]: List of distances from x to each element in y_list

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the distances method")

    def check_non_negativity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies non-negativity: d(x,y) ≥ 0.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if distance is non-negative, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the check_non_negativity method")

    def check_symmetry(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies symmetry: d(x,y) = d(y,x).

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if distance is symmetric, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the check_symmetry method")

    def check_triangle_inequality(self, x: Union[Any], y: Union[Any], z: Union[Any]) -> bool:
        """
        Check if the distance satisfies triangle inequality: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: The first element
            y: The second element
            z: The third element

        Returns:
            bool: True if triangle inequality holds, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the check_triangle_inequality method")

    def check_weak_identity(self, x: Union[Any], y: Union[Any]) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles:
        d(x,y) = 0 if and only if x and y are not distinguishable.

        Args:
            x: The first element
            y: The second element

        Returns:
            bool: True if weak identity holds, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the check_weak_identity method")