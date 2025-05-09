from typing import Union, List, Optional, Literal
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging
from sets import Set

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class OverlapCoefficientSimilarity(SimilarityBase):
    """
    Implementation of the Overlap Coefficient similarity measure for the swarmauri_standard package.

    The Overlap Coefficient measures the ratio of the intersection of two sets to the size of the smaller set.
    It is sensitive to complete inclusion of one set within another.

    Inherits from:
        SimilarityBase: Base class providing foundational functionality for similarity measures.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    type: Literal["OverlapCoefficientSimilarity"] = "OverlapCoefficientSimilarity"
    resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)

    def __init__(self):
        """Initialize the OverlapCoefficientSimilarity instance."""
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def similarity(
        self, 
        x: Union[Set, List, Tuple, str], 
        y: Union[Set, List, Tuple, str]
    ) -> float:
        """
        Calculate the similarity between two sets using the Overlap Coefficient.

        The Overlap Coefficient is defined as the size of the intersection divided by the size of the smaller set.

        Args:
            x: First set to compare. Can be a set, list, tuple, or string.
            y: Second set to compare. Can be a set, list, tuple, or string.

        Returns:
            float: Similarity score between x and y, ranging from 0 to 1.

        Raises:
            ValueError: If either x or y is empty after conversion to set.
        """
        if not x or not y:
            raise ValueError("Both sets must be non-empty for Overlap Coefficient calculation")

        # Convert inputs to sets if they aren't already
        if not isinstance(x, Set):
            x = Set(x)
        if not isinstance(y, Set):
            y = Set(y)

        intersection = x & y
        overlap = len(intersection)
        smaller_size = min(len(x), len(y))

        if smaller_size == 0:
            return 0.0

        similarity = overlap / smaller_size
        logger.debug(f"Overlap Coefficient Similarity: {similarity}")
        return similarity

    def similarities(
        self, 
        x: Union[Set, List, Tuple, str], 
        ys: Union[List[Union[Set, List, Tuple, str]], Union[Set, List, Tuple, str]]
    ) -> Union[float, List[float]]:
        """
        Calculate similarities between a reference set and multiple other sets.

        Args:
            x: Reference set to compare against. Can be a set, list, tuple, or string.
            ys: List of sets or single set to compare with x.

        Returns:
            Union[float, List[float]]: Similarity scores between x and each set in ys.
        """
        if not isinstance(ys, list):
            return self.similarity(x, ys)

        similarities = []
        for y in ys:
            similarities.append(self.similarity(x, y))
        return similarities

    def dissimilarity(
        self, 
        x: Union[Set, List, Tuple, str], 
        y: Union[Set, List, Tuple, str]
    ) -> float:
        """
        Calculate the dissimilarity between two sets using the Overlap Coefficient.

        Dissimilarity is defined as 1 minus the similarity.

        Args:
            x: First set to compare. Can be a set, list, tuple, or string.
            y: Second set to compare. Can be a set, list, tuple, or string.

        Returns:
            float: Dissimilarity score between x and y, ranging from 0 to 1.
        """
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self, 
        x: Union[Set, List, Tuple, str], 
        ys: Union[List[Union[Set, List, Tuple, str]], Union[Set, List, Tuple, str]]
    ) -> Union[float, List[float]]:
        """
        Calculate dissimilarities between a reference set and multiple other sets.

        Args:
            x: Reference set to compare against. Can be a set, list, tuple, or string.
            ys: List of sets or single set to compare with x.

        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each set in ys.
        """
        if not isinstance(ys, list):
            return self.dissimilarity(x, ys)

        dissimilarities = []
        for y in ys:
            dissimilarities.append(self.dissimilarity(x, y))
        return dissimilarities

    def check_boundedness(
        self, 
        x: Union[Set, List, Tuple, str], 
        y: Union[Set, List, Tuple, str]
    ) -> bool:
        """
        Check if the Overlap Coefficient similarity measure is bounded.

        The Overlap Coefficient is bounded between 0 and 1.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[Set, List, Tuple, str]
    ) -> bool:
        """
        Check if the Overlap Coefficient similarity measure is reflexive.

        The Overlap Coefficient is reflexive because any set compared with itself will have a similarity of 1.

        Args:
            x: Set to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return True

    def check_symmetry(
        self, 
        x: Union[Set, List, Tuple, str], 
        y: Union[Set, List, Tuple, str]
    ) -> bool:
        """
        Check if the Overlap Coefficient similarity measure is symmetric.

        The Overlap Coefficient is symmetric because the overlap of x and y is the same as the overlap of y and x.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return True

    def check_identity(
        self, 
        x: Union[Set, List, Tuple, str], 
        y: Union[Set, List, Tuple, str]
    ) -> bool:
        """
        Check if the Overlap Coefficient similarity measure satisfies identity.

        The Overlap Coefficient satisfies identity because if x and y are identical, their intersection will be the full size of the smaller set, resulting in a similarity of 1.

        Args:
            x: First set to compare.
            y: Second set to compare.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        return self.similarity(x, y) == 1.0