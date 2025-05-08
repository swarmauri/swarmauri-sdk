from typing import TypeVar, Generic, List, Union, Literal
import numpy as np
import logging
from pydantic import Field, validator

from swarmauri_base.similarities.SimilarityBase import SimilarityBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@SimilarityBase.register_type(SimilarityBase, "GaussianRBF")
class GaussianRBF(SimilarityBase, Generic[T]):
    """
    Gaussian Radial Basis Function (RBF) kernel similarity.
    
    Calculates similarity between vectors using an exponential function that
    decays with the squared Euclidean distance between the vectors.
    
    The formula is: K(x, y) = exp(-gamma * ||x - y||^2)
    
    Attributes
    ----------
    type : Literal["GaussianRBF"]
        Type identifier for the component
    gamma : float
        Parameter controlling the width of the Gaussian kernel.
        Larger values result in a narrower peak.
    """
    
    type: Literal["GaussianRBF"] = "GaussianRBF"
    gamma: float = Field(gt=0, description="Gamma parameter (inverse of RBF width)")
    
    @validator('gamma')
    def check_gamma_positive(cls, v):
        """Validate that gamma is positive."""
        if v <= 0:
            raise ValueError("Gamma must be positive")
        return v
    
    def __init__(self, gamma: float = 1.0, **kwargs):
        """
        Initialize the Gaussian RBF similarity measure.
        
        Parameters
        ----------
        gamma : float, optional
            The gamma parameter controlling the width of the Gaussian kernel, by default 1.0.
            Must be positive. Larger values result in a narrower peak.
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        self.gamma = gamma
        logger.debug(f"Initialized {self.__class__.__name__} with gamma={gamma}")
    
    def calculate(self, a: Union[List[float], np.ndarray], b: Union[List[float], np.ndarray]) -> float:
        """
        Calculate the Gaussian RBF similarity between two vectors.
        
        Similarity is computed as exp(-gamma * ||a - b||^2) where ||a - b||^2 is
        the squared Euclidean distance between vectors a and b.
        
        Parameters
        ----------
        a : Union[List[float], np.ndarray]
            First vector
        b : Union[List[float], np.ndarray]
            Second vector
            
        Returns
        -------
        float
            Similarity score between vectors (range: 0 to 1)
            
        Raises
        ------
        ValueError
            If the input vectors have different dimensions
        """
        # Convert inputs to numpy arrays if they aren't already
        a_array = np.array(a, dtype=float)
        b_array = np.array(b, dtype=float)
        
        # Check dimensions
        if a_array.shape != b_array.shape:
            logger.error(f"Input vectors have different shapes: {a_array.shape} vs {b_array.shape}")
            raise ValueError(f"Input vectors must have the same dimensions: {a_array.shape} != {b_array.shape}")
        
        # Calculate squared Euclidean distance
        squared_distance = np.sum((a_array - b_array) ** 2)
        
        # Apply RBF kernel formula
        similarity = np.exp(-self.gamma * squared_distance)
        
        logger.debug(f"Calculated similarity: {similarity} (gamma={self.gamma}, squared_distance={squared_distance})")
        return float(similarity)
    
    def is_reflexive(self) -> bool:
        """
        Check if the similarity measure is reflexive.
        
        For Gaussian RBF, sim(x, x) = exp(-gamma * 0) = 1, which is the maximum similarity.
        Therefore, it is reflexive.
        
        Returns
        -------
        bool
            True since Gaussian RBF is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the similarity measure is symmetric.
        
        For Gaussian RBF, sim(a, b) = exp(-gamma * ||a - b||^2) = exp(-gamma * ||b - a||^2) = sim(b, a).
        Therefore, it is symmetric.
        
        Returns
        -------
        bool
            True since Gaussian RBF is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Gaussian RBF similarity measure.
        
        Returns
        -------
        str
            String representation including gamma and bounds information
        """
        bounds_str = f"[{self.lower_bound}, {self.upper_bound}]" if self.is_bounded else "unbounded"
        return f"{self.__class__.__name__} (gamma={self.gamma}, bounds: {bounds_str})"