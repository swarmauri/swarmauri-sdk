import logging
import numpy as np
from typing import Union, List, Tuple, Literal, Any
from pydantic import Field

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(SimilarityBase, "BhattacharyyaCoefficient")
class BhattacharyyaCoefficient(SimilarityBase):
    """
    Bhattacharyya Coefficient for measuring the similarity between probability distributions.
    
    This coefficient measures the amount of overlap between two statistical samples or 
    probability distributions. The coefficient is a value between 0 and 1, where 1 indicates 
    complete overlap and 0 indicates no overlap.
    
    Attributes
    ----------
    type : Literal["BhattacharyyaCoefficient"]
        Type identifier for this similarity measure
    """
    
    type: Literal["BhattacharyyaCoefficient"] = "BhattacharyyaCoefficient"
    
    def __init__(self, **kwargs):
        """
        Initialize the Bhattacharyya Coefficient similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized BhattacharyyaCoefficient")
    
    def calculate(self, a: Union[List[float], np.ndarray], b: Union[List[float], np.ndarray]) -> float:
        """
        Calculate the Bhattacharyya Coefficient between two probability distributions.
        
        Parameters
        ----------
        a : Union[List[float], np.ndarray]
            First probability distribution
        b : Union[List[float], np.ndarray]
            Second probability distribution
            
        Returns
        -------
        float
            Bhattacharyya Coefficient between the two distributions
            
        Raises
        ------
        ValueError
            If input distributions have different lengths or are not normalized
        """
        # Convert inputs to numpy arrays if they aren't already
        a_array = np.array(a, dtype=float)
        b_array = np.array(b, dtype=float)
        
        # Check if distributions have the same length
        if a_array.shape != b_array.shape:
            error_msg = f"Distributions must have the same shape: {a_array.shape} != {b_array.shape}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if distributions are normalized (sum to 1)
        a_sum = np.sum(a_array)
        b_sum = np.sum(b_array)
        
        if not np.isclose(a_sum, 1.0, rtol=1e-5) or not np.isclose(b_sum, 1.0, rtol=1e-5):
            error_msg = f"Distributions must be normalized to sum to 1.0: a_sum={a_sum}, b_sum={b_sum}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Ensure non-negative values
        if np.any(a_array < 0) or np.any(b_array < 0):
            error_msg = "Distributions cannot contain negative values"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Calculate Bhattacharyya coefficient: BC(p,q) = sum(sqrt(p_i * q_i))
        # where p_i and q_i are the probabilities of the i-th bin
        try:
            # Element-wise product, then square root, then sum
            coefficient = np.sum(np.sqrt(a_array * b_array))
            
            logger.debug(f"Calculated Bhattacharyya coefficient: {coefficient}")
            return float(coefficient)
        except Exception as e:
            logger.error(f"Error calculating Bhattacharyya coefficient: {str(e)}")
            raise
    
    def is_reflexive(self) -> bool:
        """
        Check if the Bhattacharyya Coefficient is reflexive.
        
        A similarity measure is reflexive if sim(x, x) = max_similarity for all x.
        For Bhattacharyya Coefficient, sim(x, x) = 1 (the upper bound), making it reflexive.
        
        Returns
        -------
        bool
            True, as Bhattacharyya Coefficient is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Bhattacharyya Coefficient is symmetric.
        
        A similarity measure is symmetric if sim(a, b) = sim(b, a) for all a, b.
        For Bhattacharyya Coefficient, the formula is symmetric in its arguments.
        
        Returns
        -------
        bool
            True, as Bhattacharyya Coefficient is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Bhattacharyya Coefficient.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        return f"BhattacharyyaCoefficient (bounds: [0.0, 1.0])"