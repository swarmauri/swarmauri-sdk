from typing import Any, Sequence, Tuple, TypeVar, Union, Set
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar("InputType", str, bytes, Any)
OutputType = TypeVar("OutputType", float)


@ComponentBase.register_type(SimilarityBase, "OverlapCoefficientSimilarity")
class OverlapCoefficientSimilarity(SimilarityBase):
    """
    Concrete implementation of the SimilarityBase class for calculating the overlap coefficient similarity.

    The overlap coefficient measures the overlap between two sets by dividing the size of their intersection
    by the size of the smaller set. This implementation handles various input types and ensures proper bounds checking.

    Attributes:
        type: Literal["OverlapCoefficientSimilarity"]
            Type identifier for the similarity measure
    """

    type: Literal["OverlapCoefficientSimilarity"] = "OverlapCoefficientSimilarity"
    resource: str = ResourceTypes.SIMILARITY.value

    def __init__(self):
        """
        Initialize the OverlapCoefficientSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized OverlapCoefficientSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the overlap coefficient similarity between two sets.

        The overlap coefficient is defined as the ratio of the size of the intersection
        of the two sets to the size of the smaller set.

        Args:
            x: InputType
                The first set to compare
            y: InputType
                The second set to compare

        Returns:
            float:
                The overlap coefficient similarity between x and y, ranging between 0 and 1.

        Raises:
            ValueError:
                If either input is not a finite, non-empty set
        """
        if not isinstance(x, Set) or not isinstance(y, Set):
            logger.error("Inputs must be sets")
            raise ValueError("Inputs must be sets")

        if not x or not y:
            logger.error("Inputs must be non-empty sets")
            raise ValueError("Inputs must be non-empty sets")

        intersection = x & y
        smaller_set_size = min(len(x), len(y))

        if smaller_set_size == 0:
            logger.warning("Both sets are empty - returning 0.0")
            return 0.0

        overlap = len(intersection) / smaller_set_size
        logger.debug(f"Calculated overlap coefficient similarity: {overlap}")
        return overlap

    def similarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[float]:
        """
        Calculate overlap coefficient similarities for multiple pairs of sets.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of set pairs to compare

        Returns:
            Sequence[float]:
                A sequence of overlap coefficient similarities corresponding to each pair
        """
        logger.debug("Calculating similarities for multiple pairs")
        return [self.similarity(x, y) for x, y in pairs]

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the dissimilarity based on the overlap coefficient.

        The dissimilarity is defined as 1 minus the similarity value.

        Args:
            x: InputType
                The first set to compare
            y: InputType
                The second set to compare

        Returns:
            float:
                The dissimilarity between x and y, ranging between 0 and 1.
        """
        similarity = self.similarity(x, y)
        dissimilarity = 1.0 - similarity
        logger.debug(f"Calculated dissimilarity: {dissimilarity}")
        return dissimilarity

    def dissimilarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[float]:
        """
        Calculate dissimilarities for multiple pairs of sets.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of set pairs to compare

        Returns:
            Sequence[float]:
                A sequence of dissimilarity scores corresponding to each pair
        """
        logger.debug("Calculating dissimilarities for multiple pairs")
        return [self.dissimilarity(x, y) for x, y in pairs]
