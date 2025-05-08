from typing import Optional, Literal, Union
import logging
from pydantic import Field

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_base.ComponentBase import ComponentBase

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "LevenshteinMetric")
class LevenshteinMetric(MetricBase):
    """
    Levenshtein distance metric for measuring string similarity.
    
    The Levenshtein distance is a string metric for measuring the difference
    between two sequences. It is calculated as the minimum number of single-character
    edits (insertions, deletions, or substitutions) required to change one string
    into another.
    
    Attributes
    ----------
    type : Literal["LevenshteinMetric"]
        The type identifier for this metric
    case_sensitive : bool
        Whether the comparison should be case-sensitive
    """
    type: Literal["LevenshteinMetric"] = "LevenshteinMetric"
    case_sensitive: bool = Field(default=True, description="Whether string comparison is case-sensitive")
    
    def distance(self, x: str, y: str) -> float:
        """
        Calculate the Levenshtein distance between two strings.
        
        Parameters
        ----------
        x : str
            First string
        y : str
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
        # Validate input types
        if not isinstance(x, str) or not isinstance(y, str):
            error_msg = f"Both inputs must be strings, got {type(x)} and {type(y)}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        # Apply case sensitivity setting
        if not self.case_sensitive:
            x = x.lower()
            y = y.lower()
        
        # Handle edge cases
        if x == y:
            return 0
        if len(x) == 0:
            return len(y)
        if len(y) == 0:
            return len(x)
        
        # Initialize the distance matrix
        # matrix[i][j] will hold the Levenshtein distance between
        # the first i characters of x and the first j characters of y
        matrix = [[0 for _ in range(len(y) + 1)] for _ in range(len(x) + 1)]
        
        # Initialize the first row and column
        for i in range(len(x) + 1):
            matrix[i][0] = i
        for j in range(len(y) + 1):
            matrix[0][j] = j
        
        # Fill the matrix
        for i in range(1, len(x) + 1):
            for j in range(1, len(y) + 1):
                # If characters match, no additional cost
                if x[i-1] == y[j-1]:
                    substitution_cost = 0
                else:
                    substitution_cost = 1
                
                # Calculate costs for each possible operation
                deletion = matrix[i-1][j] + 1
                insertion = matrix[i][j-1] + 1
                substitution = matrix[i-1][j-1] + substitution_cost
                
                # Take the minimum cost operation
                matrix[i][j] = min(deletion, insertion, substitution)
        
        # The bottom-right cell contains the Levenshtein distance
        result = matrix[len(x)][len(y)]
        logger.debug(f"Levenshtein distance between '{x}' and '{y}' is {result}")
        return float(result)
    
    def are_identical(self, x: str, y: str) -> bool:
        """
        Check if two strings are identical according to the Levenshtein metric.
        
        Two strings are identical if their Levenshtein distance is zero.
        
        Parameters
        ----------
        x : str
            First string
        y : str
            Second string
            
        Returns
        -------
        bool
            True if the strings are identical, False otherwise
            
        Raises
        ------
        TypeError
            If inputs are not strings
        """
        # Validate input types
        if not isinstance(x, str) or not isinstance(y, str):
            error_msg = f"Both inputs must be strings, got {type(x)} and {type(y)}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        # Apply case sensitivity setting
        if not self.case_sensitive:
            return x.lower() == y.lower()
        
        return x == y
    
    def similarity(self, x: str, y: str) -> float:
        """
        Calculate a similarity score between two strings based on Levenshtein distance.
        
        The similarity is normalized to a value between 0 and 1, where:
        - 1 means the strings are identical
        - 0 means the strings are completely different
        
        Parameters
        ----------
        x : str
            First string
        y : str
            Second string
            
        Returns
        -------
        float
            A similarity score between 0 and 1
            
        Raises
        ------
        TypeError
            If inputs are not strings
        """
        # Validate input types
        if not isinstance(x, str) or not isinstance(y, str):
            error_msg = f"Both inputs must be strings, got {type(x)} and {type(y)}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        # Handle edge cases
        if x == y:
            return 1.0
        if len(x) == 0 and len(y) == 0:
            return 1.0
        if len(x) == 0 or len(y) == 0:
            return 0.0
        
        # Calculate Levenshtein distance
        lev_distance = self.distance(x, y)
        
        # Normalize by the length of the longer string
        max_len = max(len(x), len(y))
        similarity = 1.0 - (lev_distance / max_len)
        
        logger.debug(f"Similarity between '{x}' and '{y}' is {similarity}")
        return similarity