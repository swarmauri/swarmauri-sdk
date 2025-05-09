from typing import Set, Sequence, Tuple, TypeVar
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar("InputType", Set, frozenset)
OutputType = TypeVar("OutputType", float)


@ComponentBase.register_type(SimilarityBase, "JaccardIndexSimilarity")
class JaccardIndexSimilarity(SimilarityBase):
    """
    Concrete implementation of the Jaccard Index Similarity measure for sets.

    The Jaccard Index is a statistic used for comparing the similarity and diversity
    of set data. It is defined as the size of the intersection divided by the size
    of the union of the two sets.

    This implementation provides methods for calculating similarity and dissimilarity
    between pairs of sets or multiple pairs of sets.

    Attributes:
        type: Literal["JaccardIndexSimilarity"]
            Type identifier for the similarity measure
    """

    type: Literal["JaccardIndexSimilarity"] = "JaccardIndexSimilarity"

    def __init__(self):
        """
        Initialize the JaccardIndexSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized JaccardIndexSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> OutputType:
        """
        Calculate the Jaccard Index similarity between two sets.

        The Jaccard Index is calculated as:
            J(x, y) = |x ∩ y| / |x ∪ y|

        Args:
            x: InputType
                The first set to compare
            y: InputType
                The second set to compare

        Returns:
            OutputType:
                A float between 0 and 1 representing the similarity.
                0 indicates no similarity, 1 indicates identical sets.

        Raises:
            ValueError: If inputs are not valid sets
        """
        if not isinstance(x, (Set, frozenset)) or not isinstance(y, (Set, frozenset)):
            raise ValueError("Inputs must be sets or frozensets")

        intersection = x & y
        union = x | y

        if not union:
            # Both sets are empty
            return 1.0

        jaccard_index = len(intersection) / len(union)
        logger.debug(f"Similarity between {x} and {y}: {jaccard_index}")
        return jaccard_index

    def similarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[OutputType]:
        """
        Calculate Jaccard Index similarities for multiple pairs of sets.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of set pairs to compare

        Returns:
            Sequence[OutputType]:
                A sequence of similarity scores corresponding to each pair
        """
        return [self.similarity(x, y) for x, y in pairs]

    def dissimilarity(self, x: InputType, y: InputType) -> OutputType:
        """
        Calculate the dissimilarity between two sets using Jaccard Index.

        Dissimilarity is calculated as 1 - similarity.

        Args:
            x: InputType
                The first set to compare
            y: InputType
                The second set to compare

        Returns:
            OutputType:
                A float between 0 and 1 representing the dissimilarity.
                0 indicates identical sets, 1 indicates no similarity.
        """
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[OutputType]:
        """
        Calculate dissimilarities for multiple pairs of sets.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of set pairs to compare

        Returns:
            Sequence[OutputType]:
                A sequence of dissimilarity scores corresponding to each pair
        """
        return [1.0 - sim for sim in self.similarities(pairs)]
