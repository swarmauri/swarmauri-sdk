from typing import Union, Sequence, Optional
import numpy as np
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "GaussianRBFSimilarity")
class GaussianRBFSimilarity(SimilarityBase):
    """
    Implementation of the Gaussian RBF similarity measure.
    
    This class provides a concrete implementation of the RBF (Radial Basis Function)
    kernel for similarity calculations. The similarity is computed using the 
    exponential of the negative squared Euclidean distance scaled by a gamma 
    parameter.
    
    The RBF kernel is a popular choice for measuring similarity in various 
    applications due to its ability to model non-linear relationships.
    """
    type: Literal["GaussianRBFSimilarity"] = "GaussianRBFSimilarity"
    
    def __init__(self, *, gamma: float = 1.0):
        """
        Initialize the GaussianRBFSimilarity instance.
        
        Args:
            gamma: Inverse kernel length scale. Must be greater than 0.
        """
        super().__init__()
        if gamma <= 0:
            raise ValueError("Gamma must be greater than 0")
        self.gamma = gamma
        
    def similarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Calculate the similarity between two elements using the RBF kernel.
        
        Args:
            x: First element to compare
            y: Second element to compare
            
        Returns:
            float: Similarity score between x and y
        """
        logger.debug(f"Calculating RBF similarity between {x} and {y}")
        # Convert inputs to numpy arrays if they're not already
        x = np.asarray(x)
        y = np.asarray(y)
        
        # Calculate squared Euclidean distance
        dist_sq = np.linalg.norm(x - y) ** 2
        
        # Compute the RBF kernel
        similarities = np.exp(-self.gamma * dist_sq)
        
        return similarities
        
    def dissimilarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                       y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Calculate the dissimilarity between two elements.
        
        Args:
            x: First element to compare
            y: Second element to compare
            
        Returns:
            float: Dissimilarity score between x and y
        """
        logger.debug(f"Calculating RBF dissimilarity between {x} and {y}")
        sim = self.similarity(x, y)
        return 1.0 - sim
        
    def check_boundedness(self) -> bool:
        """
        Check if the similarity measure is bounded.
        
        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking boundedness for RBF similarity")
        return True
        
    def check_reflexivity(self) -> bool:
        """
        Check if the similarity measure satisfies reflexivity.
        
        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking reflexivity for RBF similarity")
        return True
        
    def check_symmetry(self) -> bool:
        """
        Check if the similarity measure is symmetric.
        
        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking symmetry for RBF similarity")
        return True
        
    def check_identity(self) -> bool:
        """
        Check if the similarity measure satisfies identity of discernibles.
        
        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug("Checking identity of discernibles for RBF similarity")
        return False