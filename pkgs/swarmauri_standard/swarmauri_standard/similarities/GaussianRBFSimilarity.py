from typing import Union, List, Optional, Literal
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.similarities.ISimilarity import ISimilarity
import numpy as np
from scipy.spatial import distance
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class GaussianRBFSimilarity(ISimilarity, ComponentBase):
    """
    Implementation of the Gaussian RBF similarity measure.

    This class provides an implementation of the Gaussian Radial Basis Function (RBF)
    similarity measure. The similarity is calculated as the exponential of the negative
    squared Euclidean distance scaled by a gamma parameter.

    Attributes:
        gamma: Inverse kernel width parameter. Must be greater than 0.
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)
    gamma: float
    
    def __init__(self, gamma: float = 1.0):
        """
        Initialize the Gaussian RBF similarity measure.

        Args:
            gamma: Inverse kernel width parameter. Must be greater than 0.
                  Defaults to 1.0.
        """
        super().__init__()
        if gamma <= 0:
            raise ValueError("Gamma must be greater than 0")
        self.gamma = gamma
        logger.info("GaussianRBFSimilarity initialized with gamma = %s", self.gamma)

    def similarity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Calculate the Gaussian RBF similarity between two elements.

        Args:
            x: First element to compare.
            y: Second element to compare.

        Returns:
            float: Similarity score between x and y in the range [0, 1].

        Raises:
            ValueError: If inputs cannot be converted to numerical arrays.
        """
        try:
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            
            if x_arr.size == 1 and y_arr.size == 1:
                # Handle scalar inputs
                dist_sq = (x_arr.item() - y_arr.item()) ** 2
            else:
                # Calculate squared Euclidean distance between vectors
                dist_sq = distance.squared_euclidean(x_arr, y_arr)
            
            # Compute RBF similarity
            similarity = np.exp(-self.gamma * dist_sq)
            logger.debug("Similarity calculated: %s", similarity)
            return similarity.item()
            
        except Exception as e:
            logger.error("Error calculating similarity: %s", str(e))
            raise ValueError("Failed to calculate similarity") from e

    def similarities(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        ys: Union[
            List[Union[IVector, IMatrix, Tuple, str, Callable]], 
            Union[IVector, IMatrix, Tuple, str, Callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Calculate Gaussian RBF similarities between an element and multiple elements.

        Args:
            x: Reference element to compare against.
            ys: List of elements or single element to compare with x.

        Returns:
            Union[float, List[float]]: Similarity scores between x and each element in ys.

        Raises:
            ValueError: If inputs cannot be converted to numerical arrays.
        """
        try:
            # Handle single element case
            if not isinstance(ys, list):
                return self.similarity(x, ys)
            
            # Convert inputs to numpy arrays
            x_arr = np.asarray(x)
            ys_arr = [np.asarray(y) for y in ys]
            
            # Calculate pairwise squared distances
            dist_sq_matrix = distance.cdist([x_arr], ys_arr, metric='sqeuclidean')
            
            # Compute RBF similarities for all pairs
            similarities = np.exp(-self.gamma * dist_sq_matrix.flatten())
            logger.debug("Similarities calculated: %s", similarities)
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error("Error calculating similarities: %s", str(e))
            raise ValueError("Failed to calculate similarities") from e

    def dissimilarity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Calculate the dissimilarity using Gaussian RBF similarity.

        This is implemented as 1 - similarity(x, y) to convert the similarity
        measure to a dissimilarity measure.

        Args:
            x: First element to compare.
            y: Second element to compare.

        Returns:
            float: Dissimilarity score between x and y in the range [0, 1].
        """
        similarity = self.similarity(x, y)
        dissimilarity = 1.0 - similarity
        logger.debug("Dissimilarity calculated: %s", dissimilarity)
        return dissimilarity

    def dissimilarities(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        ys: Union[
            List[Union[IVector, IMatrix, Tuple, str, Callable]], 
            Union[IVector, IMatrix, Tuple, str, Callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Calculate Gaussian RBF dissimilarities between an element and multiple elements.

        This is implemented as 1 - similarities(x, ys) to convert the similarity
        measure to a dissimilarity measure.

        Args:
            x: Reference element to compare against.
            ys: List of elements or single element to compare with x.

        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each element in ys.
        """
        similarities = self.similarities(x, ys)
        if isinstance(similarities, float):
            return 1.0 - similarities
        else:
            return [1.0 - s for s in similarities]

    def check_boundedness(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is bounded.

        The Gaussian RBF similarity measure produces values in the range (0, 1],
        making it bounded.

        Args:
            x: First element to compare (unused in this check).
            y: Second element to compare (unused in this check).

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is reflexive.

        For any element x, the similarity with itself is 1, making it reflexive.

        Args:
            x: Element to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return True

    def check_symmetry(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is symmetric.

        The Gaussian RBF similarity measure is symmetric since it depends only
        on the squared distance between x and y.

        Args:
            x: First element to compare (unused in this check).
            y: Second element to compare (unused in this check).

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return True

    def check_identity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure satisfies identity.

        The measure satisfies identity if x == y implies similarity(x, y) = 1.

        Args:
            x: First element to compare.
            y: Second element to compare.

        Returns:
            bool: True if x and y are identical and similarity is 1, False otherwise.
        """
        return self.similarity(x, y) == 1.0