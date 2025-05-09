import numpy as np
import logging
from typing import Union, List
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class HellingerAffinitySimilarity(SimilarityBase):
    """
    Computes the Hellinger Affinity Similarity between two discrete probability distributions.

    The Hellinger Affinity Similarity is based on the Hellinger distance, which is a measure
    of the difference between two probability distributions. The similarity is computed as
    1 minus the Hellinger distance, providing a value between 0 and 1 where higher values
    indicate greater similarity.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    resource: str = "SIMILARITY"

    def __init__(self):
        super().__init__()

    def similarity(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]], 
        y: Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> float:
        """
        Computes the similarity between two probability distributions.

        Args:
            x: First probability distribution.
            y: Second probability distribution.

        Returns:
            float: Similarity score between x and y, ranging from 0 to 1.

        Raises:
            ValueError: If x or y are not valid probability vectors.
        """
        x = np.asarray(x)
        y = np.asarray(y)
        
        if not self._is_valid_probability_vector(x):
            raise ValueError("Invalid probability vector x.")
        if not self._is_valid_probability_vector(y):
            raise ValueError("Invalid probability vector y.")
        
        sqrt_x = np.sqrt(x)
        sqrt_y = np.sqrt(y)
        diff = sqrt_x - sqrt_y
        h = np.sqrt(0.5 * np.sum(diff ** 2))
        
        return 1.0 - h

    def similarities(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]],
        ys: Union[List[Union[np.ndarray, List[float], Tuple[float, ...]]], Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> Union[float, List[float]]:
        """
        Computes similarities between a base distribution and one or more distributions.

        Args:
            x: Base probability distribution.
            ys: Single or list of probability distributions to compare against.

        Returns:
            Union[float, List[float]]: Similarity scores between x and each distribution in ys.
        """
        if not isinstance(ys, list):
            ys = [ys]
        
        similarities = []
        for y in ys:
            similarities.append(self.similarity(x, y))
        
        return similarities if len(similarities) > 1 else similarities[0]

    def dissimilarity(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]],
        y: Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> float:
        """
        Computes the dissimilarity between two probability distributions.

        Args:
            x: First probability distribution.
            y: Second probability distribution.

        Returns:
            float: Dissimilarity score between x and y, ranging from 0 to 1.
        """
        x = np.asarray(x)
        y = np.asarray(y)
        
        if not self._is_valid_probability_vector(x):
            raise ValueError("Invalid probability vector x.")
        if not self._is_valid_probability_vector(y):
            raise ValueError("Invalid probability vector y.")
        
        sqrt_x = np.sqrt(x)
        sqrt_y = np.sqrt(y)
        diff = sqrt_x - sqrt_y
        h = np.sqrt(0.5 * np.sum(diff ** 2))
        
        return h

    def dissimilarities(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]],
        ys: Union[List[Union[np.ndarray, List[float], Tuple[float, ...]]], Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> Union[float, List[float]]:
        """
        Computes dissimilarities between a base distribution and one or more distributions.

        Args:
            x: Base probability distribution.
            ys: Single or list of probability distributions to compare against.

        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each distribution in ys.
        """
        if not isinstance(ys, list):
            ys = [ys]
        
        dissimilarities = []
        for y in ys:
            dissimilarities.append(self.dissimilarity(x, y))
        
        return dissimilarities if len(dissimilarities) > 1 else dissimilarities[0]

    def check_boundedness(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]],
        y: Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        A measure is reflexive if the similarity of any distribution with itself is 1.

        Args:
            x: Probability distribution to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        x = np.asarray(x)
        if not self._is_valid_probability_vector(x):
            raise ValueError("Invalid probability vector x.")
        return np.isclose(self.similarity(x, x), 1.0, atol=1e-8)

    def check_symmetry(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]],
        y: Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        A measure is symmetric if similarity(x, y) == similarity(y, x).

        Args:
            x: First probability distribution.
            y: Second probability distribution.

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        x = np.asarray(x)
        y = np.asarray(y)
        if not self._is_valid_probability_vector(x):
            raise ValueError("Invalid probability vector x.")
        if not self._is_valid_probability_vector(y):
            raise ValueError("Invalid probability vector y.")
        return np.isclose(self.similarity(x, y), self.similarity(y, x), atol=1e-8)

    def check_identity(
        self, 
        x: Union[np.ndarray, List[float], Tuple[float, ...]],
        y: Union[np.ndarray, List[float], Tuple[float, ...]]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        A measure satisfies identity if similarity(x, y) == 1 if and only if x == y.

        Args:
            x: First probability distribution.
            y: Second probability distribution.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        x = np.asarray(x)
        y = np.asarray(y)
        if not self._is_valid_probability_vector(x):
            raise ValueError("Invalid probability vector x.")
        if not self._is_valid_probability_vector(y):
            raise ValueError("Invalid probability vector y.")
        if np.array_equal(x, y):
            return np.isclose(self.similarity(x, y), 1.0, atol=1e-8)
        else:
            return self.similarity(x, y) < 1.0

    def _is_valid_probability_vector(self, vector: Union[np.ndarray, List[float], Tuple[float, ...]]) -> bool:
        """
        Checks if a vector is a valid probability vector.

        A valid probability vector must have all non-negative elements and sum to 1.

        Args:
            vector: Vector to validate.

        Returns:
            bool: True if the vector is valid, False otherwise.
        """
        vector = np.asarray(vector)
        if not np.all(vector >= 0):
            return False
        if not np.isclose(np.sum(vector), 1.0, atol=1e-8):
            return False
        return True