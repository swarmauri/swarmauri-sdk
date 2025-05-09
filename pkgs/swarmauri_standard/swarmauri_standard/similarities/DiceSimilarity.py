from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.similarities.SimilarityBase import SimilarityBase
from typing import Union, Sequence, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class DiceSimilarity(SimilarityBase):
    """
    Provides the implementation for Dice similarity measure.
    
    The Dice similarity is an overlap-based set similarity measure that
    weighs the shared elements between two sets. It is particularly useful
    for comparing sets or multisets where the order of elements does not matter.
    
    The measure is computed as:
        Dice(x, y) = 2 * |x ∩ y| / (|x| + |y|)
    
    This implementation supports both sets and multisets, handling each case
    appropriately by considering element counts in multisets.
    """
    resource: Optional[str] = "DiceSimilarity"

    def similarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the Dice similarity between two sets or multisets.
        
        Args:
            x: The first set or multiset (as an iterable).
            y: The second set or multiset (as an iterable).
            
        Returns:
            float: The Dice similarity coefficient between x and y.
        """
        logger.debug(f"Calculating Dice similarity between {x} and {y}")

        # Convert inputs to Counters to handle both sets and multisets
        x_counter = Counter(x)
        y_counter = Counter(y)

        # Calculate the size of the intersection
        intersection = sum((x_counter & y_counter).values())
        
        # Calculate the total sizes of both sets/multisets
        size_x = sum(x_counter.values())
        size_y = sum(y_counter.values())
        
        # Handle the special case where both sets are empty
        if size_x == 0 and size_y == 0:
            return 1.0
            
        # Compute and return the Dice similarity
        return (2 * intersection) / (size_x + size_y)

    def similarities(self, xs: Union[IVector, IMatrix, Sequence, str, Callable], 
                     ys: Union[IVector, IMatrix, Sequence, str, Callable]) -> Union[float, Sequence[float]]:
        """
        Computes Dice similarities for multiple pairs of elements.
        
        Args:
            xs: First set or sequence of sets/multisets.
            ys: Second set or sequence of sets/multisets.
            
        Returns:
            Union[float, Sequence[float]]: Dice similarities for each pair.
        """
        logger.debug(f"Calculating Dice similarities between {xs} and {ys}")
        
        if isinstance(xs, Sequence) and isinstance(ys, Sequence):
            return [self.similarity(x, y) for x, y in zip(xs, ys)]
        else:
            return self.similarity(xs, ys)

    def dissimilarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                      y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the dissimilarity as 1 minus the similarity.
        
        Args:
            x: First element to compare.
            y: Second element to compare.
            
        Returns:
            float: Dissimilarity between x and y.
        """
        logger.debug(f"Calculating dissimilarity between {x} and {y}")
        return 1.0 - self.similarity(x, y)

    def dissimilarities(self, xs: Union[IVector, IMatrix, Sequence, str, Callable], 
                       ys: Union[IVector, IMatrix, Sequence, str, Callable]) -> Union[float, Sequence[float]]:
        """
        Computes dissimilarities for multiple pairs of elements.
        
        Args:
            xs: First set or sequence of elements.
            ys: Second set or sequence of elements.
            
        Returns:
            Union[float, Sequence[float]]: Dissimilarities for each pair.
        """
        logger.debug(f"Calculating dissimilarities between {xs} and {ys}")
        
        if isinstance(xs, Sequence) and isinstance(ys, Sequence):
            return [1.0 - s for s in self.similarities(xs, ys)]
        else:
            return 1.0 - self.similarity(xs, ys)

    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.
        
        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        logger.debug("Checking boundedness for DiceSimilarity")
        return True

    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.
        
        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        logger.debug("Checking reflexivity for DiceSimilarity")
        return True

    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.
        
        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        logger.debug("Checking symmetry for DiceSimilarity")
        return True