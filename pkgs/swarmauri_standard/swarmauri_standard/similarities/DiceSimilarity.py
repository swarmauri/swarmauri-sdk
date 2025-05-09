from typing import Union, List, Optional, Tuple
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "DiceSimilarity")
class DiceSimilarity(SimilarityBase):
    """
    Implementation of the Dice similarity measure for sets.

    The Dice similarity coefficient is a measure of similarity between two sets,
    defined as twice the size of their intersection divided by the sum of the sizes
    of the two sets. This implementation supports both sets and multisets.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """

    type: str = "DiceSimilarity"
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def similarity(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        y: Union[Union[List, Tuple, str], Callable],
    ) -> float:
        """
        Calculate the Dice similarity coefficient between two sets.

        Args:
            x: First set or iterable to compare.
            y: Second set or iterable to compare.

        Returns:
            float: Similarity score between 0 (no overlap) and 1 (complete overlap).

        Raises:
            ValueError: If either input is None or not iterable.
        """
        try:
            # Convert inputs to sets
            set_x = set(x) if not isinstance(x, str) else set(x)
            set_y = set(y) if not isinstance(y, str) else set(y)

            # Calculate intersection and sizes
            intersection = len(set_x & set_y)
            size_x = len(set_x)
            size_y = len(set_y)

            # Avoid division by zero
            if size_x + size_y == 0:
                return 0.0

            # Compute Dice similarity
            similarity = (2 * intersection) / (size_x + size_y)
            logger.debug(f"Dice similarity calculated: {similarity}")

            return similarity

        except Exception as e:
            logger.error(f"Error calculating Dice similarity: {str(e)}")
            raise ValueError(f"Failed to calculate similarity: {str(e)}")

    def similarities(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        ys: Union[
            List[Union[List, Tuple, str, Callable]], Union[List, Tuple, str, Callable]
        ],
    ) -> Union[float, List[float]]:
        """
        Calculate Dice similarity coefficients between a reference set and multiple sets.

        Args:
            x: Reference set or iterable.
            ys: List of sets or iterables to compare against x.

        Returns:
            Union[float, List[float]]: Similarity scores for each set in ys.

        Raises:
            ValueError: If any input is invalid.
        """
        try:
            # Ensure ys is a list
            if not isinstance(ys, list):
                ys = [ys]

            # Initialize results list
            results = []

            # Calculate similarity for each element in ys
            for y in ys:
                results.append(self.similarity(x, y))

            logger.debug(f"Calculated similarities: {results}")

            return results

        except Exception as e:
            logger.error(f"Error calculating similarities: {str(e)}")
            raise ValueError(f"Failed to calculate similarities: {str(e)}")

    def dissimilarity(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        y: Union[Union[List, Tuple, str], Callable],
    ) -> float:
        """
        Calculate the dissimilarity as 1 - similarity.

        Args:
            x: First set or iterable.
            y: Second set or iterable.

        Returns:
            float: Dissimilarity score between 0 (identical) and 1 (completely different).
        """
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        ys: Union[
            List[Union[List, Tuple, str, Callable]], Union[List, Tuple, str, Callable]
        ],
    ) -> Union[float, List[float]]:
        """
        Calculate dissimilarities between a reference set and multiple sets.

        Args:
            x: Reference set or iterable.
            ys: List of sets or iterables to compare against x.

        Returns:
            Union[float, List[float]]: Dissimilarity scores for each set in ys.
        """
        similarities = self.similarities(x, ys)
        if isinstance(similarities, float):
            return 1.0 - similarities
        else:
            return [1.0 - s for s in similarities]

    def check_boundedness(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        y: Union[Union[List, Tuple, str], Callable],
    ) -> bool:
        """
        Check if the similarity measure is bounded.

        The Dice similarity measure is bounded between 0 and 1.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(self, x: Union[Union[List, Tuple, str], Callable]) -> bool:
        """
        Check if the similarity measure is reflexive.

        The Dice similarity measure is reflexive since similarity(x, x) = 1.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return True

    def check_symmetry(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        y: Union[Union[List, Tuple, str], Callable],
    ) -> bool:
        """
        Check if the similarity measure is symmetric.

        The Dice similarity measure is symmetric since similarity(x, y) = similarity(y, x).

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return True

    def check_identity(
        self,
        x: Union[Union[List, Tuple, str], Callable],
        y: Union[Union[List, Tuple, str], Callable],
    ) -> bool:
        """
        Check if the similarity measure satisfies identity.

        The Dice similarity measure satisfies identity since if x == y, similarity(x, y) = 1.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        return self.similarity(x, y) == 1.0
