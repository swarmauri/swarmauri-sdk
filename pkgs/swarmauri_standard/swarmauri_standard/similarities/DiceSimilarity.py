from typing import List, Sequence, Union, Literal, Optional, Set, Dict, Any, Counter as CounterType
from collections import Counter
import logging

from swarmauri_core.similarities.ISimilarity import ISimilarity, ComparableType
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

# Set up logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(SimilarityBase, "DiceSimilarity")
class DiceSimilarity(SimilarityBase):
    """
    Dice similarity coefficient implementation.
    
    The Dice similarity coefficient is a set-based similarity measure that
    calculates the overlap between two sets, defined as twice the size of the
    intersection divided by the sum of the sizes of the two sets.
    
    For multisets (where elements can appear multiple times), the formula
    accounts for the multiplicity of elements.
    
    Formula: 2 * |X ∩ Y| / (|X| + |Y|)
    
    Attributes
    ----------
    type : Literal["DiceSimilarity"]
        Type identifier for the similarity measure
    resource : str
        Resource type identifier
    """
    
    type: Literal["DiceSimilarity"] = "DiceSimilarity"
    resource: Optional[str] = ResourceTypes.SIMILARITY.value
    
    def __init__(self):
        """
        Initialize the Dice similarity measure.
        """
        super().__init__()
        logger.debug("Initializing DiceSimilarity")
    
    def _convert_to_counter(self, x: ComparableType) -> CounterType:
        """
        Convert the input to a Counter object for multiset operations.
        
        Parameters
        ----------
        x : ComparableType
            Input to convert to a Counter
            
        Returns
        -------
        Counter
            Counter representation of the input
            
        Raises
        ------
        TypeError
            If the input cannot be converted to a Counter
        """
        if isinstance(x, Counter):
            return x
        elif isinstance(x, (list, tuple, set)):
            return Counter(x)
        elif isinstance(x, dict):
            return Counter(x)
        elif isinstance(x, str):
            return Counter(x)
        else:
            try:
                # Try to convert to a list and then to a Counter
                return Counter(list(x))
            except Exception as e:
                logger.error(f"Cannot convert input to Counter: {str(e)}")
                raise TypeError(f"Cannot convert input of type {type(x)} to Counter") from e
    
    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Dice similarity coefficient between two objects.
        
        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare
            
        Returns
        -------
        float
            Dice similarity coefficient between x and y
            
        Raises
        ------
        ValueError
            If the objects are incomparable
        TypeError
            If the input types are not supported
        """
        try:
            # Convert inputs to Counter objects for multiset operations
            counter_x = self._convert_to_counter(x)
            counter_y = self._convert_to_counter(y)
            
            # Calculate the sum of the minimum counts for each element in both counters
            # This represents the intersection size for multisets
            intersection_size = sum((counter_x & counter_y).values())
            
            # Calculate the sum of the sizes of both sets
            sum_sizes = sum(counter_x.values()) + sum(counter_y.values())
            
            # Handle edge case where both sets are empty
            if sum_sizes == 0:
                return 1.0  # By convention, similarity of two empty sets is 1.0
            
            # Calculate Dice coefficient
            dice_coefficient = (2.0 * intersection_size) / sum_sizes
            
            return dice_coefficient
        
        except Exception as e:
            logger.error(f"Error calculating Dice similarity: {str(e)}")
            raise
    
    def similarities(self, x: ComparableType, ys: Sequence[ComparableType]) -> List[float]:
        """
        Calculate Dice similarity coefficients between one object and multiple other objects.
        
        Parameters
        ----------
        x : ComparableType
            Reference object
        ys : Sequence[ComparableType]
            Sequence of objects to compare against the reference
            
        Returns
        -------
        List[float]
            List of Dice similarity coefficients between x and each element in ys
            
        Raises
        ------
        ValueError
            If any objects are incomparable
        TypeError
            If any input types are not supported
        """
        try:
            # Convert the reference object to a Counter once
            counter_x = self._convert_to_counter(x)
            x_size = sum(counter_x.values())
            
            results = []
            for y in ys:
                counter_y = self._convert_to_counter(y)
                y_size = sum(counter_y.values())
                
                # Calculate intersection size
                intersection_size = sum((counter_x & counter_y).values())
                
                # Calculate sum of sizes
                sum_sizes = x_size + y_size
                
                # Handle edge case where both sets are empty
                if sum_sizes == 0:
                    results.append(1.0)
                else:
                    # Calculate Dice coefficient
                    dice_coefficient = (2.0 * intersection_size) / sum_sizes
                    results.append(dice_coefficient)
            
            return results
        
        except Exception as e:
            logger.error(f"Error calculating multiple Dice similarities: {str(e)}")
            raise
    
    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Dice dissimilarity between two objects.
        
        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare
            
        Returns
        -------
        float
            Dice dissimilarity between x and y
            
        Raises
        ------
        ValueError
            If the objects are incomparable
        TypeError
            If the input types are not supported
        """
        try:
            # Dice dissimilarity is 1 minus the Dice similarity
            return 1.0 - self.similarity(x, y)
        except Exception as e:
            logger.error(f"Error calculating Dice dissimilarity: {str(e)}")
            raise
    
    def check_bounded(self) -> bool:
        """
        Check if the Dice similarity measure is bounded.
        
        The Dice similarity coefficient is bounded in the range [0,1].
        
        Returns
        -------
        bool
            True, as the Dice similarity is bounded
        """
        return True
    
    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the Dice similarity measure is symmetric.
        
        The Dice similarity coefficient is symmetric: s(x,y) = s(y,x).
        
        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare
            
        Returns
        -------
        bool
            True, as the Dice similarity is symmetric
            
        Raises
        ------
        ValueError
            If the objects are incomparable
        TypeError
            If the input types are not supported
        """
        try:
            # The Dice similarity is inherently symmetric, but we'll verify
            similarity_xy = self.similarity(x, y)
            similarity_yx = self.similarity(y, x)
            return abs(similarity_xy - similarity_yx) < 1e-10
        except Exception as e:
            logger.error(f"Error checking symmetry of Dice similarity: {str(e)}")
            raise