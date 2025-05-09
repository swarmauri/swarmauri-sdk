from typing import Union, Sequence, Tuple, Any, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "DiceSimilarity")
class DiceSimilarity(SimilarityBase):
    """
    Concrete implementation of the Dice similarity measure for set-based comparisons.

    This class implements the Dice similarity coefficient, which measures the
    similarity between two sets based on their overlap. The Dice coefficient is
    defined as:

        Dice(a, b) = 2 * |a ∩ b| / (|a| + |b|)

    where |a| and |b| are the cardinalities of sets a and b, respectively.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        resource: str = ResourceTypes.SIMILARITY.value
            Specifies the resource type for this component
    """
    resource: str = "similarity"

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the Dice similarity coefficient between two elements.

        The Dice coefficient is a measure of similarity between two sets,
        defined as twice the size of their intersection divided by the sum
        of the sizes of both sets.

        Args:
            a: Union[Any, None]
                The first element to compare (typically a set or list)
            b: Union[Any, None]
                The second element to compare (typically a set or list)

        Returns:
            float:
                The Dice similarity coefficient, ranging from 0 to 1

        Raises:
            ValueError:
                If either a or b is None
        """
        if a is None or b is None:
            logger.error("Both elements must be non-None for similarity calculation")
            raise ValueError("Both elements must be non-None")

        if not isinstance(a, (set, list, tuple)) or not isinstance(b, (set, list, tuple)):
            logger.warning("Input elements should be sets, lists, or tuples for accurate calculation")

        a_set = set(a) if not isinstance(a, set) else a
        b_set = set(b) if not isinstance(b, set) else b

        intersection = a_set & b_set
        intersection_size = len(intersection)
        a_size = len(a_set)
        b_size = len(b_set)

        if (a_size + b_size) == 0:
            logger.debug("Both elements are empty sets/sequences")
            return 1.0

        dice_coefficient = 2.0 * intersection_size / (a_size + b_size)
        logger.debug(f"Dice similarity calculated as {dice_coefficient}")
        return dice_coefficient

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates Dice similarity coefficients between one element and a list of elements.

        Args:
            a: Union[Any, None]
                The element to compare against multiple elements
            b_list: Sequence[Union[Any, None]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of Dice similarity coefficients

        Raises:
            ValueError:
                If a is None
        """
        if a is None:
            logger.error("Base element must be non-None for similarities calculation")
            raise ValueError("Base element must be non-None")

        if not isinstance(b_list, Sequence):
            logger.error("Expected a sequence for b_list")
            raise TypeError("Expected a sequence for b_list")

        similarity_scores = []
        for b in b_list:
            similarity_score = self.similarity(a, b)
            similarity_scores.append(similarity_score)

        logger.debug(f"Calculated similarities: {similarity_scores}")
        return tuple(similarity_scores)

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity score as 1 minus the Dice similarity.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The dissimilarity score, ranging from 0 to 1
        """
        similarity = self.similarity(a, b)
        dissimilarity_score = 1.0 - similarity
        logger.debug(f"Dice dissimilarity calculated as {dissimilarity_score}")
        return dissimilarity_score

    def dissimilarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates dissimilarity scores between one element and a list of elements.

        Args:
            a: Union[Any, None]
                The element to compare against multiple elements
            b_list: Sequence[Union[Any, None]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores
        """
        similarity_scores = self.similarities(a, b_list)
        dissimilarity_scores = tuple(1.0 - score for score in similarity_scores)
        logger.debug(f"Dice dissimilarities calculated as {dissimilarity_scores}")
        return dissimilarity_scores

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Dice similarity measure is bounded.

        The Dice coefficient is inherently bounded between 0 and 1 due to its
        mathematical formulation.

        Args:
            a: Union[Any, None]
                The first element to compare (unused in this check)
            b: Union[Any, None]
                The second element to compare (unused in this check)

        Returns:
            bool:
                True if the measure is bounded, False otherwise
        """
        logger.debug("Dice similarity is bounded between 0 and 1")
        return True

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the Dice similarity measure is reflexive.

        Reflexivity is satisfied if the similarity of any element with itself is 1.

        Args:
            a: Union[Any, None]
                The element to check reflexivity for

        Returns:
            bool:
                True if the measure is reflexive, False otherwise
        """
        if a is None:
            logger.debug("Reflexivity not applicable for None")
            return False

        a_set = set(a)
        reflexivity = self.similarity(a_set, a_set) == 1.0
        logger.debug(f"Dice similarity reflexivity check: {reflexivity}")
        return reflexivity

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Dice similarity measure is symmetric.

        Symmetry is satisfied if s(a, b) = s(b, a) for all a, b.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the measure is symmetric, False otherwise
        """
        if a is None or b is None:
            logger.debug("Symmetry not applicable for None values")
            return False

        a_set = set(a)
        b_set = set(b)
        symmetry = self.similarity(a_set, b_set) == self.similarity(b_set, a_set)
        logger.debug(f"Dice similarity symmetry check: {symmetry}")
        return symmetry

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Dice similarity measure satisfies identity.

        Identity is satisfied if s(a, b) = 1 if and only if a = b.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the measure satisfies identity, False otherwise
        """
        if a is None or b is None:
            logger.debug("Identity not applicable for None values")
            return False

        a_set = set(a)
        b_set = set(b)
        identity = (a_set == b_set) and (self.similarity(a_set, b_set) == 1.0)
        logger.debug(f"Dice similarity identity check: {identity}")
        return identity