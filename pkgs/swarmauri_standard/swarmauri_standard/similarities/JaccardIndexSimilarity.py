from typing import Union, Sequence, Tuple, Any, Optional
import logging
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "JaccardIndexSimilarity")
class JaccardIndexSimilarity(SimilarityBase):
    """
    A concrete implementation of the SimilarityBase class for Jaccard Index Similarity.

    The Jaccard Index is a statistic used for comparing the similarity and diversity
    of set data. It is calculated as the size of the intersection divided by the
    size of the union of the sets.

    Inherits From:
        SimilarityBase: Base class for implementing similarity measures

    Attributes:
        resource: Optional[str] = ResourceTypes.SIMILARITY.value
            Specifies the resource type for this component
    """
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def similarity(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the Jaccard Index similarity between two sets.

        The Jaccard Index is calculated as the size of the intersection divided by
        the size of the union of the two sets. If both sets are None or empty,
        we treat them as empty sets and return 1.0 as they are identical.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            float:
                The Jaccard Index similarity score between the two sets

        Raises:
            ValueError:
                If either input is not a set
        """
        if a is None and b is None:
            return 1.0
        if a is None or b is None:
            return 0.0
        if not isinstance(a, set) or not isinstance(b, set):
            raise ValueError("Inputs must be sets")

        intersection = a.intersection(b)
        union = a.union(b)

        if not union:
            return 1.0

        jaccard_index = len(intersection) / len(union)
        return jaccard_index

    def similarities(
            self,
            a: Union[Any, None],
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates the Jaccard Index similarity scores between one set and a list of sets.

        Args:
            a: Union[Any, None]
                The set to compare against multiple sets
            b_list: Sequence[Union[Any, None]]
                The list of sets to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of Jaccard Index similarity scores

        Raises:
            ValueError:
                If any input is not a set
        """
        return tuple(self.similarity(a, b) for b in b_list)

    def dissimilarity(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity score between two sets using Jaccard Index.

        Dissimilarity is calculated as 1 minus the similarity score.

        Args:
            a: Union[Any, None]
                The first set to compare
            b: Union[Any, None]
                The second set to compare

        Returns:
            float:
                The dissimilarity score between the two sets
        """
        similarity_score = self.similarity(a, b)
        return 1.0 - similarity_score

    def dissimilarities(
            self,
            a: Union[Any, None],
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates the dissimilarity scores between one set and a list of sets.

        Args:
            a: Union[Any, None]
                The set to compare against multiple sets
            b_list: Sequence[Union[Any, None]]
                The list of sets to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores
        """
        return tuple(self.dissimilarity(a, b) for b in b_list)

    def check_boundedness(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Jaccard Index similarity measure is bounded.

        The Jaccard Index is bounded between 0 and 1.

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
        Checks if the Jaccard Index similarity measure is reflexive.

        The Jaccard Index is reflexive because s(x, x) = 1 for any set x.

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
        Checks if the Jaccard Index similarity measure is symmetric.

        The Jaccard Index is symmetric because s(x, y) = s(y, x) for any sets x and y.

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
        Checks if the Jaccard Index similarity measure satisfies identity.

        The Jaccard Index satisfies identity because s(x, y) = 1 if and only if x = y.

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