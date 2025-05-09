import logging
import numpy as np
from typing import Sequence, Tuple, Any
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)

InputType = Any
OutputType = float


@ComponentBase.register_model()
class GaussianRBFSimilarity(SimilarityBase):
    """
    Concrete implementation of the RBF (Gaussian) similarity measure.

    This class implements the Gaussian radial basis function (RBF) similarity,
    which measures the exponential decay of similarity with squared Euclidean distance.
    The similarity is calculated as:

    similarity(x, y) = exp(-γ ||x - y||²)

    where γ is a positive parameter controlling the bandwidth of the RBF.

    Attributes:
        gamma: float
            The bandwidth parameter of the RBF kernel. Must be greater than 0.
    """

    type: str = "GaussianRBFSimilarity"

    def __init__(self, gamma: float = 1.0):
        """
        Initialize the GaussianRBFSimilarity instance.

        Args:
            gamma: float
                The bandwidth parameter of the RBF kernel. Must be greater than 0.
                Defaults to 1.0
        """
        super().__init__()
        if gamma <= 0:
            raise ValueError("Gamma must be greater than 0")
        self.gamma = gamma
        logger.debug("Initialized GaussianRBFSimilarity with gamma=%s", gamma)

    def similarity(self, x: InputType, y: InputType) -> OutputType:
        """
        Calculate the Gaussian RBF similarity between two elements.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            OutputType:
                A float representing the similarity between x and y,
                ranging between 0 and 1.

        Note:
            The elements can be of any type that can be converted to a numpy array.
            The similarity is computed as exp(-gamma * ||x - y||²).
        """
        try:
            # Convert inputs to numpy arrays if they aren't already
            x_array = np.asarray(x)
            y_array = np.asarray(y)

            # Compute squared Euclidean distance
            distance_sq = np.linalg.norm(x_array - y_array) ** 2

            # Compute RBF similarity
            similarity = np.exp(-self.gamma * distance_sq)

            logger.debug("Computed similarity: %s", similarity)
            return similarity

        except Exception as e:
            logger.error("Error computing similarity", exc_info=e)
            raise

    def similarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[OutputType]:
        """
        Calculate Gaussian RBF similarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[OutputType]:
                A sequence of similarity scores corresponding to each pair.
        """
        try:
            # Use list comprehension to compute similarity for each pair
            return [self.similarity(x, y) for x, y in pairs]
        except Exception as e:
            logger.error("Error computing similarities", exc_info=e)
            raise

    def dissimilarity(self, x: InputType, y: InputType) -> OutputType:
        """
        Calculate the Gaussian RBF dissimilarity between two elements.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            OutputType:
                A float representing the dissimilarity between x and y,
                ranging between 0 and 1.
        """
        try:
            # Dissimilarity is 1 - similarity
            return 1.0 - self.similarity(x, y)
        except Exception as e:
            logger.error("Error computing dissimilarity", exc_info=e)
            raise

    def dissimilarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[OutputType]:
        """
        Calculate Gaussian RBF dissimilarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[OutputType]:
                A sequence of dissimilarity scores corresponding to each pair.
        """
        try:
            # Use list comprehension to compute dissimilarity for each pair
            return [self.dissimilarity(x, y) for x, y in pairs]
        except Exception as e:
            logger.error("Error computing dissimilarities", exc_info=e)
            raise
