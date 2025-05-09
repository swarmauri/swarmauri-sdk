import logging
from abc import ABC, abstractmethod
from typing import Union, Sequence, Tuple, Any, Optional
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.swarmauri_standard.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "ExponentialDistanceSimilarity")
class ExponentialDistanceSimilarity(SimilarityBase):
    """
    Exponential distance similarity implementation.

    This class provides an exponentially decaying similarity measure based on the distance between elements.
    The similarity decreases exponentially as the distance between the elements increases.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        decay_coefficient: float
            Controls how quickly the similarity decays with distance. Higher values mean slower decay.
        resource: Optional[str] = "Similarity"
            Specifies the resource type for this component
    """
    type: Literal["ExponentialDistanceSimilarity"] = "ExponentialDistanceSimilarity"
    decay_coefficient: float
    resource: Optional[str] = "Similarity"

    def __init__(self, decay_coefficient: float = 1.0):
        """
        Initializes the ExponentialDistanceSimilarity instance.

        Args:
            decay_coefficient: float, optional
                Controls how quickly the similarity decays with distance. 
                Higher values mean slower decay (default is 1.0)
        """
        super().__init__()
        self.decay_coefficient = decay_coefficient

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the similarity between two elements using exponential decay of distance.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The similarity score between the two elements, 
                ranging from 0 (completely dissimilar) to 1 (identical)

        Raises:
            ValueError:
                If either a or b is None and cannot be processed
        """
        if a is None or b is None:
            logger.warning("None value encountered in similarity calculation")
            return 0.0

        distance = self._calculate_distance(a, b)
        similarity = self._exponential_decay(distance, self.decay_coefficient)
        return similarity

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates similarity scores between one element and a list of elements.

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
                If any element in b_list is None and cannot be processed
        """
        similarities = []
        for b in b_list:
            similarities.append(self.similarity(a, b))
        return tuple(similarities)

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity between two elements.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The dissimilarity score between the two elements

        Raises:
            ValueError:
                If either a or b is None and cannot be processed
        """
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

        Raises:
            ValueError:
                If any element in b_list is None and cannot be processed
        """
        return tuple(1.0 - s for s in self.similarities(a, b_list))

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure is bounded, False otherwise
        """
        return True  # Exponential similarity is always bounded between 0 and 1

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive, i.e., s(x, x) = 1.

        Args:
            a: Union[Any, None]
                The element to check reflexivity for

        Returns:
            bool:
                True if the similarity measure is reflexive, False otherwise
        """
        return self.similarity(a, a) == 1.0

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric, i.e., s(x, y) = s(y, x).

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure is symmetric, False otherwise
        """
        return self.similarity(a, b) == self.similarity(b, a)

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity, i.e., s(x, y) = 1
        if and only if x = y.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure satisfies identity, False otherwise
        """
        return a == b

    def _calculate_distance(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the distance between two elements.

        This method should be implemented by subclasses to provide the actual
        distance calculation logic.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The distance between the two elements

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("_calculate_distance method not implemented")
        raise NotImplementedError("_calculate_distance method must be implemented")

    def _exponential_decay(
            self, 
            distance: float, 
            decay_coefficient: float
    ) -> float:
        """
        Applies exponential decay to the distance.

        Args:
            distance: float
                The distance value to apply decay to
            decay_coefficient: float
                Controls how quickly the similarity decays with distance

        Returns:
            float:
                The similarity value after applying exponential decay
        """
        return float(exp(-decay_coefficient * distance))