from typing import Any, Sequence, Tuple, TypeVar, Union, Literal
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging
from ..SimilarityBase import SimilarityBase

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, bytes, Any)
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_type(SimilarityBase, "TanimotoSimilarity")
class TanimotoSimilarity(SimilarityBase):
    """
    Implementation of the Tanimoto similarity measure for real vectors.

    The Tanimoto similarity is a commonly used measure in cheminformatics
    for comparing molecular fingerprints. It generalizes the Jaccard index
    to real-valued vectors. The similarity is calculated as:

    Tanimoto(a, b) = (a·b) / (|a|² + |b|² - a·b)

    where:
    - a·b is the dot product of vectors a and b
    - |a|² is the squared magnitude of vector a
    - |b|² is the squared magnitude of vector b

    This implementation ensures that vectors are non-zero and provides
    efficient computation of similarities for both individual pairs
    and batches of pairs.
    """
    
    type: Literal["TanimotoSimilarity"] = "TanimotoSimilarity"
    resource: str = ResourceTypes.SIMILARITY.value

    def __init__(self):
        """
        Initialize the TanimotoSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized TanimotoSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Tanimoto similarity between two vectors.

        Args:
            x: InputType
                The first vector to compare
            y: InputType
                The second vector to compare

        Returns:
            float:
                A float representing the Tanimoto similarity between x and y.
                The value will be in the range [0, 1]

        Raises:
            ValueError: If either vector is empty or not of the same length
            ZeroDivisionError: If the denominator is zero (should not occur with non-zero vectors)
        """
        # Ensure inputs are valid
        if not x or not y:
            raise ValueError("Vectors must be non-zero")
            
        if len(x) != len(y):
            raise ValueError("Vectors must be of the same length")

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(x, y))
        # Calculate squared magnitudes
        mag_x_sq = sum(a ** 2 for a in x)
        mag_y_sq = sum(b ** 2 for b in y)

        # Compute denominator
        denominator = mag_x_sq + mag_y_sq - dot_product

        # Handle division by zero
        if denominator == 0:
            raise ZeroDivisionError("Denominator is zero - cannot compute similarity")

        similarity = dot_product / denominator

        logger.debug(f"Calculated Tanimoto similarity: {similarity}")
        return similarity

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate Tanimoto similarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of Tanimoto similarity scores corresponding to each pair
        """
        return [self.similarity(x, y) for x, y in pairs]

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Tanimoto dissimilarity between two vectors.

        The dissimilarity is simply 1 minus the similarity.

        Args:
            x: InputType
                The first vector to compare
            y: InputType
                The second vector to compare

        Returns:
            float:
                A float representing the Tanimoto dissimilarity between x and y.
                The value will be in the range [0, 1]
        """
        similarity = self.similarity(x, y)
        dissimilarity = 1.0 - similarity
        
        logger.debug(f"Calculated Tanimoto dissimilarity: {dissimilarity}")
        return dissimilarity

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate Tanimoto dissimilarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of Tanimoto dissimilarity scores corresponding to each pair
        """
        return [self.dissimilarity(x, y) for x, y in pairs]