from typing import List, Dict, Union, Any, Literal
import numpy as np
import logging
from pydantic import Field, validator

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(SimilarityBase, "HellingerAffinity")
class HellingerAffinity(SimilarityBase):
    """
    Hellinger Affinity similarity measure for probability distributions.
    
    This class implements the Hellinger Affinity, which measures the similarity
    between two probability distributions. It is based on the square root of
    the product of corresponding probabilities.
    
    The Hellinger Affinity is defined as:
    H(P, Q) = ∑(√(p_i * q_i)) for discrete distributions
    
    Attributes
    ----------
    type : Literal["HellingerAffinity"]
        The type identifier for this similarity measure
    """
    
    type: Literal["HellingerAffinity"] = "HellingerAffinity"
    
    def __init__(self, **kwargs):
        """
        Initialize the Hellinger Affinity similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized HellingerAffinity similarity measure")
    
    @validator('type')
    def validate_type(cls, v):
        """
        Validate that the type field matches the class name.
        
        Parameters
        ----------
        v : str
            The type value to validate
            
        Returns
        -------
        str
            The validated type value
            
        Raises
        ------
        ValueError
            If the type does not match "HellingerAffinity"
        """
        if v != "HellingerAffinity":
            raise ValueError(f"Type must be 'HellingerAffinity', got '{v}'")
        return v
    
    def calculate(self, a: Union[List[float], np.ndarray, Dict[Any, float]], 
                  b: Union[List[float], np.ndarray, Dict[Any, float]]) -> float:
        """
        Calculate the Hellinger Affinity between two probability distributions.
        
        Parameters
        ----------
        a : Union[List[float], np.ndarray, Dict[Any, float]]
            First probability distribution
        b : Union[List[float], np.ndarray, Dict[Any, float]]
            Second probability distribution
            
        Returns
        -------
        float
            Hellinger Affinity between distributions a and b
            
        Raises
        ------
        ValueError
            If inputs are not valid probability distributions
        TypeError
            If inputs are of unsupported types
        """
        # Convert inputs to numpy arrays for consistent processing
        a_array = self._convert_to_array(a)
        b_array = self._convert_to_array(b)
        
        # Validate probability distributions
        self._validate_distribution(a_array, "a")
        self._validate_distribution(b_array, "b")
        
        # Check if distributions have the same dimension
        if a_array.shape != b_array.shape:
            raise ValueError(f"Distributions must have the same dimensions. Got {a_array.shape} and {b_array.shape}")
        
        # Calculate Hellinger Affinity
        # H(P, Q) = ∑(√(p_i * q_i))
        try:
            # Element-wise square root of the product
            sqrt_product = np.sqrt(a_array * b_array)
            # Sum of the square roots
            affinity = np.sum(sqrt_product)
            
            logger.debug(f"Calculated Hellinger Affinity: {affinity}")
            return float(affinity)
        except Exception as e:
            logger.error(f"Error calculating Hellinger Affinity: {str(e)}")
            raise
    
    def _convert_to_array(self, dist: Union[List[float], np.ndarray, Dict[Any, float]]) -> np.ndarray:
        """
        Convert various input types to numpy array.
        
        Parameters
        ----------
        dist : Union[List[float], np.ndarray, Dict[Any, float]]
            Input distribution in various formats
            
        Returns
        -------
        np.ndarray
            Distribution as a numpy array
            
        Raises
        ------
        TypeError
            If input type is not supported
        """
        if isinstance(dist, list):
            return np.array(dist, dtype=float)
        elif isinstance(dist, np.ndarray):
            return dist.astype(float)
        elif isinstance(dist, dict):
            # Extract values from dictionary
            return np.array(list(dist.values()), dtype=float)
        else:
            raise TypeError(f"Unsupported type for probability distribution: {type(dist)}")
    
    def _validate_distribution(self, dist: np.ndarray, name: str) -> None:
        """
        Validate that the input is a valid probability distribution.
        
        Parameters
        ----------
        dist : np.ndarray
            Distribution to validate
        name : str
            Name of the distribution for error messages
            
        Raises
        ------
        ValueError
            If the distribution contains negative values or doesn't sum to 1
        """
        # Check for negative values
        if np.any(dist < 0):
            raise ValueError(f"Distribution '{name}' contains negative values")
        
        # Check if sum is approximately 1 (allowing for floating-point precision issues)
        sum_value = np.sum(dist)
        if not np.isclose(sum_value, 1.0, rtol=1e-5):
            raise ValueError(f"Distribution '{name}' must sum to 1, got {sum_value}")
    
    def is_reflexive(self) -> bool:
        """
        Check if the Hellinger Affinity measure is reflexive.
        
        Hellinger Affinity is reflexive because H(P, P) = ∑(√(p_i * p_i)) = ∑p_i = 1
        when P is a valid probability distribution.
        
        Returns
        -------
        bool
            True, as Hellinger Affinity is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Hellinger Affinity measure is symmetric.
        
        Hellinger Affinity is symmetric because H(P, Q) = ∑(√(p_i * q_i)) = ∑(√(q_i * p_i)) = H(Q, P)
        
        Returns
        -------
        bool
            True, as Hellinger Affinity is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Hellinger Affinity measure.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        return f"HellingerAffinity (bounds: [{self.lower_bound}, {self.upper_bound}])"