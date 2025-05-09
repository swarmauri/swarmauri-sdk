from abc import ABC, abstractmethod
from typing import Any, Callable, Literal, TypeVar, Union
import logging
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
from typing import Sequence

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, Callable, IVector, IMatrix, Sequence)
OutputType = TypeVar('OutputType', float, bool)

class ISimilarity(ABC):
    """
    Abstract base class for implementing similarity measures.

    This interface provides a foundation for various similarity and dissimilarity 
    measures. It supports direction-based or bounded comparisons and includes 
    validation methods for different similarity properties.

    Classes implementing this interface should provide concrete implementations 
    for the similarity calculation methods while adhering to the defined interface.
    """

    def __init__(self):
        """
        Initialize the similarity measure.
        """
        self._is_bounded: bool | None = None
        logger.debug("Initialized ISimilarity instance")

    @property
    def is_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        Returns:
            bool: True if the similarity measure is bounded, False otherwise
        """
        if self._is_bounded is None:
            self._is_bounded = self.check_boundedness()
        return self._is_bounded

    @abstractmethod
    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the similarity between two elements.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            float:
                A float representing the similarity between x and y.
                If bounded, should be between 0 and 1.

        Raises:
            TypeError: If input types are not supported
        """
        raise NotImplementedError("similarity must be implemented by subclass")

    @abstractmethod
    def similarities(self, pairs: Sequence[tuple[InputType, InputType]]) -> list[float]:
        """
        Calculate similarities for multiple pairs of elements.

        Args:
            pairs: Sequence[tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            list[float]:
                A list of similarity scores corresponding to each pair.
        """
        raise NotImplementedError("similarities must be implemented by subclass")

    @abstractmethod
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
                A float representing the dissimilarity between x and y.
                If bounded, should be between 0 and 1.

        Raises:
            TypeError: If input types are not supported
        """
        raise NotImplementedError("dissimilarity must be implemented by subclass")

    @abstractmethod
    def dissimilarities(self, pairs: Sequence[tuple[InputType, InputType]]) -> list[float]:
        """
        Calculate dissimilarities for multiple pairs of elements.

        Args:
            pairs: Sequence[tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            list[float]:
                A list of dissimilarity scores corresponding to each pair.
        """
        raise NotImplementedError("dissimilarities must be implemented by subclass")

    def check_boundedness(self, pairs: Sequence[tuple[InputType, InputType]] = ()) -> bool:
        """
        Check if the similarity measure is bounded between 0 and 1.

        Args:
            pairs: Sequence[tuple[InputType, InputType]]
                Optional sequence of pairs to test boundedness

        Returns:
            bool:
                True if the similarity measure is bounded between 0 and 1,
                False otherwise
        """
        if not pairs:
            logger.warning("No pairs provided for boundedness check")
            return False
        
        all_bounded = all(0 <= self.similarity(x, y) <= 1 for x, y in pairs)
        logger.debug(f"Boundedness check result: {all_bounded}")
        return all_bounded

    def check_reflexivity(self, elements: Sequence[InputType] = ()) -> bool:
        """
        Check if the similarity measure is reflexive (s(x, x) = 1).

        Args:
            elements: Sequence[InputType]
                Optional sequence of elements to test reflexivity

        Returns:
            bool:
                True if the similarity measure is reflexive,
                False otherwise
        """
        if not elements:
            logger.warning("No elements provided for reflexivity check")
            return False
        
        all_reflexive = all(self.similarity(x, x) == 1 for x in elements)
        logger.debug(f"Reflexivity check result: {all_reflexive}")
        return all_reflexive

    def check_symmetry(self, pairs: Sequence[tuple[InputType, InputType]] = ()) -> bool:
        """
        Check if the similarity measure is symmetric (s(x, y) = s(y, x)).

        Args:
            pairs: Sequence[tuple[InputType, InputType]]
                Optional sequence of pairs to test symmetry

        Returns:
            bool:
                True if the similarity measure is symmetric,
                False otherwise
        """
        if not pairs:
            logger.warning("No pairs provided for symmetry check")
            return False
        
        all_symmetric = all(self.similarity(x, y) == self.similarity(y, x) for x, y in pairs)
        logger.debug(f"Symmetry check result: {all_symmetric}")
        return all_symmetric

    def check_identity(self, pairs: Sequence[tuple[InputType, InputType]] = ()) -> bool:
        """
        Check if the similarity measure satisfies identity (s(x, y) = 1 ⟺ x = y).

        Args:
            pairs: Sequence[tuple[InputType, InputType]]
                Optional sequence of pairs to test identity

        Returns:
            bool:
                True if the similarity measure satisfies identity,
                False otherwise
        """
        if not pairs:
            logger.warning("No pairs provided for identity check")
            return False
        
        all_identity = True
        for x, y in pairs:
            if x == y:
                if not self.similarity(x, y) == 1:
                    all_identity = False
                    break
            else:
                if self.similarity(x, y) == 1:
                    all_identity = False
                    break
        
        logger.debug(f"Identity check result: {all_identity}")
        return all_identity