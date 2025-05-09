from typing import Any, Sequence, Tuple, TypeVar, Union
from collections import Counter
from swarmauri_base.ComponentBase import ComponentBase
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, bytes, Any)
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_type(SimilarityBase, "DiceSimilarity")
class DiceSimilarity(SimilarityBase):
    """
    Concrete implementation of the Dice similarity measure for sets or multisets.

    This class implements the Dice coefficient, which is a measure of similarity 
    between two sets or multisets. The coefficient is calculated as twice the 
    intersection divided by the sum of the sizes of both sets.

    The implementation supports both sets and multisets, with the similarity 
    ranging between 0 (completely dissimilar) and 1 (identical).

    Attributes:
        type: Literal["DiceSimilarity"] = "DiceSimilarity"
            The type identifier for this similarity measure.
    """
    type: Literal["DiceSimilarity"] = "DiceSimilarity"

    def __init__(self):
        """
        Initialize the DiceSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized DiceSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Dice similarity coefficient between two elements.

        The Dice coefficient is calculated as:
            similarity = 2 * |x ∩ y| / (|x| + |y|)

        Args:
            x: InputType
                The first element to compare (can be a set or multiset)
            y: InputType
                The second element to compare (can be a set or multiset)

        Returns:
            float:
                A float between 0 and 1 representing the similarity between x and y.
                Returns 1.0 if both elements are empty, and 0.0 if they have
                nothing in common.

        Raises:
            ValueError:
                If the input types are not supported
        """
        logger.debug("Calculating Dice similarity between two elements")
        
        try:
            # Convert inputs to Counter objects to handle multisets
            x_counter = Counter(x) if x else Counter()
            y_counter = Counter(y) if y else Counter()

            # Calculate the intersection
            intersection = sum((x_counter & y_counter).values())

            # Calculate total number of elements in both sets
            total = sum(x_counter.values()) + sum(y_counter.values())

            # Handle special cases
            if total == 0:
                # Both sets are empty
                return 1.0
            if intersection == 0:
                # No overlap
                return 0.0

            # Calculate Dice similarity
            similarity = (2 * intersection) / total

            logger.debug(f"Dice similarity result: {similarity}")
            return similarity

        except Exception as e:
            logger.error(f"Error calculating Dice similarity: {str(e)}")
            raise

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate Dice similarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[float]:
                A sequence of similarity scores corresponding to each pair.

        Raises:
            ValueError:
                If the input pairs are not in the correct format
        """
        logger.debug("Calculating Dice similarities for multiple pairs")
        
        try:
            results = []
            for pair in pairs:
                if len(pair) != 2:
                    raise ValueError("Each pair must contain exactly two elements")
                similarity = self.similarity(pair[0], pair[1])
                results.append(similarity)
            
            logger.debug(f"Dice similarities results: {results}")
            return results

        except Exception as e:
            logger.error(f"Error calculating Dice similarities: {str(e)}")
            raise

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Dice dissimilarity between two elements.

        Dissimilarity is calculated as 1 - similarity.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            float:
                A float between 0 and 1 representing the dissimilarity between x and y.
        """
        logger.debug("Calculating Dice dissimilarity between two elements")
        
        try:
            similarity = self.similarity(x, y)
            dissimilarity = 1.0 - similarity
            logger.debug(f"Dice dissimilarity result: {dissimilarity}")
            return dissimilarity

        except Exception as e:
            logger.error(f"Error calculating Dice dissimilarity: {str(e)}")
            raise

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate Dice dissimilarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[float]:
                A sequence of dissimilarity scores corresponding to each pair.
        """
        logger.debug("Calculating Dice dissimilarities for multiple pairs")
        
        try:
            results = []
            for pair in pairs:
                if len(pair) != 2:
                    raise ValueError("Each pair must contain exactly two elements")
                dissimilarity = self.dissimilarity(pair[0], pair[1])
                results.append(dissimilarity)
            
            logger.debug(f"Dice dissimilarities results: {results}")
            return results

        except Exception as e:
            logger.error(f"Error calculating Dice dissimilarities: {str(e)}")
            raise