from typing import Set, Dict, TypeVar, List, Any, Collection, Union
import logging
from collections import Counter
from typing import Literal

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@ComponentBase.register_type(SimilarityBase, "Dice")
class Dice(SimilarityBase):
    """
    Dice similarity coefficient implementation.
    
    Calculates similarity based on the weighted overlap between two sets or multisets.
    The Dice coefficient is defined as twice the size of the intersection divided by
    the sum of the sizes of the two sets.
    
    For multisets, the coefficient takes into account element multiplicities.
    
    Attributes
    ----------
    type : Literal["Dice"]
        Type identifier for the similarity measure
    """
    
    type: Literal["Dice"] = "Dice"
    
    def __init__(self, **kwargs):
        """
        Initialize the Dice similarity measure.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(is_bounded=True, lower_bound=0.0, upper_bound=1.0, **kwargs)
        logger.debug("Initialized Dice similarity measure")
    
    def calculate(self, a: Union[Set[T], List[T], Dict[T, int], Counter], 
                  b: Union[Set[T], List[T], Dict[T, int], Counter]) -> float:
        """
        Calculate Dice similarity coefficient between two collections.
        
        The Dice coefficient is calculated as:
        dice(A, B) = 2 * |A ∩ B| / (|A| + |B|)
        
        For multisets (represented as Counter objects or dictionaries with counts),
        the intersection and sizes account for multiplicities.
        
        Parameters
        ----------
        a : Union[Set[T], List[T], Dict[T, int], Counter]
            First collection to compare
        b : Union[Set[T], List[T], Dict[T, int], Counter]
            Second collection to compare
            
        Returns
        -------
        float
            Dice similarity coefficient between the collections
            
        Examples
        --------
        >>> dice = Dice()
        >>> dice.calculate({"a", "b", "c"}, {"a", "c", "d"})
        0.5
        >>> dice.calculate(Counter(["a", "a", "b"]), Counter(["a", "b", "b"]))
        0.6666666666666666
        """
        # Convert inputs to Counter objects to handle multisets
        if isinstance(a, (list, set)):
            a_counter = Counter(a)
        elif isinstance(a, dict):
            a_counter = Counter(a)
        else:
            a_counter = a
            
        if isinstance(b, (list, set)):
            b_counter = Counter(b)
        elif isinstance(b, dict):
            b_counter = Counter(b)
        else:
            b_counter = b
            
        # Calculate intersection size (with multiplicities)
        intersection_size = sum((a_counter & b_counter).values())
        
        # Calculate sizes (with multiplicities)
        size_a = sum(a_counter.values())
        size_b = sum(b_counter.values())
        
        # Handle edge case of empty collections
        if size_a + size_b == 0:
            logger.warning("Both collections are empty, returning maximum similarity (1.0)")
            return 1.0
            
        # Calculate Dice coefficient
        dice_coefficient = 2 * intersection_size / (size_a + size_b)
        
        logger.debug(f"Calculated Dice coefficient: {dice_coefficient} between collections of sizes {size_a} and {size_b}")
        return dice_coefficient
    
    def is_reflexive(self) -> bool:
        """
        Check if the Dice similarity measure is reflexive.
        
        The Dice coefficient is reflexive as dice(A, A) = 2|A|/2|A| = 1.0,
        which is the maximum similarity value.
        
        Returns
        -------
        bool
            True, as Dice similarity is reflexive
        """
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the Dice similarity measure is symmetric.
        
        The Dice coefficient is symmetric as dice(A, B) = dice(B, A) for all A, B.
        
        Returns
        -------
        bool
            True, as Dice similarity is symmetric
        """
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the Dice similarity measure.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        return f"Dice Similarity (bounds: [{self.lower_bound}, {self.upper_bound}])"