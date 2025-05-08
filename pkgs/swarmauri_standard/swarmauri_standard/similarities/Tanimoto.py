import logging
import numpy as np
from typing import List, Union, Literal
from pydantic import Field, validator

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

VectorType = Union[List[float], np.ndarray]

@ComponentBase.register_type(SimilarityBase, "Tanimoto")
class Tanimoto(SimilarityBase):
    """
    Tanimoto similarity measure for real-valued vectors.
    
    Tanimoto coefficient is a generalization of Jaccard similarity for real-valued vectors,
    commonly used in cheminformatics for comparing chemical fingerprints.
    
    The formula is:
        T(A, B) = (A·B) / (|A|^2 + |B|^2 - A·B)
    
    Where A·B is the dot product and |X|^2 is the sum of squares of elements in X.
    
    Attributes
    ----------
    type : Literal["Tanimoto"]
        Type identifier for the similarity measure
    """
    
    type: Literal["Tanimoto"] = "Tanimoto"
    
    @validator('type')
    def validate_type(cls, v):
        """
        Validate that the type is "Tanimoto".
        
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
            If the type is not "Tanimoto"
        """
        if v != "Tanimoto":
            raise ValueError(f"Type must be 'Tanimoto', got '{v}'")
        return v
    
    def __init__(self, **kwargs):
        """
        Initialize the Tanimoto similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        # Tanimoto coefficient is bounded between 0 and 1
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized Tanimoto similarity measure")
    
    def calculate(self, a: VectorType, b: VectorType) -> float:
        """
        Calculate the Tanimoto similarity between two vectors.
        
        Parameters
        ----------
        a : VectorType
            First vector
        b : VectorType
            Second vector
            
        Returns
        -------
        float
            Tanimoto similarity score between vectors
            
        Raises
        ------
        ValueError
            If either vector is zero (all elements are zero)
        """
        # Convert inputs to numpy arrays if they aren't already
        a_array = np.array(a, dtype=float)
        b_array = np.array(b, dtype=float)
        
        # Check if vectors are non-zero (requirement for Tanimoto)
        if np.all(a_array == 0) or np.all(b_array == 0):
            logger.error("Cannot compute Tanimoto similarity with zero vectors")
            raise ValueError("Tanimoto similarity is undefined for zero vectors")
        
        # Calculate dot product
        dot_product = np.dot(a_array, b_array)
        
        # Calculate sum of squares
        a_sum_squares = np.sum(a_array * a_array)
        b_sum_squares = np.sum(b_array * b_array)
        
        # Calculate Tanimoto coefficient
        denominator = a_sum_squares + b_sum_squares - dot_product
        
        # Avoid division by zero (though this shouldn't happen with non-zero vectors)
        if denominator == 0:
            logger.warning("Denominator is zero in Tanimoto calculation, returning 0")
            return 0.0
        
        similarity = dot_product / denominator
        
        logger.debug(f"Calculated Tanimoto similarity: {similarity}")
        return similarity
    
    def is_reflexive(self) -> bool:
        """
        Check if the Tanimoto similarity measure is reflexive.
        
        Tanimoto similarity is reflexive as sim(x, x) = 1 (maximum similarity) for all x.
        
        Returns
        -------
        bool
            True, as Tanimoto similarity is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Tanimoto similarity measure is symmetric.
        
        Tanimoto similarity is symmetric as sim(a, b) = sim(b, a) for all a, b.
        
        Returns
        -------
        bool
            True, as Tanimoto similarity is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Tanimoto similarity measure.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        return f"Tanimoto (bounds: [{self.lower_bound}, {self.upper_bound}])"