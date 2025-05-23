import logging
from math import exp
from typing import List, Literal, Sequence

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "GaussianRBFSimilarity")
class GaussianRBFSimilarity(SimilarityBase):
    """
    Gaussian Radial Basis Function (RBF) similarity measure.

    This similarity measure uses the Gaussian kernel to calculate similarity between vectors,
    where similarity decays exponentially with the squared Euclidean distance between points.

    The similarity is defined as: s(x,y) = exp(-gamma * ||x-y||^2)

    Attributes
    ----------
    type : Literal["GaussianRBFSimilarity"]
        Type identifier for the similarity measure
    gamma : float
        The scaling parameter for the squared distance (must be positive)
    """

    type: Literal["GaussianRBFSimilarity"] = "GaussianRBFSimilarity"
    gamma: float

    def __init__(self, gamma: float = 1.0, **kwargs):
        """
        Initialize the Gaussian RBF similarity measure.

        Parameters
        ----------
        gamma : float, default=1.0
            The scaling parameter for the squared distance. Higher values make the similarity
            more localized (decay faster with distance).

        Raises
        ------
        ValueError
            If gamma is not positive
        """
        if gamma <= 0:
            logger.error(f"Invalid gamma value: {gamma}. Gamma must be positive.")
            raise ValueError("Gamma must be positive")

        super().__init__(**kwargs, gamma=gamma)

        logger.debug(f"Initialized GaussianRBFSimilarity with gamma={gamma}")

    def _validate_inputs(self, x: ComparableType, y: ComparableType) -> tuple:
        """
        Validate and convert inputs to numpy arrays.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        tuple
            Tuple of numpy arrays (x_array, y_array)

        Raises
        ------
        TypeError
            If inputs cannot be converted to numpy arrays
        ValueError
            If inputs have incompatible dimensions
        """
        try:
            # Convert inputs to numpy arrays if they aren't already
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)

            # Ensure inputs have the same shape
            if x_array.shape != y_array.shape:
                raise ValueError(
                    f"Input shapes must match: got {x_array.shape} and {y_array.shape}"
                )

            return x_array, y_array

        except (TypeError, ValueError) as e:
            logger.error(f"Input validation error: {str(e)}")
            raise

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Gaussian RBF similarity between two objects.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        float
            Similarity score between x and y, in range [0, 1]

        Raises
        ------
        ValueError
            If the objects have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        try:
            x_array, y_array = self._validate_inputs(x, y)

            # Calculate squared Euclidean distance
            squared_distance = np.sum(np.square(x_array - y_array))

            # Apply RBF kernel formula: exp(-gamma * ||x-y||^2)
            similarity_value = exp(-self.gamma * squared_distance)

            logger.debug(
                f"Calculated similarity: {similarity_value} for inputs with squared distance: {squared_distance}"
            )
            return similarity_value

        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate similarities between one object and multiple other objects.

        Parameters
        ----------
        x : ComparableType
            Reference object
        ys : Sequence[ComparableType]
            Sequence of objects to compare against the reference

        Returns
        -------
        List[float]
            List of similarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any objects have incompatible dimensions
        TypeError
            If any input types are not supported
        """
        try:
            # Convert reference object to numpy array
            x_array = np.array(x, dtype=float)

            # Optimized vectorized implementation for numpy arrays
            if isinstance(ys, np.ndarray) and ys.ndim == 2:
                # Calculate squared distances efficiently
                squared_distances = np.sum(np.square(ys - x_array), axis=1)
                # Apply RBF kernel formula vectorized
                similarity_values = np.exp(-self.gamma * squared_distances)
                return similarity_values.tolist()
            else:
                # Fall back to default implementation for other sequences
                return [self.similarity(x, y) for y in ys]

        except Exception as e:
            logger.error(f"Error calculating similarities: {str(e)}")
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the dissimilarity between two objects.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        float
            Dissimilarity score between x and y, in range [0, 1]
        """
        try:
            # For bounded similarity in [0,1], dissimilarity is 1-similarity
            return 1.0 - self.similarity(x, y)
        except Exception as e:
            logger.error(f"Error calculating dissimilarity: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        The Gaussian RBF kernel always produces values in [0,1],
        with 1 for identical vectors and approaching 0 as distance increases.

        Returns
        -------
        bool
            True as this similarity measure is bounded in [0,1]
        """
        return True
