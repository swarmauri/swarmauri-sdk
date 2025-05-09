from typing import Union, List, Literal, Optional
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LevenshteinMetric")
class LevenshteinMetric(MetricBase):
    """
    Implementation of the Levenshtein metric for calculating the minimum number of 
    single-character edits (insertions, deletions or substitutions) required to 
    change one string into the other.

    Inherits from MetricBase and implements the distance calculation between two 
    strings. This metric is particularly useful in NLP and bioinformatics for 
    measuring string similarity.
    """
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)
    type: Literal["LevenshteinMetric"] = "LevenshteinMetric"

    def distance(
        self, 
        x: Union[str, List[str]], 
        y: Union[str, List[str]]
    ) -> float:
        """
        Compute the Levenshtein distance between two strings.

        The Levenshtein distance is a measure of the minimum number of single-character 
        edits (insertions, deletions or substitutions) required to change one string 
        into the other.

        Args:
            x: The first string or list of characters.
            y: The second string or list of characters.

        Returns:
            float: The Levenshtein distance between x and y.

        Example:
            >>> distance("kitten", "sitting")
            3
            Substitute 's' for 'k', substitute 'i' for 'e', append 'g'.
        """
        logger.debug("Calculating Levenshtein distance between strings")
        
        # Convert lists to strings if necessary
        x_str = ''.join(x) if isinstance(x, list) else x
        y_str = ''.join(y) if isinstance(y, list) else y

        # Handle edge cases
        if not x_str and not y_str:
            return 0.0
        if not x_str:
            return float(len(y_str))
        if not y_str:
            return float(len(x_str))

        # Create a table to store results of subproblems
        dp = [[0 for _ in range(len(y_str) + 1)] for _ in range(len(x_str) + 1)]

        # Initialize the table
        for i in range(len(x_str) + 1):
            dp[i][0] = i
        for j in range(len(y_str) + 1):
            dp[0][j] = j

        # Fill the table
        for i in range(1, len(x_str) + 1):
            for j in range(1, len(y_str) + 1):
                cost = 0 if x_str[i-1] == y_str[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # Deletion
                    dp[i][j-1] + 1,      # Insertion
                    dp[i-1][j-1] + cost  # Substitution
                )

        return float(dp[len(x_str)][len(y_str)])

    def distances(
        self, 
        x: Union[str, List[str]], 
        ys: List[Union[str, List[str]]]
    ) -> List[float]:
        """
        Compute distances from a reference string to multiple strings.

        Args:
            x: The reference string.
            ys: List of strings to compute distances to.

        Returns:
            List[float]: List of Levenshtein distances from x to each string in ys.
        """
        return [self.distance(x, y) for y in ys]

    def check_non_negativity(
        self, 
        x: Union[str, List[str]], 
        y: Union[str, List[str]]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.
        """
        distance = self.distance(x, y)
        return Literal[True](distance >= 0)

    def check_identity(
        self, 
        x: Union[str, List[str]], 
        y: Union[str, List[str]]
    ) -> Literal[True]:
        """
        Verify the identity property: d(x, y) = 0 if and only if x = y.
        """
        return Literal[True](self.distance(x, y) == 0 if x == y else True)

    def check_symmetry(
        self, 
        x: Union[str, List[str]], 
        y: Union[str, List[str]]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).
        """
        return Literal[True](self.distance(x, y) == self.distance(y, x))

    def check_triangle_inequality(
        self, 
        x: Union[str, List[str]], 
        y: Union[str, List[str]], 
        z: Union[str, List[str]]
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return Literal[True](d_xz <= d_xy + d_yz)