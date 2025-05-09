from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from typing import Union, Sequence, TypeVar
import logging

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T", str, Sequence[str])


@ComponentBase.register_type(MetricBase, "LevenshteinMetric")
class LevenshteinMetric(MetricBase):
    """
    Provides a concrete implementation of the Levenshtein distance metric.

    The Levenshtein distance is a measure of the minimum number of single-character edits (insertions, deletions or substitutions) required to change one string into the other.

    Inherits From:
        MetricBase: Base class for metrics, providing foundational functionality.

    Provides:
        - Implementation of the Levenshtein distance algorithm
        - Compliance with the four main metric axioms
        - Logging functionality
        - Type hints and docstrings
        - PEP 8 and PEP 484 compliance
    """

    def __init__(self):
        """
        Initialize the LevenshteinMetric instance.

        Initializes the base class and sets up logging.
        """
        super().__init__()
        logger.debug("LevenshteinMetric instance initialized")

    def distance(self, x: str, y: str) -> float:
        """
        Compute the Levenshtein distance between two strings.

        Args:
            x: str
                The first string to compare
            y: str
                The second string to compare

        Returns:
            float:
                The computed Levenshtein distance between x and y

        Raises:
            ValueError:
                If inputs are not strings
        """
        if not isinstance(x, str) or not isinstance(y, str):
            raise ValueError("Inputs must be strings")

        # Handle edge cases
        if x == y:
            return 0.0
        if len(x) == 0:
            return float(len(y))
        if len(y) == 0:
            return float(len(x))

        # Initialize the matrix
        m, n = len(x), len(y)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize the first row and column
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # Fill in the rest of the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if x[i - 1] == y[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # Deletion
                    dp[i][j - 1] + 1,  # Insertion
                    dp[i - 1][j - 1] + cost,
                )  # Substitution or no cost

        # The bottom-right cell contains the result
        return float(dp[m][n])

    def distances(
        self, x: T, y_list: Union[T, Sequence[T]]
    ) -> Union[float, Sequence[float]]:
        """
        Compute the Levenshtein distance(s) between a string and one or more strings.

        Args:
            x: T
                The reference string
            y_list: Union[T, Sequence[T]]
                Either a single string or a sequence of strings

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single string: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            ValueError:
                If inputs are not strings
        """
        if not isinstance(x, str):
            raise ValueError("Reference input must be a string")

        if isinstance(y_list, str):
            return self.distance(x, y_list)
        elif isinstance(y_list, Sequence):
            return [self.distance(x, y) for y in y_list]
        else:
            raise ValueError("y_list must be a string or sequence of strings")
