from typing import Any, Sequence, Tuple, TypeVar, Union
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, bytes, Any)
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_type(SimilarityBase, "BrayCurtisSimilarity")
class BrayCurtisSimilarity(SimilarityBase):
    """
    Concrete implementation of the Bray-Curtis similarity measure.

    The Bray-Curtis similarity is calculated as 1 minus the Bray-Curtis dissimilarity.
    It is commonly used in ecological studies to compare sample compositions.

    Attributes:
        type: Literal["BrayCurtisSimilarity"]
            The type identifier for this similarity measure
    """
    type: Literal["BrayCurtisSimilarity"] = "BrayCurtisSimilarity"
    
    def __init__(self):
        """
        Initialize the BrayCurtisSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized BrayCurtisSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Bray-Curtis similarity between two vectors.

        The Bray-Curtis similarity is computed as:
            1 - (|x - y| / (|x| + |y|))

        Args:
            x: InputType
                The first vector to compare
            y: InputType
                The second vector to compare

        Returns:
            float:
                A float representing the similarity between x and y,
                ranging between 0 (completely dissimilar) and 1 (identical).

        Raises:
            ValueError: If input vectors contain negative values
        """
        if not (isinstance(x, (list, np.ndarray)) and isinstance(y, (list, np.ndarray))):
            x = np.array(x)
            y = np.array(y)

        if np.any(x < 0) or np.any(y < 0):
            raise ValueError("Input vectors must contain non-negative values")

        # Calculate absolute differences
        differences = np.abs(x - y)
        total = np.sum(differences)
        sum_all = np.sum(x) + np.sum(y)

        if sum_all == 0:
            # Handle case where both vectors are zero vectors
            return 1.0

        similarity = 1.0 - (total / sum_all)
        logger.debug(f"Similarity calculation result: {similarity}")
        return similarity

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate Bray-Curtis similarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of similarity scores corresponding to each pair
        """
        similarities = []
        for pair in pairs:
            x, y = pair
            similarities.append(self.similarity(x, y))
        logger.debug(f"Similarities for multiple pairs calculated: {similarities}")
        return similarities

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Bray-Curtis dissimilarity between two vectors.

        The Bray-Curtis dissimilarity is computed as:
            (|x - y|) / (|x| + |y|)

        Args:
            x: InputType
                The first vector to compare
            y: InputType
                The second vector to compare

        Returns:
            float:
                A float representing the dissimilarity between x and y,
                ranging between 0 (identical) and 1 (completely dissimilar)

        Raises:
            ValueError: If input vectors contain negative values
        """
        if not (isinstance(x, (list, np.ndarray)) and isinstance(y, (list, np.ndarray))):
            x = np.array(x)
            y = np.array(y)

        if np.any(x < 0) or np.any(y < 0):
            raise ValueError("Input vectors must contain non-negative values")

        # Calculate absolute differences
        differences = np.abs(x - y)
        total = np.sum(differences)
        sum_all = np.sum(x) + np.sum(y)

        if sum_all == 0:
            # Handle case where both vectors are zero vectors
            return 0.0

        dissimilarity = total / sum_all
        logger.debug(f"Dissimilarity calculation result: {dissimilarity}")
        return dissimilarity

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate Bray-Curtis dissimilarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of dissimilarity scores corresponding to each pair
        """
        dissimilarities = []
        for pair in pairs:
            x, y = pair
            dissimilarities.append(self.dissimilarity(x, y))
        logger.debug(f"Dissimilarities for multiple pairs calculated: {dissimilarities}")
        return dissimilarities