from typing import Set, TypeVar, Generic, Any
import logging
from pydantic import Field
from typing_extensions import Literal

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@ComponentBase.register_type(SimilarityBase, "JaccardIndex")
class JaccardIndex(SimilarityBase, Generic[T]):
    """
    Jaccard Index similarity measure.
    
    Calculates similarity based on the size of the intersection divided by the size of the union
    of two sets. Useful for binary attributes or comparing sets.
    
    The Jaccard Index is defined as:
    J(A, B) = |A ∩ B| / |A ∪ B|
    
    This implementation is bounded in the range [0, 1], where:
    - 0 indicates no similarity (disjoint sets)
    - 1 indicates identical sets
    
    Attributes
    ----------
    type : Literal["JaccardIndex"]
        The type identifier for this similarity measure
    """
    
    type: Literal["JaccardIndex"] = "JaccardIndex"
    
    def __init__(self, **kwargs):
        """
        Initialize the Jaccard Index similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        # Jaccard Index is bounded between 0 and 1
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized JaccardIndex similarity measure")
    
    def calculate(self, a: Set[T], b: Set[T]) -> float:
        """
        Calculate the Jaccard Index similarity between two sets.
        
        Parameters
        ----------
        a : Set[T]
            First set
        b : Set[T]
            Second set
            
        Returns
        -------
        float
            Jaccard Index similarity score between the sets
            
        Raises
        ------
        TypeError
            If inputs are not sets
        """
        # Validate that inputs are sets
        if not isinstance(a, set) or not isinstance(b, set):
            logger.error(f"JaccardIndex requires set inputs, got {type(a)} and {type(b)}")
            raise TypeError(f"JaccardIndex requires set inputs, got {type(a)} and {type(b)}")
        
        # Handle edge case where both sets are empty
        if len(a) == 0 and len(b) == 0:
            logger.debug("Both sets are empty, returning maximum similarity (1.0)")
            return 1.0
        
        # Calculate intersection and union
        intersection = a.intersection(b)
        union = a.union(b)
        
        # Calculate Jaccard Index
        similarity = len(intersection) / len(union)
        logger.debug(f"Calculated Jaccard similarity: {similarity}")
        
        return similarity
    
    def is_reflexive(self) -> bool:
        """
        Check if the Jaccard Index is reflexive.
        
        The Jaccard Index is reflexive because for any set A:
        J(A, A) = |A ∩ A| / |A ∪ A| = |A| / |A| = 1 (maximum similarity)
        
        Returns
        -------
        bool
            True, as the Jaccard Index is reflexive
        """
        logger.debug("JaccardIndex is reflexive")
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Jaccard Index is symmetric.
        
        The Jaccard Index is symmetric because for any sets A and B:
        J(A, B) = |A ∩ B| / |A ∪ B| = |B ∩ A| / |B ∪ A| = J(B, A)
        
        Returns
        -------
        bool
            True, as the Jaccard Index is symmetric
        """
        logger.debug("JaccardIndex is symmetric")
        return True