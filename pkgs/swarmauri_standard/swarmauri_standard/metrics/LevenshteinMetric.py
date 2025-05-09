from typing import Union, Sequence, Optional
from swarmauri_base.metrics import MetricBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LevenshteinMetric")
class LevenshteinMetric(MetricBase):
    """
    Provides a concrete implementation of the Levenshtein distance metric.
    
    The Levenshtein distance is a measure of the minimum number of single-character edits (insertions, deletions or substitutions) required to change one string into the other. This is useful in applications such as spell checkers, speech recognition systems, and molecular biology.
    """
    type: Literal["LevenshteinMetric"] = "LevenshteinMetric"
    
    def __init__(self):
        """
        Initializes the LevenshteinMetric class.
        """
        super().__init__()
        self.resource = "LevenshteinMetric"
        
    def distance(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> float:
        """
        Computes the Levenshtein distance between two strings.
        
        Args:
            x: Union[str, Sequence]
                The first string
            y: Union[str, Sequence]
                The second string
                
        Returns:
            float: The Levenshtein distance between x and y
        """
        # Ensure inputs are strings
        if not isinstance(x, str) or not isinstance(y, str):
            raise TypeError("Both inputs must be strings")
            
        # Handle edge cases
        if len(x) == 0:
            return len(y)
        if len(y) == 0:
            return len(x)
            
        # Initialize the matrix
        m, n = len(x), len(y)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill the first row and column
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        # Fill the rest of the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if x[i-1] == y[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # Deletion
                    dp[i][j-1] + 1,      # Insertion
                    dp[i-1][j-1] + cost  # Substitution
                )
                
        return dp[m][n]
    
    def distances(self, x: Union[str, Sequence], ys: Optional[Sequence[str]] = None) -> Union[float, Sequence[float]]:
        """
        Computes the Levenshtein distances from a reference string x to one or more strings y.
        
        Args:
            x: Union[str, Sequence]
                The reference string
            ys: Optional[Sequence[str]]
                Optional sequence of strings to compute distances to
                
        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances
        """
        if ys is None:
            return self.distance(x, ys)
        else:
            return [self.distance(x, y) for y in ys]
    
    def check_non_negativity(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: Union[str, Sequence]
                The first string
            y: Union[str, Sequence]
                The second string
                
        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        """
        distance = self.distance(x, y)
        return distance >= 0
        
    def check_identity(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: Union[str, Sequence]
                The first string
            y: Union[str, Sequence]
                The second string
                
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        return self.distance(x, y) == 0 if x == y else True
        
    def check_symmetry(self, x: Union[str, Sequence], y: Union[str, Sequence]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: Union[str, Sequence]
                The first string
            y: Union[str, Sequence]
                The second string
                
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        return self.distance(x, y) == self.distance(y, x)
        
    def check_triangle_inequality(self, x: Union[str, Sequence], y: Union[str, Sequence], z: Union[str, Sequence]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: Union[str, Sequence]
                The first string
            y: Union[str, Sequence]
                The second string
            z: Union[str, Sequence]
                The third string
                
        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)