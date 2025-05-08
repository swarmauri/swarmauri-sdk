import logging
import numpy as np
from typing import Any, List, Union, TypeVar, Literal
from pydantic import Field

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Union[List[float], np.ndarray])

@ComponentBase.register_type(SimilarityBase, "CosineSimilarity")
class CosineSimilarity(SimilarityBase):
    """
    Cosine similarity implementation for comparing the direction between vectors.
    
    Calculates similarity as the dot product of vectors divided by the product
    of their norms. This measures the cosine of the angle between two vectors,
    with 1 indicating identical direction and 0 indicating orthogonality.
    
    Attributes
    ----------
    type : Literal["CosineSimilarity"]
        Type identifier for the component
    """
    
    type: Literal["CosineSimilarity"] = "CosineSimilarity"
    
    def __init__(self, **kwargs):
        """
        Initialize CosineSimilarity with bounded similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized CosineSimilarity")
    
    def calculate(self, a: T, b: T) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Parameters
        ----------
        a : T
            First vector
        b : T
            Second vector
            
        Returns
        -------
        float
            Cosine similarity in range [0, 1]
            
        Raises
        ------
        ValueError
            If either vector has zero magnitude
        """
        # Convert inputs to numpy arrays if they aren't already
        a_array = np.array(a, dtype=float)
        b_array = np.array(b, dtype=float)
        
        # Calculate vector norms
        norm_a = np.linalg.norm(a_array)
        norm_b = np.linalg.norm(b_array)
        
        # Check for zero vectors
        if norm_a == 0 or norm_b == 0:
            logger.error("Cannot compute cosine similarity with zero-length vector")
            raise ValueError("Cosine similarity is undefined for zero-length vectors")
        
        # Calculate dot product
        dot_product = np.dot(a_array, b_array)
        
        # Calculate cosine similarity
        similarity = dot_product / (norm_a * norm_b)
        
        # Handle potential numerical issues (values slightly outside [-1,1] due to floating point)
        if similarity > 1.0:
            similarity = 1.0
        elif similarity < 0.0:
            similarity = 0.0
            
        logger.debug(f"Calculated cosine similarity: {similarity}")
        return float(similarity)
    
    def is_reflexive(self) -> bool:
        """
        Check if cosine similarity is reflexive.
        
        A similarity measure is reflexive if sim(x, x) = max_similarity for all x.
        Cosine similarity is reflexive as the cosine of the angle between
        identical vectors is 1, which is the maximum similarity value.
        
        Returns
        -------
        bool
            True, as cosine similarity is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if cosine similarity is symmetric.
        
        A similarity measure is symmetric if sim(a, b) = sim(b, a) for all a, b.
        Cosine similarity is symmetric as the dot product and vector norms
        are independent of the order of vectors.
        
        Returns
        -------
        bool
            True, as cosine similarity is symmetric
        """
        return True