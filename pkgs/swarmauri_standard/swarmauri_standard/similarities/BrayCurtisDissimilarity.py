from typing import List, TypeVar, Union, Literal, Any
import logging
import numpy as np
from pydantic import Field, validator

from swarmauri_standard.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')
VectorType = Union[List[float], np.ndarray]

@ComponentBase.register_type(SimilarityBase, "BrayCurtisDissimilarity")
class BrayCurtisDissimilarity(SimilarityBase):
    """
    Bray-Curtis dissimilarity measure.
    
    A measure commonly used in ecology to quantify the compositional dissimilarity
    between two samples. It ranges from 0 (identical) to 1 (completely different).
    
    Attributes
    ----------
    type : Literal["BrayCurtisDissimilarity"]
        Type identifier for this similarity measure
    """
    
    type: Literal["BrayCurtisDissimilarity"] = "BrayCurtisDissimilarity"
    
    def __init__(self, **kwargs):
        """
        Initialize the Bray-Curtis dissimilarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized BrayCurtisDissimilarity")
    
    @validator('type')
    def validate_type(cls, v):
        """
        Validate that the type is correctly set.
        
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
            If the type is not "BrayCurtisDissimilarity"
        """
        if v != "BrayCurtisDissimilarity":
            raise ValueError(f"Type must be 'BrayCurtisDissimilarity', got '{v}'")
        return v
    
    def calculate(self, a: VectorType, b: VectorType) -> float:
        """
        Calculate the Bray-Curtis dissimilarity between two vectors.
        
        The Bray-Curtis dissimilarity is defined as:
        BC = sum(|a_i - b_i|) / sum(a_i + b_i)
        
        Parameters
        ----------
        a : VectorType
            First vector (must be non-negative)
        b : VectorType
            Second vector (must be non-negative)
            
        Returns
        -------
        float
            Bray-Curtis dissimilarity score between vectors
            
        Raises
        ------
        ValueError
            If vectors have different lengths or contain negative values
        """
        # Convert inputs to numpy arrays for efficient computation
        a_array = np.asarray(a, dtype=float)
        b_array = np.asarray(b, dtype=float)
        
        # Check if inputs have the same length
        if a_array.shape != b_array.shape:
            logger.error(f"Input vectors must have the same shape: {a_array.shape} != {b_array.shape}")
            raise ValueError(f"Input vectors must have the same shape: {a_array.shape} != {b_array.shape}")
        
        # Check if inputs are non-negative
        if np.any(a_array < 0) or np.any(b_array < 0):
            logger.error("Input vectors must be non-negative")
            raise ValueError("Input vectors must be non-negative")
        
        # Calculate the numerator (sum of absolute differences)
        numerator = np.sum(np.abs(a_array - b_array))
        
        # Calculate the denominator (sum of all values)
        denominator = np.sum(a_array + b_array)
        
        # Handle the case where denominator is zero
        if denominator == 0:
            logger.warning("Both vectors are zero vectors, returning 0.0")
            return 0.0
        
        # Calculate and return the Bray-Curtis dissimilarity
        dissimilarity = numerator / denominator
        logger.debug(f"Calculated Bray-Curtis dissimilarity: {dissimilarity}")
        return dissimilarity
    
    def is_reflexive(self) -> bool:
        """
        Check if the Bray-Curtis dissimilarity measure is reflexive.
        
        A dissimilarity measure is reflexive if d(x, x) = 0 for all x.
        Bray-Curtis dissimilarity is reflexive.
        
        Returns
        -------
        bool
            True, as Bray-Curtis dissimilarity is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Bray-Curtis dissimilarity measure is symmetric.
        
        A dissimilarity measure is symmetric if d(a, b) = d(b, a) for all a, b.
        Bray-Curtis dissimilarity is symmetric.
        
        Returns
        -------
        bool
            True, as Bray-Curtis dissimilarity is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Bray-Curtis dissimilarity measure.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        return f"BrayCurtisDissimilarity (bounds: [0.0, 1.0])"