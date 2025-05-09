from typing import Union, Sequence, Optional, Literal
from abc import ABC
import logging
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "OverlapCoefficientSimilarity")
class OverlapCoefficientSimilarity(SimilarityBase):
    """
    Implementation of the Overlap Coefficient similarity measure.

    The Overlap Coefficient is defined as the ratio of the intersection size to
    the size of the smaller of the two sets. It is sensitive to cases where one set
    is completely included in the other.

    Inherits from SimilarityBase and implements all required methods for
    similarity calculation.
    """

    type: Literal["OverlapCoefficientSimilarity"] = "OverlapCoefficientSimilarity"
    resource: Optional[str] = "SIMILARITY.OVERLAP"

    def similarity(self, x: Union[Sequence, str], y: Union[Sequence, str]) -> float:
        """
        Calculate the similarity between two elements using the Overlap Coefficient.

        The Overlap Coefficient is calculated as:
            |x ∩ y| / min(|x|, |y|)

        Args:
            x: First element to compare (sequence or string)
            y: Second element to compare (sequence or string)

        Returns:
            float: Similarity score between 0 and 1

        Raises:
            ValueError: If either x or y is empty
        """
        logger.debug(f"Calculating overlap coefficient similarity between {x} and {y}")

        # Convert elements to sets
        set_x = set(x)
        set_y = set(y)

        # Calculate intersection
        intersection = set_x & set_y
        overlap = len(intersection)

        # Get sizes of sets
        size_x = len(set_x)
        size_y = len(set_y)

        # Determine the size of the smaller set
        smaller_size = min(size_x, size_y)

        if smaller_size == 0:
            raise ValueError("Both sets must be non-empty")

        # Calculate and return the coefficient
        coefficient = overlap / smaller_size
        return coefficient

    def similarities(
        self, xs: Union[Sequence, str], ys: Union[Sequence, str]
    ) -> Sequence[float]:
        """
        Calculate similarities for multiple pairs of elements.

        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare

        Returns:
            Sequence[float]: List of similarity scores
        """
        logger.debug(
            f"Calculating overlap coefficient similarities for {len(xs)} pairs"
        )
        return [self.similarity(x, y) for x, y in zip(xs, ys)]

    def dissimilarity(self, x: Union[Sequence, str], y: Union[Sequence, str]) -> float:
        """
        Calculate the dissimilarity between two elements.

        Dissimilarity is 1 minus the similarity score.

        Args:
            x: First element to compare
            y: Second element to compare

        Returns:
            float: Dissimilarity score between 0 and 1
        """
        logger.debug(
            f"Calculating overlap coefficient dissimilarity between {x} and {y}"
        )
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self, xs: Union[Sequence, str], ys: Union[Sequence, str]
    ) -> Sequence[float]:
        """
        Calculate dissimilarities for multiple pairs of elements.

        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare

        Returns:
            Sequence[float]: List of dissimilarity scores
        """
        logger.debug(
            f"Calculating overlap coefficient dissimilarities for {len(xs)} pairs"
        )
        return [self.dissimilarity(x, y) for x, y in zip(xs, ys)]

    def check_boundedness(self) -> bool:
        """
        Check if the similarity measure is bounded.

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking boundedness of overlap coefficient similarity")
        return True  # Overlap Coefficient scores are bounded between 0 and 1

    def check_reflexivity(self) -> bool:
        """
        Check if the similarity measure satisfies reflexivity.

        A measure is reflexive if s(x, x) = 1 for all x.

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking reflexivity of overlap coefficient similarity")
        return True  # s(x, x) = 1 since |x ∩ x| / |x| = 1

    def check_symmetry(self) -> bool:
        """
        Check if the similarity measure is symmetric.

        A measure is symmetric if s(x, y) = s(y, x) for all x, y.

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking symmetry of overlap coefficient similarity")
        return True  # Overlap Coefficient is symmetric as |x ∩ y| / min(|x|, |y|) is the same for x and y

    def check_identity(self) -> bool:
        """
        Check if the similarity measure satisfies identity of discernibles.

        A measure satisfies identity if s(x, y) = 1 if and only if x = y.

        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug(
            "Checking identity of discernibles for overlap coefficient similarity"
        )
        return False  # Different sets can have full overlap without being identical
