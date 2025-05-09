from typing import Union, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "JaccardIndexSimilarity")
class JaccardIndexSimilarity(SimilarityBase):
    """
    Concrete implementation of the SimilarityBase class for Jaccard Index Similarity.

    The Jaccard Index is a statistic used for comparing the similarity and diversity of set data.
    It is calculated as the size of the intersection divided by the size of the union of two sets.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def __init__(self) -> None:
        """
        Initializes the JaccardIndexSimilarity component.
        """
        super().__init__()

    def similarity(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        y: Union[Tuple, frozenset, set, List]
    ) -> float:
        """
        Computes the Jaccard Index similarity between two sets.

        The Jaccard Index is calculated as the size of the intersection of x and y 
        divided by the size of the union of x and y.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            float: Jaccard Index similarity between x and y.

        Raises:
            ValueError: If either x or y is not a set-like collection.
        """
        if not isinstance(x, (set, frozenset, tuple, list)) or \
           not isinstance(y, (set, frozenset, tuple, list)):
            raise ValueError("Inputs must be set-like collections.")

        x_set = set(x) if not isinstance(x, (set, frozenset)) else x
        y_set = set(y) if not isinstance(y, (set, frozenset)) else y

        intersection = x_set & y_set
        union = x_set | y_set

        if len(union) == 0:
            logger.debug("Both sets are empty, returning maximum similarity of 1.0")
            return 1.0
            
        jaccard_index = len(intersection) / len(union)
        logger.debug(f"Jaccard Index similarity calculated as {jaccard_index}")
        return jaccard_index

    def similarities(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        ys: Union[List[Union[Tuple, frozenset, set, List]], Tuple, frozenset, set, List]
    ) -> Union[float, List[float]]:
        """
        Computes similarities between a reference set and multiple other sets.

        Args:
            x: Reference set to compare against.
            ys: List of sets or single set to compare with x.

        Returns:
            Union[float, List[float]]: Similarity scores between x and each set in ys.
        """
        if isinstance(ys, (list, tuple)):
            return [self.similarity(x, y) for y in ys]
        else:
            return self.similarity(x, ys)

    def dissimilarity(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        y: Union[Tuple, frozenset, set, List]
    ) -> float:
        """
        Computes the dissimilarity as 1 minus the similarity.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            float: Dissimilarity between x and y.
        """
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        ys: Union[List[Union[Tuple, frozenset, set, List]], Tuple, frozenset, set, List]
    ) -> Union[float, List[float]]:
        """
        Computes dissimilarities between a reference set and multiple other sets.

        Args:
            x: Reference set to compare against.
            ys: List of sets or single set to compare with x.

        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each set in ys.
        """
        if isinstance(ys, (list, tuple)):
            return [1.0 - sim for sim in self.similarities(x, ys)]
        else:
            return 1.0 - self.similarity(x, ys)

    def check_boundedness(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        y: Union[Tuple, frozenset, set, List]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        The Jaccard Index is bounded between 0 and 1.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[Tuple, frozenset, set, List]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        The Jaccard Index is reflexive since the similarity of a set with itself is 1.

        Args:
            x: Set to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return self.similarity(x, x) == 1.0

    def check_symmetry(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        y: Union[Tuple, frozenset, set, List]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        The Jaccard Index is symmetric as J(x, y) = J(y, x).

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return self.similarity(x, y) == self.similarity(y, x)

    def check_identity(
        self, 
        x: Union[Tuple, frozenset, set, List], 
        y: Union[Tuple, frozenset, set, List]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        The Jaccard Index satisfies identity as identical sets have maximum similarity.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            bool: True if x and y are identical sets, False otherwise.
        """
        return self.similarity(x, y) == 1.0