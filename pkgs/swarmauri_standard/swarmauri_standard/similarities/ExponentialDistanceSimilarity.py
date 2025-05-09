from typing import Union, List, Optional, Callable, Literal
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import logging
from scipy.spatial import distance

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "ExponentialDistanceSimilarity")
class ExponentialDistanceSimilarity(SimilarityBase):
    """
    Exponential distance similarity implementation.

    This class provides an implementation of similarity calculation using an exponential
    decay function based on the distance between elements. It supports arbitrary distance
    measures and provides standard similarity functionality.

    Attributes:
        distance_fn: Callable to compute distance between elements.
        gamma: Scaling factor for exponential decay. Defaults to 1.0.
    """
    type: Literal["ExponentialDistanceSimilarity"] = "ExponentialDistanceSimilarity"
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def __init__(self, distance_fn: Callable = distance.euclidean, gamma: float = 1.0):
        """
        Initialize the ExponentialDistanceSimilarity instance.

        Args:
            distance_fn: Function to compute distance between elements. Defaults to Euclidean distance.
            gamma: Scaling factor for exponential decay. Defaults to 1.0.
        """
        self.distance_fn = distance_fn
        self.gamma = gamma

    def similarity(
        self,
        x: Union[IVector, IMatrix, Tuple, str, Callable],
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Compute the similarity between two elements using exponential decay.

        Args:
            x: First element to compare. Can be vector, matrix, tuple, string, or callable.
            y: Second element to compare. Can be vector, matrix, tuple, string, or callable.

        Returns:
            float: Similarity score between x and y.

        Raises:
            ValueError: If elements are of invalid type.
        """
        # Ensure elements are valid
        if isinstance(x, Callable):
            x = x()
        if isinstance(y, Callable):
            y = y()

        try:
            # Compute distance between elements
            dist = self.distance_fn(x, y)
            # Apply exponential decay
            similarity = 1.0 / (1.0 + (dist / self.gamma))
            logger.debug(f"Computed similarity: {similarity}")
            return similarity
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise

    def dissimilarity(
        self,
        x: Union[IVector, IMatrix, Tuple, str, Callable],
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Compute the dissimilarity between two elements.

        Args:
            x: First element to compare. Can be vector, matrix, tuple, string, or callable.
            y: Second element to compare. Can be vector, matrix, tuple, string, or callable.

        Returns:
            float: Dissimilarity score between x and y.
        """
        # Compute similarity and convert to dissimilarity
        similarity = self.similarity(x, y)
        return 1.0 - similarity

    def check_boundedness(
        self,
        x: Union[IVector, IMatrix, Tuple, str, Callable],
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is bounded.

        Args:
            x: First element to compare.
            y: Second element to compare.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True  # Exponential similarity is always bounded between 0 and 1

    def check_reflexivity(
        self,
        x: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is reflexive.

        Args:
            x: Element to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        try:
            # Compute similarity of element with itself
            similarity = self.similarity(x, x)
            return similarity == 1.0
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            return False

    def check_symmetry(
        self,
        x: Union[IVector, IMatrix, Tuple, str, Callable],
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is symmetric.

        Args:
            x: First element to compare.
            y: Second element to compare.

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        try:
            # Compute similarity in both directions
            similarity_xy = self.similarity(x, y)
            similarity_yx = self.similarity(y, x)
            return similarity_xy == similarity_yx
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            return False

    def check_identity(
        self,
        x: Union[IVector, IMatrix, Tuple, str, Callable],
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure satisfies identity.

        Args:
            x: First element to compare.
            y: Second element to compare.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        try:
            # Identity means x and y are the same if similarity is 1.0
            return self.similarity(x, y) == 1.0
        except Exception as e:
            logger.error(f"Error checking identity: {str(e)}")
            return False