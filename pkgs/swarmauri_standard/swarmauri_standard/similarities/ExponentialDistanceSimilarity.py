from typing import Any, Sequence, Tuple, TypeVar, Union, Callable
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, bytes, Any)
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_type(SimilarityBase, "ExponentialDistanceSimilarity")
class ExponentialDistanceSimilarity(SimilarityBase):
    """
    Exponential distance similarity implementation.

    This class provides an exponential decay similarity measure based on arbitrary distance metrics.
    The similarity between two elements is calculated as exp(-distance), where distance is computed using
    a provided distance function.

    Attributes:
        distance_function: Callable[[InputType, InputType], float]
            A function that computes the distance between two elements
    """
    
    type: Literal["ExponentialDistanceSimilarity"] = "ExponentialDistanceSimilarity"
    resource: str = ResourceTypes.SIMILARITY.value

    def __init__(self, distance_function: Callable[[InputType, InputType], float]):
        """
        Initialize the ExponentialDistanceSimilarity instance.

        Args:
            distance_function: Callable[[InputType, InputType], float]
                A function that computes the distance between two elements of type InputType
        """
        super().__init__()
        if distance_function is None:
            raise ValueError("distance_function must be provided")
        if not callable(distance_function):
            raise TypeError("distance_function must be callable")
        self.distance_function = distance_function
        logger.debug("Initialized ExponentialDistanceSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the similarity between two elements using exponential decay of distance.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            float:
                A float representing the similarity between x and y, computed as exp(-distance(x, y))
        """
        logger.debug(f"Calculating similarity between {x} and {y}")
        distance = self.distance_function(x, y)
        similarity = float(__import__("math").exp(-distance))
        logger.debug(f"Similarity: {similarity}")
        return similarity

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate similarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[float]:
                A sequence of similarity scores corresponding to each pair
        """
        logger.debug(f"Calculating similarities for {len(pairs)} pairs")
        results = []
        for x, y in pairs:
            results.append(self.similarity(x, y))
        logger.debug(f"Similarities calculated: {results}")
        return results

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the dissimilarity between two elements.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            float:
                A float representing the dissimilarity between x and y, computed as 1 - similarity(x, y)
        """
        logger.debug(f"Calculating dissimilarity between {x} and {y}")
        similarity = self.similarity(x, y)
        dissimilarity = 1.0 - similarity
        logger.debug(f"Dissimilarity: {dissimilarity}")
        return dissimilarity

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate dissimilarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[float]:
                A sequence of dissimilarity scores corresponding to each pair
        """
        logger.debug(f"Calculating dissimilarities for {len(pairs)} pairs")
        results = []
        for x, y in pairs:
            results.append(self.dissimilarity(x, y))
        logger.debug(f"Dissimilarities calculated: {results}")
        return results