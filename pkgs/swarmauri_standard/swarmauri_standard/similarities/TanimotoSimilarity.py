from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from typing import Union, Sequence, Optional, Literal
import logging
import numpy as np

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TanimotoSimilarity")
class TanimotoSimilarity(SimilarityBase):
    """
    Implementation of the Tanimoto similarity measure for real-valued vectors.
    
    The Tanimoto similarity is a generalization of the Jaccard index for 
    real-valued vectors. It is commonly used in cheminformatics for 
    comparing molecular fingerprints. The similarity is calculated as:
    
    S = (A·B) / (|A|² + |B|² - A·B)
    
    where A and B are vectors, A·B is the dot product, and |A| is the 
    Euclidean norm of vector A.
    
    Attributes:
        type: Literal["TanimotoSimilarity"] = "TanimotoSimilarity"
        is_symmetric: bool = True
        is_bounded: bool = True
    """
    type: Literal["TanimotoSimilarity"] = "TanimotoSimilarity"
    is_symmetric: bool = True
    is_bounded: bool = True

    def similarity(self, x: Union[Sequence[float], np.ndarray], 
                    y: Union[Sequence[float], np.ndarray]) -> float:
        """
        Calculate the Tanimoto similarity between two vectors.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            float: Tanimoto similarity between x and y
            
        Raises:
            ValueError: If either vector contains only zeros
        """
        logger.debug(f"Calculating Tanimoto similarity between {x} and {y}")
        
        # Convert to numpy arrays if not already
        x = np.asarray(x)
        y = np.asarray(y)
        
        # Handle edge case where both vectors are zero
        if np.all(x == 0) and np.all(y == 0):
            return 1.0
        if np.all(x == 0) or np.all(y == 0):
            return 0.0
        
        # Calculate dot product
        dot_product = np.dot(x, y)
        
        # Calculate magnitudes
        mag_x = np.dot(x, x)
        mag_y = np.dot(y, y)
        
        # Compute similarity
        similarity = dot_product / (mag_x + mag_y - dot_product)
        
        return similarity

    def similarities(self, xs: Union[Sequence[Sequence[float]], Sequence[np.ndarray]], 
                     ys: Union[Sequence[Sequence[float]], Sequence[np.ndarray]]) -> Sequence[float]:
        """
        Calculate Tanimoto similarities for multiple pairs of vectors.
        
        Args:
            xs: Sequence of first vectors
            ys: Sequence of second vectors
            
        Returns:
            Sequence[float]: Sequence of Tanimoto similarities for each pair
        """
        logger.debug(f"Calculating Tanimoto similarities between {xs} and {ys}")
        return [self.similarity(x, y) for x, y in zip(xs, ys)]

    def dissimilarity(self, x: Union[Sequence[float], np.ndarray], 
                      y: Union[Sequence[float], np.ndarray]) -> float:
        """
        Calculate the Tanimoto dissimilarity between two vectors.
        
        The dissimilarity is 1 minus the similarity.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            float: Tanimoto dissimilarity between x and y
        """
        logger.debug(f"Calculating Tanimoto dissimilarity between {x} and {y}")
        return 1.0 - self.similarity(x, y)

    def dissimilarities(self, xs: Union[Sequence[Sequence[float]], Sequence[np.ndarray]], 
                       ys: Union[Sequence[Sequence[float]], Sequence[np.ndarray]]) -> Sequence[float]:
        """
        Calculate Tanimoto dissimilarities for multiple pairs of vectors.
        
        Args:
            xs: Sequence of first vectors
            ys: Sequence of second vectors
            
        Returns:
            Sequence[float]: Sequence of Tanimoto dissimilarities for each pair
        """
        logger.debug(f"Calculating Tanimoto dissimilarities between {xs} and {ys}")
        return [1.0 - sim for sim in self.similarities(xs, ys)]

    def check_boundedness(self) -> bool:
        """
        Check if the Tanimoto similarity measure is bounded.
        
        The Tanimoto similarity is bounded between 0 and 1 inclusive.
        
        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking Tanimoto similarity boundedness")
        return self.is_bounded

    def check_reflexivity(self) -> bool:
        """
        Check if the Tanimoto similarity measure satisfies reflexivity.
        
        A measure is reflexive if s(x, x) = 1 for all x.
        
        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking Tanimoto similarity reflexivity")
        return True

    def check_symmetry(self) -> bool:
        """
        Check if the Tanimoto similarity measure is symmetric.
        
        A measure is symmetric if s(x, y) = s(y, x) for all x, y.
        
        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking Tanimoto similarity symmetry")
        return self.is_symmetric

    def check_identity(self) -> bool:
        """
        Check if the Tanimoto similarity measure satisfies identity of 
        discernibles.
        
        A measure satisfies identity if s(x, y) = 1 if and only if x = y.
        
        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug("Checking Tanimoto similarity identity of discernibles")
        return False