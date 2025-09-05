import logging
from typing import List, Literal, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LevenshteinMetric")
class LevenshteinMetric(MetricBase):
    """
    Implementation of Levenshtein distance metric.

    Levenshtein distance is a string metric for measuring the difference between two sequences.
    It represents the minimum number of single-character edits (insertions, deletions, or
    substitutions) required to change one string into another.

    This metric is widely used in natural language processing and bioinformatics for
    measuring the similarity between strings.
    """

    type: Literal["LevenshteinMetric"] = "LevenshteinMetric"

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the Levenshtein distance between two strings.

        Parameters
        ----------
        x : MetricInput
            First string
        y : MetricInput
            Second string

        Returns
        -------
        float
            The Levenshtein distance between x and y

        Raises
        ------
        TypeError
            If inputs are not strings
        """
        if not isinstance(x, str) or not isinstance(y, str):
            logger.error(f"Inputs must be strings, got {type(x)} and {type(y)}")
            raise TypeError(f"Inputs must be strings, got {type(x)} and {type(y)}")

        logger.debug(f"Calculating Levenshtein distance between '{x}' and '{y}'")

        # If either string is empty, the distance is the length of the other string
        if len(x) == 0:
            return len(y)
        if len(y) == 0:
            return len(x)

        # Initialize the matrix
        # The matrix has len(x)+1 rows and len(y)+1 columns
        matrix = [[0 for _ in range(len(y) + 1)] for _ in range(len(x) + 1)]

        # Initialize the first row and column
        for i in range(len(x) + 1):
            matrix[i][0] = i
        for j in range(len(y) + 1):
            matrix[0][j] = j

        # Fill the matrix using dynamic programming
        for i in range(1, len(x) + 1):
            for j in range(1, len(y) + 1):
                # If characters match, no additional cost
                if x[i - 1] == y[j - 1]:
                    cost = 0
                else:
                    cost = 1

                # Calculate the minimum of the three possible operations:
                # deletion, insertion, or substitution
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # deletion
                    matrix[i][j - 1] + 1,  # insertion
                    matrix[i - 1][j - 1] + cost,  # substitution
                )

        # The bottom-right cell contains the Levenshtein distance
        return matrix[len(x)][len(y)]

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate Levenshtein distances between collections of strings.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of strings
        y : Union[MetricInput, MetricInputCollection]
            Second collection of strings

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix of distances between strings in x and y

        Raises
        ------
        TypeError
            If inputs are not collections of strings
        """
        logger.debug("Calculating Levenshtein distances between collections")

        # Convert numpy arrays to lists if necessary
        if isinstance(x, np.ndarray):
            x = x.tolist()
        if isinstance(y, np.ndarray):
            y = y.tolist()

        # Validate input types
        if not isinstance(x, list) or not isinstance(y, list):
            logger.error(
                f"Inputs must be lists or numpy arrays, got {type(x)} and {type(y)}"
            )
            raise TypeError(
                f"Inputs must be lists or numpy arrays, got {type(x)} and {type(y)}"
            )

        # Validate that all elements are strings
        for i, item in enumerate(x):
            if not isinstance(item, str):
                logger.error(
                    f"All elements must be strings, found {type(item)} at index {i} in x"
                )
                raise TypeError(
                    f"All elements must be strings, found {type(item)} at index {i} in x"
                )

        for i, item in enumerate(y):
            if not isinstance(item, str):
                logger.error(
                    f"All elements must be strings, found {type(item)} at index {i} in y"
                )
                raise TypeError(
                    f"All elements must be strings, found {type(item)} at index {i} in y"
                )

        # Create a matrix of distances
        result = [[self.distance(xi, yi) for yi in y] for xi in x]

        # If only one string in x, return a vector
        if len(x) == 1:
            return result[0]

        return result

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Levenshtein metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Levenshtein distance is always non-negative by definition.

        Parameters
        ----------
        x : MetricInput
            First string
        y : MetricInput
            Second string

        Returns
        -------
        bool
            True, as Levenshtein distance is always non-negative
        """
        logger.debug(f"Checking non-negativity axiom for '{x}' and '{y}'")

        # Levenshtein distance is always non-negative as it counts the number of operations
        # which cannot be negative
        return True

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Levenshtein metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First string
        y : MetricInput
            Second string

        Returns
        -------
        bool
            True if d(x,y) = 0 iff x = y, False otherwise
        """
        logger.debug(f"Checking identity of indiscernibles axiom for '{x}' and '{y}'")

        # The distance is 0 if and only if the strings are identical
        return (self.distance(x, y) == 0) == (x == y)

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Levenshtein metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First string
        y : MetricInput
            Second string

        Returns
        -------
        bool
            True if d(x,y) = d(y,x), False otherwise
        """
        logger.debug(f"Checking symmetry axiom for '{x}' and '{y}'")

        # Calculate distances in both directions and check if they're equal
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)

        return d_xy == d_yx

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the Levenshtein metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First string
        y : MetricInput
            Second string
        z : MetricInput
            Third string

        Returns
        -------
        bool
            True if d(x,z) ≤ d(x,y) + d(y,z), False otherwise
        """
        logger.debug(f"Checking triangle inequality axiom for '{x}', '{y}', and '{z}'")

        # Calculate the three distances
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        d_xz = self.distance(x, z)

        # Check if the triangle inequality holds
        return d_xz <= d_xy + d_yz
