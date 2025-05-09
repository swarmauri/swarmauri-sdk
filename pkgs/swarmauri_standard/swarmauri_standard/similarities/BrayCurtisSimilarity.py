from typing import Union, List, Optional, Tuple
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "BrayCurtisSimilarity")
class BrayCurtisSimilarity(SimilarityBase):
    """
    A concrete implementation of the SimilarityBase class for Bray-Curtis similarity measure.

    The Bray-Curtis similarity is calculated as 1 minus the sum of absolute differences
    between corresponding elements of two vectors, divided by the sum of all elements.
    It is commonly used in ecology to compare sample compositions.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    type: Literal["BrayCurtisSimilarity"] = "BrayCurtisSimilarity"
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def similarity(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable], 
        y: Union[Tuple[float, ...], List[float], str, Callable]
    ) -> float:
        """
        Calculate the Bray-Curtis similarity between two vectors.

        The Bray-Curtis similarity is computed as:
            1 - (sum(|x_i - y_i|) / sum(x_i + y_i))

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            float: Bray-Curtis similarity score between 0 and 1

        Raises:
            ValueError: If input vectors contain negative values
        """
        # Ensure inputs are valid vectors
        if not (isinstance(x, (tuple, list)) and isinstance(y, (tuple, list))):
            raise ValueError("Both inputs must be vectors (tuple or list)")

        # Check for non-negative values
        if any(val < 0 for val in x) or any(val < 0 for val in y):
            raise ValueError("Input vectors must contain only non-negative values")

        # Calculate sum of absolute differences
        sum_diff = sum(abs(a - b) for a, b in zip(x, y))
        # Calculate total sum of both vectors
        total = sum(x) + sum(y)

        if total == 0:
            # Special case: both vectors are zero vectors
            return 1.0

        similarity = 1 - (sum_diff / total)

        logger.debug(f"Bray-Curtis similarity calculated: {similarity}")
        return similarity

    def similarities(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable], 
        ys: Union[List[Union[Tuple[float, ...], List[float], str, Callable]], 
            Union[Tuple[float, ...], List[float], str, Callable]]
    ) -> Union[float, List[float]]:
        """
        Calculate Bray-Curtis similarities between a reference vector and multiple vectors.

        Args:
            x: Reference vector
            ys: List of vectors or single vector to compare against

        Returns:
            Union[float, List[float]]: Similarity scores against each vector in ys
        """
        if not isinstance(ys, list):
            ys = [ys]

        return [self.similarity(x, y) for y in ys]

    def dissimilarity(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable], 
        y: Union[Tuple[float, ...], List[float], str, Callable]
    ) -> float:
        """
        Calculate the Bray-Curtis dissimilarity between two vectors.

        This is simply 1 minus the similarity.

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            float: Dissimilarity score between 0 and 1
        """
        return 1 - self.similarity(x, y)

    def check_boundedness(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable], 
        y: Union[Tuple[float, ...], List[float], str, Callable]
    ) -> bool:
        """
        Check if the Bray-Curtis similarity measure is bounded.

        The Bray-Curtis similarity ranges between 0 and 1, making it bounded.

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable]
    ) -> bool:
        """
        Check if the Bray-Curtis similarity measure is reflexive.

        The measure is reflexive since similarity(x, x) = 1 for any vector x.

        Args:
            x: Vector to check reflexivity for

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        return True

    def check_symmetry(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable], 
        y: Union[Tuple[float, ...], List[float], str, Callable]
    ) -> bool:
        """
        Check if the Bray-Curtis similarity measure is symmetric.

        The measure is symmetric since similarity(x, y) = similarity(y, x).

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        return True

    def check_identity(
        self, 
        x: Union[Tuple[float, ...], List[float], str, Callable], 
        y: Union[Tuple[float, ...], List[float], str, Callable]
    ) -> bool:
        """
        Check if the Bray-Curtis similarity measure satisfies identity.

        The measure satisfies identity since similarity(x, x) = 1 and x ≠ y implies similarity(x, y) < 1.

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        return x == y