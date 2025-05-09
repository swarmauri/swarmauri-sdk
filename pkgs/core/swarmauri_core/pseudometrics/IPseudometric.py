from abc import ABC, abstractmethod
from typing import List, Union, Callable
import logging
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class IPseudometric(ABC):
    """
    Interface for pseudometric space. Defines a distance structure that satisfies:
    - Non-negativity: d(x,y) ≥ 0
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    - Weak identity: d(x,y) = 0 does not necessarily imply x = y

    This interface provides methods for computing distances and validating the pseudometric properties.
    """

    @abstractmethod
    def distance(
        self,
        x: Union[IVector, IMatrix, List[float], str, Callable],
        y: Union[IVector, IMatrix, List[float], str, Callable]
    ) -> float:
        """
        Computes the distance between two elements.

        Args:
            x: First element to compute distance from
            y: Second element to compute distance to

        Returns:
            float: Distance between x and y

        Raises:
            TypeError: If input types are not supported
        """
        logger.debug(f"Computing distance between {x} and {y}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def distances(
        self,
        x: Union[IVector, IMatrix, List[float], str, Callable],
        y_list: List[Union[IVector, IMatrix, List[float], str, Callable]]
    ) -> List[float]:
        """
        Computes distances from a single element to multiple elements.

        Args:
            x: Reference element
            y_list: List of elements to compute distances to

        Returns:
            List[float]: List of distances from x to each element in y_list

        Raises:
            TypeError: If input types are not supported
        """
        logger.debug(f"Computing distances from {x} to {y_list}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_non_negativity(
        self,
        x: Union[IVector, IMatrix, List[float], str, Callable],
        y: Union[IVector, IMatrix, List[float], str, Callable]
    ) -> bool:
        """
        Verifies the non-negativity property: d(x,y) ≥ 0.

        Args:
            x: First element
            y: Second element

        Returns:
            bool: True if non-negativity holds, False otherwise
        """
        logger.debug(f"Checking non-negativity for {x} and {y}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_symmetry(
        self,
        x: Union[IVector, IMatrix, List[float], str, Callable],
        y: Union[IVector, IMatrix, List[float], str, Callable]
    ) -> bool:
        """
        Verifies the symmetry property: d(x,y) = d(y,x).

        Args:
            x: First element
            y: Second element

        Returns:
            bool: True if symmetry holds, False otherwise
        """
        logger.debug(f"Checking symmetry for {x} and {y}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_triangle_inequality(
        self,
        x: Union[IVector, IMatrix, List[float], str, Callable],
        y: Union[IVector, IMatrix, List[float], str, Callable],
        z: Union[IVector, IMatrix, List[float], str, Callable]
    ) -> bool:
        """
        Verifies the triangle inequality property: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First element
            y: Second element
            z: Third element

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug(f"Checking triangle inequality for {x}, {y}, {z}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_weak_identity(
        self,
        x: Union[IVector, IMatrix, List[float], str, Callable],
        y: Union[IVector, IMatrix, List[float], str, Callable]
    ) -> bool:
        """
        Verifies weak identity property: d(x,y) = 0 does not necessarily imply x = y.

        This method should be implemented to check if the space maintains weak identity.

        Args:
            x: First element
            y: Second element

        Returns:
            bool: True if weak identity holds (d(x,y)=0 does not imply x=y), False otherwise
        """
        logger.debug(f"Checking weak identity for {x} and {y}")
        raise NotImplementedError("Method not implemented")