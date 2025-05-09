import logging
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.swarmauri_standard.similarities.SimilarityBase import SimilarityBase
from typing import Union, Sequence, Tuple, Any, Optional

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "GaussianRBFSimilarity")
class GaussianRBFSimilarity(SimilarityBase):
    """
    Implementation of the Gaussian RBF similarity measure.

    This class provides an implementation of the Radial Basis Function (RBF)
    kernel similarity, which measures the exponential decay of the squared Euclidean
    distance between two elements. The similarity score is calculated as:

        s(a, b) = exp(-gamma * ||a - b||^2)

    where gamma is a positive parameter that controls the width of the RBF kernel.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        gamma: float
            The width parameter of the RBF kernel. Must be greater than 0.
    """
    type: Literal["GaussianRBFSimilarity"] = "GaussianRBFSimilarity"
    gamma: float

    def __init__(self, gamma: float = 1.0) -> None:
        """
        Initializes the GaussianRBFSimilarity instance.

        Args:
            gamma: float
                The width parameter of the RBF kernel. Must be greater than 0.

        Raises:
            ValueError:
                If gamma is not greater than 0.
        """
        if gamma <= 0:
            raise ValueError("Gamma must be greater than 0")
        self.gamma = gamma

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the Gaussian RBF similarity between two elements.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The similarity score between the two elements

        Raises:
            ValueError:
                If either element is None
        """
        if a is None or b is None:
            raise ValueError("Both elements must be non-None")

        # Compute squared Euclidean distance between a and b
        distance = np.linalg.norm(np.array(a) - np.array(b))
        squared_distance = distance ** 2

        # Compute RBF kernel
        similarity_score = np.exp(-self.gamma * squared_distance)

        logger.debug(f"Similarity score calculated: {similarity_score}")
        return similarity_score

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates Gaussian RBF similarity scores between one element and a list of elements.

        Args:
            a: Union[Any, None]
                The element to compare against multiple elements
            b_list: Sequence[Union[Any, None]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of similarity scores

        Raises:
            ValueError:
                If a is None or if any element in b_list is None
        """
        if a is None:
            raise ValueError("Element a must be non-None")
        if any(b is None for b in b_list):
            raise ValueError("All elements in b_list must be non-None")

        # Compute similarities for each element in b_list
        similarity_scores = tuple(
            self.similarity(a, b) for b in b_list
        )

        logger.debug(f"Similarity scores calculated: {similarity_scores}")
        return similarity_scores

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity score between two elements.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The dissimilarity score between the two elements
        """
        # Dissimilarity is 1 - similarity
        return 1.0 - self.similarity(a, b)

    def dissimilarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates dissimilarity scores between one element and a list of elements.

        Args:
            a: Union[Any, None]
                The element to compare against multiple elements
            b_list: Sequence[Union[Any, None]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores
        """
        # Dissimilarities are 1 - similarities
        return tuple(1.0 - score for score in self.similarities(a, b_list))

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        Returns:
            bool:
                True if the similarity measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        Returns:
            bool:
                True if the similarity measure is reflexive, False otherwise
        """
        return True

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        Returns:
            bool:
                True if the similarity measure is symmetric, False otherwise
        """
        return True

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        Returns:
            bool:
                True if the similarity measure satisfies identity, False otherwise
        """
        return True