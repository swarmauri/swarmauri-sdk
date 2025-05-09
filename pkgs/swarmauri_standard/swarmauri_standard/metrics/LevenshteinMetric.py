from typing import Sequence, Union, List, Literal
import logging
from swarmauri_standard.metrics.MetricBase import MetricBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LevenshteinMetric")
class LevenshteinMetric(MetricBase):
    """
    A concrete implementation of the MetricBase class that calculates the Levenshtein distance
    between two strings. The Levenshtein distance is a measure of the minimum number of single-character
    edits (insertions, deletions or substitutions) required to change one word into the other.

    Inherits From:
        MetricBase: Base class providing abstract methods for metric calculations

    Attributes:
        type: Literal["LevenshteinMetric"] = "LevenshteinMetric"
    """

    type: Literal["LevenshteinMetric"] = "LevenshteinMetric"

    def __init__(self) -> None:
        """
        Initializes the LevenshteinMetric class.
        """
        super().__init__()
        logger.debug("Initialized LevenshteinMetric")

    def distance(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> float:
        """
        Computes the Levenshtein distance between two strings.

        The Levenshtein distance is calculated as the minimum number of operations needed to
        transform one string into the other, where the operations allowed are:
        - Insertion of a character
        - Deletion of a character
        - Substitution of a character

        Args:
            x: The first string
            y: The second string

        Returns:
            float: The Levenshtein distance between x and y

        Raises:
            TypeError: If either x or y is not a string
        """
        if not isinstance(x, str) or not isinstance(y, str):
            raise TypeError("Both inputs must be strings")

        logger.debug(f"Calculating Levenshtein distance between '{x}' and '{y}'")
        return float(self._levenshtein_distance(x, y))

    def distances(
        self, xs: List[Union[str, Sequence]], ys: List[Union[str, Sequence]]
    ) -> List[List[float]]:
        """
        Computes pairwise Levenshtein distances between two lists of strings.

        Args:
            xs: First list of strings
            ys: Second list of strings

        Returns:
            List[List[float]]: Matrix of pairwise Levenshtein distances
        """
        logger.debug(
            f"Calculating pairwise Levenshtein distances between {len(xs)} and {len(ys)} strings"
        )
        return [[self.distance(x, y) for y in ys] for x in xs]

    def check_non_negativity(
        self, x: Union[str, Sequence], y: Union[str, Sequence]
    ) -> None:
        """
        Verifies the non-negativity axiom: distance(x, y) >= 0.

        Args:
            x: First string
            y: Second string

        Raises:
            ValueError: If the distance is negative
        """
        distance = self.distance(x, y)
        if distance < 0:
            raise ValueError(
                f"Non-negativity violation: distance({x}, {y}) = {distance} < 0"
            )

    def check_identity(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> None:
        """
        Verifies the identity of indiscernibles axiom: distance(x, y) = 0 if and only if x == y.

        Args:
            x: First string
            y: Second string

        Raises:
            ValueError: If distance(x, y) == 0 but x != y or vice versa
        """
        distance = self.distance(x, y)
        if (x == y and distance != 0) or (x != y and distance == 0):
            raise ValueError(
                f"Identity violation: x={'x'}, y={'y'}, distance={distance}"
            )

    def check_symmetry(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> None:
        """
        Verifies the symmetry axiom: distance(x, y) = distance(y, x).

        Args:
            x: First string
            y: Second string

        Raises:
            ValueError: If distance(x, y) != distance(y, x)
        """
        if self.distance(x, y) != self.distance(y, x):
            raise ValueError(
                f"Symmetry violation: distance({x}, {y}) != distance({y}, {x})"
            )

    def check_triangle_inequality(
        self, x: Union[str, Sequence], y: Union[str, Sequence], z: Union[str, Sequence]
    ) -> None:
        """
        Verifies the triangle inequality axiom: distance(x, z) <= distance(x, y) + distance(y, z).

        Args:
            x: First string
            y: Second string
            z: Third string

        Raises:
            ValueError: If distance(x, z) > distance(x, y) + distance(y, z)
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)

        if d_xz > d_xy + d_yz:
            raise ValueError(f"Triangle inequality violation: {d_xz} > {d_xy} + {d_yz}")

    def _levenshtein_distance(self, x: str, y: str) -> int:
        """
        Helper method to compute the Levenshtein distance using dynamic programming.

        Args:
            x: The first string
            y: The second string

        Returns:
            int: The Levenshtein distance between x and y
        """
        m, n = len(x), len(y)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if x[i - 1] == y[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # Deletion
                    dp[i][j - 1] + 1,  # Insertion
                    dp[i - 1][j - 1] + cost,
                )  # Substitution or no cost

        return dp[m][n]
