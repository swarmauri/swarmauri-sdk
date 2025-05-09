from abc import ABC, abstractmethod
from typing import Union, Sequence, Callable, Tuple, Any
import logging
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class ISimilarity(ABC):
    """
    Interface for similarity measures. This abstract base class defines the interface
    for implementing various similarity and dissimilarity measures. It includes methods
    for calculating similarities between different types of data (vectors, matrices,
    sequences, strings, callables) and provides checks for boundedness, reflexivity,
    symmetry, and identity properties.

    All implementing classes must provide concrete implementations of the abstract
    methods defined here.
    """

    @abstractmethod
    def similarity(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> float:
        """
        Calculates the similarity score between two elements.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compare
            b: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compare

        Returns:
            float:
                The similarity score between the two elements

        Raises:
            ValueError:
                If the elements are not of compatible types
            AttributeError:
                If the elements don't support the required operations
        """
        raise NotImplementedError("similarity method must be implemented")

    @abstractmethod
    def similarities(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b_list: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
    ) -> Tuple[float, ...]:
        """
        Calculates similarity scores between one element and a list of elements.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The element to compare against multiple elements
            b_list: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of similarity scores

        Raises:
            ValueError:
                If the elements are not of compatible types
            AttributeError:
                If the elements don't support the required operations
        """
        raise NotImplementedError("similarities method must be implemented")

    @abstractmethod
    def dissimilarity(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> float:
        """
        Calculates the dissimilarity score between two elements.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compare
            b: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compare

        Returns:
            float:
                The dissimilarity score between the two elements

        Raises:
            ValueError:
                If the elements are not of compatible types
            AttributeError:
                If the elements don't support the required operations
        """
        raise NotImplementedError("dissimilarity method must be implemented")

    @abstractmethod
    def dissimilarities(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b_list: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
    ) -> Tuple[float, ...]:
        """
        Calculates dissimilarity scores between one element and a list of elements.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The element to compare against multiple elements
            b_list: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores

        Raises:
            ValueError:
                If the elements are not of compatible types
            AttributeError:
                If the elements don't support the required operations
        """
        raise NotImplementedError("dissimilarities method must be implemented")

    @abstractmethod
    def check_boundedness(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compare
            b: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure is bounded, False otherwise
        """
        raise NotImplementedError("check_boundedness method must be implemented")

    @abstractmethod
    def check_reflexivity(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive, i.e., s(x, x) = 1.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The element to check reflexivity for

        Returns:
            bool:
                True if the similarity measure is reflexive, False otherwise
        """
        raise NotImplementedError("check_reflexivity method must be implemented")

    @abstractmethod
    def check_symmetry(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric, i.e., s(x, y) = s(y, x).

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compare
            b: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure is symmetric, False otherwise
        """
        raise NotImplementedError("check_symmetry method must be implemented")

    @abstractmethod
    def check_identity(
            self, 
            a: Union[IVector, IMatrix, Sequence, str, Callable], 
            b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity, i.e., s(x, y) = 1 if and only if x = y.

        Args:
            a: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compare
            b: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure satisfies identity, False otherwise
        """
        raise NotImplementedError("check_identity method must be implemented")