from typing import Union, Sequence, Tuple, Any, Optional
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "OverlapCoefficientSimilarity")
class OverlapCoefficientSimilarity(SimilarityBase):
    """
    Implementation of the Overlap Coefficient similarity measure.

    The Overlap Coefficient measures the overlap between two sets by dividing the
    size of their intersection by the size of the smaller set. It is sensitive
    to complete inclusion of one set within another.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)
            Specifies the resource type for this component
    """
    resource: Optional[str] = "similarity"

    def __init__(self):
        """
        Initializes the OverlapCoefficientSimilarity instance.
        """
        super().__init__()

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the overlap coefficient similarity between two sets.

        The overlap coefficient is defined as the size of the intersection
        of the two sets divided by the size of the smaller set.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            float:
                The overlap coefficient similarity score

        Raises:
            ValueError:
                If either set is None or not iterable
        """
        try:
            if a is None or b is None:
                logger.error("Invalid input: Both sets must be non-null")
                raise ValueError("Both sets must be non-null")

            if not isinstance(a, (set, frozenset)) or not isinstance(b, (set, frozenset)):
                logger.error("Invalid input: Inputs must be sets")
                raise ValueError("Inputs must be sets")

            intersection = a & b
            size_a = len(a)
            size_b = len(b)

            if size_a == 0 or size_b == 0:
                return 0.0

            smaller_size = min(size_a, size_b)
            overlap = len(intersection) / smaller_size

            return overlap

        except Exception as e:
            logger.error(f"Error calculating overlap coefficient: {str(e)}")
            raise

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates overlap coefficient similarity scores for one set against a list of sets.

        Args:
            a: Union[Any, None]
                The set to compare against multiple sets
            b_list: Sequence[Union[Any, None]]
                The list of sets to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of overlap coefficient similarity scores

        Raises:
            ValueError:
                If input a is None or the list contains None values
        """
        try:
            if a is None or any(b is None for b in b_list):
                logger.error("Invalid input: All sets must be non-null")
                raise ValueError("All sets must be non-null")

            return tuple(self.similarity(a, b) for b in b_list)

        except Exception as e:
            logger.error(f"Error calculating overlap coefficients: {str(e)}")
            raise

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity score based on the overlap coefficient.

        The dissimilarity is defined as 1 minus the overlap coefficient.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            float:
                The dissimilarity score
        """
        try:
            similarity = self.similarity(a, b)
            return 1.0 - similarity

        except Exception as e:
            logger.error(f"Error calculating dissimilarity: {str(e)}")
            raise

    def dissimilarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates dissimilarity scores for one set against a list of sets.

        Args:
            a: Union[Any, None]
                The set to compare against multiple sets
            b_list: Sequence[Union[Any, None]]
                The list of sets to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores
        """
        try:
            similarities = self.similarities(a, b_list)
            return tuple(1.0 - s for s in similarities)

        except Exception as e:
            logger.error(f"Error calculating dissimilarities: {str(e)}")
            raise

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        The overlap coefficient is always bounded between 0 and 1.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            bool:
            True if the measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        For the overlap coefficient, s(x, x) = 1 since the intersection
        of a set with itself is the set itself, and the smaller set size is
        the same as the set size.

        Args:
            a: Union[Any, None]
                The set to check reflexivity for

        Returns:
            bool:
            True if the measure is reflexive, False otherwise
        """
        return True

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        The overlap coefficient is symmetric since the intersection
        of a and b is the same as the intersection of b and a.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            bool:
            True if the measure is symmetric, False otherwise
        """
        return True

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        For the overlap coefficient, s(x, y) = 1 if and only if x and y are identical
        sets.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            bool:
            True if the measure satisfies identity, False otherwise
        """
        return a == b