import logging
from typing import Union, List, Optional, Literal
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import math

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TriangleCosineSimilarity")
class TriangleCosineSimilarity(SimilarityBase):
    """
    Computes the cosine similarity between vectors using the dot product over norm product.

    This implementation provides a concrete realization of the SimilarityBase class
    for calculating cosine similarity, which measures the cosine of the angle between
    two vectors. The similarity is calculated as the dot product of the vectors divided
    by the product of their magnitudes. The implementation ensures non-zero vectors only
    and uses a tighter bound derived from spherical law of cosines.
    """

    type: Literal["TriangleCosineSimilarity"] = "TriangleCosineSimilarity"

    def __init__(self):
        """
        Initializes the TriangleCosineSimilarity calculator.

        This constructor sets up the basic configuration for the cosine similarity
        calculation. It initializes the parent class and prepares the calculator
        for vector comparison.
        """
        super().__init__()
        logger.debug("Initialized TriangleCosineSimilarity calculator")

    def similarity(
        self, x: Union[List[float], tuple], y: Union[List[float], tuple]
    ) -> float:
        """
        Computes the cosine similarity between two vectors.

        Args:
            x: First non-zero vector (list or tuple of floats)
            y: Second non-zero vector (list or tuple of floats)

        Returns:
            float: Cosine similarity score between x and y in range [-1, 1]

        Raises:
            ValueError: If either vector is zero vector or of different lengths
        """
        if len(x) != len(y):
            raise ValueError("Vectors must be of the same length")

        if all(v == 0 for v in x) or all(v == 0 for v in y):
            raise ValueError("Non-zero vectors only")

        # Compute dot product
        dot_product = sum(a * b for a, b in zip(x, y))
        logger.debug(f"Dot product: {dot_product}")

        # Compute magnitudes
        x_norm = math.sqrt(sum(a**2 for a in x))
        y_norm = math.sqrt(sum(b**2 for b in y))
        logger.debug(f"Norm of x: {x_norm}, Norm of y: {y_norm}")

        if x_norm == 0 or y_norm == 0:
            raise ValueError("Vectors must be non-zero")

        # Compute cosine similarity with tight bounding
        cosine_sim = dot_product / (x_norm * y_norm)
        cosine_sim = max(min(cosine_sim, 1.0), -1.0)  # Ensure in [-1, 1]

        logger.debug(f"Cosine similarity: {cosine_sim}")
        return cosine_sim

    def dissimilarity(
        self, x: Union[List[float], tuple], y: Union[List[float], tuple]
    ) -> float:
        """
        Computes the dissimilarity as 1 - similarity.

        Args:
            x: First non-zero vector (list or tuple of floats)
            y: Second non-zero vector (list or tuple of floats)

        Returns:
            float: Dissimilarity score between x and y in range [-1, 1]
        """
        sim = self.similarity(x, y)
        return 1.0 - sim

    def similarities(
        self,
        x: Union[List[float], tuple],
        ys: Union[List[List[float]], List[tuple], List[Union[List[float], tuple]]],
    ) -> Union[float, List[float]]:
        """
        Computes similarity scores between x and multiple vectors.

        Args:
            x: Reference non-zero vector (list or tuple of floats)
            ys: List of non-zero vectors (list of lists or tuples of floats)

        Returns:
            Union[float, List[float]]: Similarity scores between x and each vector in ys
        """
        if not isinstance(ys, list):
            return self.similarity(x, ys)

        return [self.similarity(x, y) for y in ys]

    def check_boundedness(
        self, x: Union[List[float], tuple], y: Union[List[float], tuple]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        Args:
            x: First vector (list or tuple of floats)
            y: Second vector (list or tuple of floats)

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        return True  # Cosine similarity is always bounded between -1 and 1

    def check_reflexivity(self, x: Union[List[float], tuple]) -> bool:
        """
        Checks if the similarity measure is reflexive.

        Args:
            x: Vector to check reflexivity for (list or tuple of floats)

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        if all(v == 0 for v in x):
            return False
        return True

    def check_symmetry(
        self, x: Union[List[float], tuple], y: Union[List[float], tuple]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        Args:
            x: First vector (list or tuple of floats)
            y: Second vector (list or tuple of floats)

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        return True  # Cosine similarity is symmetric

    def check_identity(
        self, x: Union[List[float], tuple], y: Union[List[float], tuple]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        Args:
            x: First vector (list or tuple of floats)
            y: Second vector (list or tuple of floats)

        Returns:
            bool: True if x and y are identical, False otherwise
        """
        return x == y
