import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Sequence, Union

import numpy as np
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)

# Define a type alias for supported metric input types
MetricInput = Union[
    int,
    float,  # Scalar values
    List[Union[int, float]],  # List of scalars
    Sequence[Union[int, float]],  # Any sequence of scalars
    np.ndarray,  # NumPy arrays
    IVector,  # Vector interface
    IMatrix,  # Matrix interface
    Dict[str, Union[int, float]],  # Dictionary with numeric values
]

# For collections of inputs
MetricInputCollection = Union[List[MetricInput], Sequence[MetricInput]]


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
    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the distance between two points.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
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
    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate distances between collections of points.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of points
        y : Union[MetricInput, MetricInputCollection]
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
    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass

    @abstractmethod
    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass

    @abstractmethod
    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass

    @abstractmethod
    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point
        z : MetricInput
            Third point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        pass
