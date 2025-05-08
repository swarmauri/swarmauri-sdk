from typing import Set, TypeVar, Generic, Any
import logging
from typing_extensions import Literal

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@ComponentBase.register_type(SimilarityBase, "OverlapCoefficient")
class OverlapCoefficient(SimilarityBase, Generic[T]):
    """
    Overlap Coefficient similarity measure.
    
    Calculates the overlap coefficient between two sets, which is defined as
    the size of the intersection divided by the size of the smaller set.
    This measure is particularly sensitive to complete inclusion of one set
    within another.
    
    Attributes
    ----------
    type : Literal["OverlapCoefficient"]
        The type identifier for this similarity measure
    """
    
    type: Literal["OverlapCoefficient"] = "OverlapCoefficient"
    
    def __init__(self, **kwargs):
        """
        Initialize the Overlap Coefficient similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized OverlapCoefficient similarity measure")
    
    def calculate(self, a: Set[T], b: Set[T]) -> float:
        """
        Calculate the Overlap Coefficient between two sets.
        
        The Overlap Coefficient is defined as:
        |A ∩ B| / min(|A|, |B|)
        
        Parameters
        ----------
        a : Set[T]
            First set to compare
        b : Set[T]
            Second set to compare
            
        Returns
        -------
        float
            Overlap Coefficient between the two sets (0.0 to 1.0)
            
        Raises
        ------
        ValueError
            If either set is empty
        """
        # Validate input
        if not a or not b:
            logger.error("Empty set provided for Overlap Coefficient calculation")
            raise ValueError("Both sets must be non-empty for Overlap Coefficient calculation")
        
        # Calculate intersection size
        intersection_size = len(a.intersection(b))
        
        # Calculate minimum size of the two sets
        min_size = min(len(a), len(b))
        
        # Calculate and return the Overlap Coefficient
        result = intersection_size / min_size
        logger.debug(f"Calculated Overlap Coefficient: {result} between sets of size {len(a)} and {len(b)}")
        return result
    
    def is_reflexive(self) -> bool:
        """
        Check if the Overlap Coefficient is reflexive.
        
        The Overlap Coefficient is reflexive because for any non-empty set A:
        |A ∩ A| / min(|A|, |A|) = |A| / |A| = 1.0
        
        Returns
        -------
        bool
            True, as the Overlap Coefficient is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Overlap Coefficient is symmetric.
        
        The Overlap Coefficient is symmetric because:
        |A ∩ B| / min(|A|, |B|) = |B ∩ A| / min(|B|, |A|)
        
        Returns
        -------
        bool
            True, as the Overlap Coefficient is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Overlap Coefficient.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        return f"OverlapCoefficient (bounds: [{self.lower_bound}, {self.upper_bound}])"