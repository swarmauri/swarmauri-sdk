import logging
import numpy as np
from typing import Union, List, Optional, Tuple, Callable
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "CosineSimilarity")
class CosineSimilarity(SimilarityBase):
    """
    Computes the cosine similarity between vectors.

    This class provides an implementation of cosine similarity, a measure of
    similarity between two non-zero vectors of an inner product space that
    measures the cosine of the angle between them. The cosine similarity is
    the dot product of the vectors divided by the product of their magnitudes.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """

    type: str = "CosineSimilarity"
    resource: Optional[str] = SimilarityBase.ResourceTypes.SIMILARITY

    def similarity(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        y: Union[np.ndarray, Tuple, str, Callable],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            x: First vector to compare.
            y: Second vector to compare.

        Returns:
            float: Cosine similarity score between x and y.

        Raises:
            ValueError: If either vector is zero.
        """
        # Ensure inputs are numpy arrays
        x = np.asarray(x) if not isinstance(x, (np.ndarray, str)) else x
        y = np.asarray(y) if not isinstance(y, (np.ndarray, str)) else y

        if callable(x):
            x = x()
        if callable(y):
            y = y()

        # Check for non-zero vectors
        if np.linalg.norm(x) == 0 or np.linalg.norm(y) == 0:
            raise ValueError("Non-zero vectors only. Found zero vector.")

        # Compute dot product
        dot_product = np.dot(x, y)

        # Compute magnitudes
        x_magnitude = np.linalg.norm(x)
        y_magnitude = np.linalg.norm(y)

        # Compute cosine similarity
        similarity = dot_product / (x_magnitude * y_magnitude)
        similarity = np.clip(similarity, -1.0, 1.0)

        return similarity

    def similarities(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        ys: Union[
            List[Union[np.ndarray, Tuple, str, Callable]],
            Union[np.ndarray, Tuple, str, Callable],
        ],
    ) -> Union[float, List[float]]:
        """
        Calculate cosine similarities between a vector and multiple vectors.

        Args:
            x: Reference vector to compare against.
            ys: List of vectors or single vector to compare with x.

        Returns:
            Union[float, List[float]]: Cosine similarity scores between x and each vector in ys.
        """
        if not isinstance(ys, list):
            ys = [ys]

        return [self.similarity(x, y) for y in ys]

    def dissimilarity(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        y: Union[np.ndarray, Tuple, str, Callable],
    ) -> float:
        """
        Calculate cosine dissimilarity between two vectors.

        Args:
            x: First vector to compare.
            y: Second vector to compare.

        Returns:
            float: Dissimilarity score between x and y.
        """
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        ys: Union[
            List[Union[np.ndarray, Tuple, str, Callable]],
            Union[np.ndarray, Tuple, str, Callable],
        ],
    ) -> Union[float, List[float]]:
        """
        Calculate cosine dissimilarities between a vector and multiple vectors.

        Args:
            x: Reference vector to compare against.
            ys: List of vectors or single vector to compare with x.

        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each vector in ys.
        """
        if not isinstance(ys, list):
            ys = [ys]

        return [self.dissimilarity(x, y) for y in ys]

    def check_boundedness(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        y: Union[np.ndarray, Tuple, str, Callable],
    ) -> bool:
        """
        Check if the similarity measure is bounded.

        Args:
            x: First vector to compare.
            y: Second vector to compare.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(self, x: Union[np.ndarray, Tuple, str, Callable]) -> bool:
        """
        Check if the similarity measure is reflexive.

        Args:
            x: Vector to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return True

    def check_symmetry(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        y: Union[np.ndarray, Tuple, str, Callable],
    ) -> bool:
        """
        Check if the similarity measure is symmetric.

        Args:
            x: First vector to compare.
            y: Second vector to compare.

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return True

    def check_identity(
        self,
        x: Union[np.ndarray, Tuple, str, Callable],
        y: Union[np.ndarray, Tuple, str, Callable],
    ) -> bool:
        """
        Check if the similarity measure satisfies identity.

        Args:
            x: First vector to compare.
            y: Second vector to compare.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        return np.allclose(self.similarity(x, y), 1.0)
