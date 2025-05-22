import logging
from abc import ABC, abstractmethod
from typing import Any, List, Union

from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)


class IMetric(ABC):
    """
    Interface for proper metric spaces.

    This interface defines the contract enforcing the full metric axioms:
    - Non-negativity: d(x,y) ≥ 0
    - Identity of indiscernibles (point separation): d(x,y) = 0 if and only if x = y
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)

    Implementations must support various input types including vectors, matrices,
    sequences, strings, and callables.
    """

    @abstractmethod
    def distance(self, x: Any, y: Any) -> float:
        """
        Calculate the distance between two points.

        Parameters
        ----------
        x : Any
            First point
        y : Any
            Second point

        Returns
        -------
        float
            The distance between x and y

        Raises
        ------
        ValueError
            If inputs are incompatible with the metric
        TypeError
            If input types are not supported
        """
        pass

    @abstractmethod
    def distances(self, x: Any, y: Any) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate distances between collections of points.

        Parameters
        ----------
        x : Any
            First collection of points
        y : Any
            Second collection of points

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix or vector of distances between points in x and y

        Raises
        ------
        ValueError
            If inputs are incompatible with the metric
        TypeError
            If input types are not supported
        """
        pass

    @abstractmethod
    def check_non_negativity(self, x: Any, y: Any) -> bool:
        """
        Check if the metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Parameters
        ----------
        x : Any
            First point
        y : Any
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass

    @abstractmethod
    def check_identity_of_indiscernibles(self, x: Any, y: Any) -> bool:
        """
        Check if the metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : Any
            First point
        y : Any
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass

    @abstractmethod
    def check_symmetry(self, x: Any, y: Any) -> bool:
        """
        Check if the metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : Any
            First point
        y : Any
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, x: Any, y: Any, z: Any) -> bool:
        """
        Check if the metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : Any
            First point
        y : Any
            Second point
        z : Any
            Third point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass
