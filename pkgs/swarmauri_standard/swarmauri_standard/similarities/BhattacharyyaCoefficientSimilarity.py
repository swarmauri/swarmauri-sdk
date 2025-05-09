import logging
import numpy as np
from typing import Union, Sequence, Literal
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "BhattacharyyaCoefficientSimilarity")
class BhattacharyyaCoefficientSimilarity(SimilarityBase):
    """
    A class to compute the Bhattacharyya Coefficient Similarity between two probability
    distributions. The Bhattacharyya coefficient measures the similarity between two 
    distributions and is particularly useful for comparing histograms or probability 
    density functions.
    
    Inherits from:
        SimilarityBase: Base class for similarity measures providing common functionality
        and interface definitions.
        
    Provides:
        Implementation of similarity calculation based on the Bhattacharyya coefficient.
        The coefficient is calculated as the sum of the square roots of the product of 
        corresponding bins in the two distributions.
    """
    type: Literal["BhattacharyyaCoefficientSimilarity"] = "BhattacharyyaCoefficientSimilarity"
    
    def __init__(self) -> None:
        """
        Initializes the BhattacharyyaCoefficientSimilarity instance.
        """
        super().__init__()
        logger.debug("BhattacharyyaCoefficientSimilarity instance initialized")

    def similarity(self, x: Union[Sequence, np.ndarray], 
                    y: Union[Sequence, np.ndarray]) -> float:
        """
        Calculates the Bhattacharyya coefficient similarity between two distributions.
        
        Args:
            x: First distribution (histogram or probability distribution vector)
            y: Second distribution (histogram or probability distribution vector)
            
        Returns:
            float: Bhattacharyya coefficient value between 0 and 1.
            
        Raises:
            ValueError: If the input distributions have different lengths
        """
        logger.debug(f"Calculating Bhattacharyya coefficient similarity between {x} and {y}")
        
        # Ensure inputs are numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)
        
        # Check if the distributions have the same length
        if len(x) != len(y):
            raise ValueError("Input distributions must have the same length")
            
        # Normalize the distributions if they are not already
        x = x / x.sum()
        y = y / y.sum()
        
        # Calculate element-wise product and square root
        product = np.sqrt(x * y)
        
        # Sum the values to get the Bhattacharyya coefficient
        coefficient = np.sum(product)
        
        return coefficient
    
    def dissimilarity(self, x: Union[Sequence, np.ndarray], 
                      y: Union[Sequence, np.ndarray]) -> float:
        """
        Calculates the Bhattacharyya dissimilarity between two distributions.
        The dissimilarity is derived from the similarity coefficient.
        
        Args:
            x: First distribution
            y: Second distribution
            
        Returns:
            float: Bhattacharyya dissimilarity value between 0 and 1.
        """
        logger.debug(f"Calculating Bhattacharyya dissimilarity between {x} and {y}")
        
        similarity = self.similarity(x, y)
        return np.sqrt(1 - similarity)
    
    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.
        
        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking boundedness of BhattacharyyaCoefficientSimilarity")
        return True
    
    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.
        
        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking reflexivity of BhattacharyyaCoefficientSimilarity")
        return True
    
    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.
        
        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking symmetry of BhattacharyyaCoefficientSimilarity")
        return True
    
    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.
        
        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug("Checking identity of discernibles for BhattacharyyaCoefficientSimilarity")
        return True