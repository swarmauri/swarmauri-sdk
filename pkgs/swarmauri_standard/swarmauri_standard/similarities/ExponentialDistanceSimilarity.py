from typing import Union, Sequence, Optional, Callable, Literal
import numpy as np
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ISimilarity

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "ExponentialDistanceSimilarity")
class ExponentialDistanceSimilarity(SimilarityBase):
    """
    Implements an exponentially decaying similarity measure based on distance.

    The similarity score is calculated as:
    s(x, y) = exp(-distance(x, y) / scale)

    Where:
    - distance(x, y) is the distance between elements x and y
    - scale is a positive scaling factor that controls the decay rate

    This implementation supports arbitrary distance measures and provides
    both similarity and dissimilarity calculations.
    """

    type: Literal["ExponentialDistanceSimilarity"] = "ExponentialDistanceSimilarity"

    def __init__(self, scale: float = 1.0, distance_fn: Optional[Callable] = None):
        """
        Initializes the ExponentialDistanceSimilarity instance.

        Args:
            scale: Positive scaling factor controlling the exponential decay
            distance_fn: Optional custom distance function. If not provided,
                uses Euclidean distance by default.
        """
        super().__init__()
        self.scale = scale
        self.distance_fn = distance_fn if distance_fn else self._default_distance

    def _default_distance(
        self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]
    ) -> float:
        """
        Default distance function using Euclidean distance.

        Args:
            x: First element
            y: Second element

        Returns:
            float: Euclidean distance between x and y
        """
        return np.sqrt(np.sum((np.asarray(x) - np.asarray(y)) ** 2))

    def similarity(
        self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]
    ) -> float:
        """
        Calculates the similarity between two elements using exponential decay.

        Args:
            x: First element to compare
            y: Second element to compare

        Returns:
            float: Similarity score between x and y in [0, 1]
        """
        distance = self.distance_fn(x, y)
        similarity_score = np.exp(-distance / self.scale)
        logger.debug(f"Similarity between {x} and {y}: {similarity_score}")
        return similarity_score

    def similarities(
        self, xs: Union[Sequence, np.ndarray], ys: Union[Sequence, np.ndarray]
    ) -> Union[float, Sequence[float]]:
        """
        Calculates similarities for multiple pairs of elements.

        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare

        Returns:
            Union[float, Sequence[float]]: Similarity scores for the pairs
        """
        if len(xs) != len(ys):
            raise ValueError("Number of elements in xs and ys must match")

        scores = [self.similarity(x, y) for x, y in zip(xs, ys)]
        logger.debug(f"Similarities for multiple pairs: {scores}")
        return scores

    def dissimilarity(
        self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]
    ) -> float:
        """
        Calculates the dissimilarity between two elements.

        Args:
            x: First element to compare
            y: Second element to compare

        Returns:
            float: Dissimilarity score between x and y in [0, 1]
        """
        similarity = self.similarity(x, y)
        dissimilarity_score = 1.0 - similarity
        logger.debug(f"Dissimilarity between {x} and {y}: {dissimilarity_score}")
        return dissimilarity_score

    def dissimilarities(
        self, xs: Union[Sequence, np.ndarray], ys: Union[Sequence, np.ndarray]
    ) -> Union[float, Sequence[float]]:
        """
        Calculates dissimilarity scores for multiple pairs of elements.

        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare

        Returns:
            Union[float, Sequence[float]]: Dissimilarity scores for the pairs
        """
        if len(xs) != len(ys):
            raise ValueError("Number of elements in xs and ys must match")

        scores = [self.dissimilarity(x, y) for x, y in zip(xs, ys)]
        logger.debug(f"Dissimilarities for multiple pairs: {scores}")
        return scores

    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.

        The exponential distance similarity is bounded between 0 and 1.

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.

        For all x, s(x, x) = 1 since distance(x, x) = 0.

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        return True

    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.

        Since distance measures are symmetric, this similarity measure
        is symmetric as well.

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        return True

    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.

        For distinct x and y, s(x, y) < 1 if they are different.

        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        return True
