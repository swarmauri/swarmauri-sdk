from typing import Union, Sequence, Optional, Literal
from abc import ABC
import logging
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "JaccardIndexSimilarity")
class JaccardIndexSimilarity(SimilarityBase):
    """
    Jaccard Index Similarity measure implementation.

    The Jaccard Index is a statistic used for comparing the similarity and diversity of sample sets.
    The Jaccard Index is the size of the intersection divided by the size of the union of the sample sets.

    This implementation provides methods for calculating similarity and dissimilarity between sets.

    Attributes:
        resource (str): The resource identifier for this component.
    """

    type: Literal["JaccardIndexSimilarity"] = "JaccardIndexSimilarity"
    resource: str = "JACCARD_INDEX_SIMILARITY"

    def __init__(self):
        """
        Initializes the JaccardIndexSimilarity instance.
        """
        super().__init__()

    def similarity(self, x: Union[set, Sequence], y: Union[set, Sequence]) -> float:
        """
        Calculates the Jaccard Index similarity between two sets.

        Args:
            x: First set to compare
            y: Second set to compare

        Returns:
            float: The Jaccard Index similarity score between 0 and 1

        Raises:
            ValueError: If inputs are not sets or sequences
        """
        logger.debug(f"Calculating Jaccard similarity between {x} and {y}")

        if not isinstance(x, (set, Sequence)) or not isinstance(y, (set, Sequence)):
            raise ValueError("Inputs must be sets or sequences")

        x_set = set(x) if not isinstance(x, set) else x
        y_set = set(y) if not isinstance(y, set) else y

        intersection = x_set.intersection(y_set)
        union = x_set.union(y_set)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def similarities(
        self, xs: Union[set, Sequence], ys: Union[set, Sequence]
    ) -> Sequence[float]:
        """
        Calculates Jaccard Index similarities for multiple pairs of sets.

        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare

        Returns:
            Sequence[float]: List of similarity scores for each pair

        Raises:
            ValueError: If inputs are not sets or sequences
        """
        logger.debug(f"Calculating Jaccard similarities between {xs} and {ys}")

        if not isinstance(xs, (set, Sequence)) or not isinstance(ys, (set, Sequence)):
            raise ValueError("Inputs must be sets or sequences")

        if not (isinstance(xs, Sequence) and isinstance(ys, Sequence)):
            raise ValueError("Inputs must be sequences for multiple comparisons")

        return [self.similarity(x, y) for x, y in zip(xs, ys)]

    def dissimilarity(self, x: Union[set, Sequence], y: Union[set, Sequence]) -> float:
        """
        Calculates the dissimilarity based on Jaccard Index.

        Args:
            x: First set to compare
            y: Second set to compare

        Returns:
            float: The dissimilarity score between 0 and 1
        """
        logger.debug(f"Calculating Jaccard dissimilarity between {x} and {y}")
        similarity = self.similarity(x, y)
        return 1.0 - similarity

    def dissimilarities(
        self, xs: Union[set, Sequence], ys: Union[set, Sequence]
    ) -> Sequence[float]:
        """
        Calculates Jaccard Index dissimilarities for multiple pairs of sets.

        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare

        Returns:
            Sequence[float]: List of dissimilarity scores for each pair
        """
        logger.debug(f"Calculating Jaccard dissimilarities between {xs} and {ys}")
        return [self.dissimilarity(x, y) for x, y in zip(xs, ys)]

    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking Jaccard Index boundedness")
        return True

    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking Jaccard Index reflexivity")
        return True

    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking Jaccard Index symmetry")
        return True

    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.

        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug("Checking Jaccard Index identity of discernibles")
        return True
