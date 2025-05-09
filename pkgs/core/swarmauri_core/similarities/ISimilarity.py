from abc import ABC, abstractmethod
from typing import Union, Any, Tuple, Callable, Literal
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class ISimilarity(ABC):
    """
    Abstract base class for implementing similarity measures. This interface
    provides a blueprint for creating concrete similarity implementations with
    support for various data types and mathematical properties.

    The interface enforces abstract methods for core similarity calculations
    and property checks, ensuring consistency and type safety across different
    implementations.
    """

    @abstractmethod
    def similarity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Calculate the similarity between two elements.

        Args:
            x: The first element to compare. Can be a vector, matrix, tuple, string, or callable.
            y: The second element to compare. Can be a vector, matrix, tuple, string, or callable.

        Returns:
            float: A measure of similarity between x and y.

        Raises:
            TypeError: If input types are not supported.
        """
        pass

    @abstractmethod
    def similarities(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        ys: Union[
            List[Union[IVector, IMatrix, Tuple, str, Callable]], 
            Union[IVector, IMatrix, Tuple, str, Callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Calculate similarities between an element and multiple elements.

        Args:
            x: The reference element to compare against. Can be a vector, matrix, tuple, string, or callable.
            ys: A list of elements or a single element to compare with x. Elements can be vectors, matrices, tuples, strings, or callables.

        Returns:
            Union[float, List[float]]: A measure of similarity (or similarities) between x and each element in ys.

        Raises:
            TypeError: If input types are not supported.
        """
        pass

    @abstractmethod
    def dissimilarity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Calculate the dissimilarity between two elements.

        Args:
            x: The first element to compare. Can be a vector, matrix, tuple, string, or callable.
            y: The second element to compare. Can be a vector, matrix, tuple, string, or callable.

        Returns:
            float: A measure of dissimilarity between x and y.

        Raises:
            TypeError: If input types are not supported.
        """
        pass

    @abstractmethod
    def dissimilarities(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        ys: Union[
            List[Union[IVector, IMatrix, Tuple, str, Callable]], 
            Union[IVector, IMatrix, Tuple, str, Callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Calculate dissimilarities between an element and multiple elements.

        Args:
            x: The reference element to compare against. Can be a vector, matrix, tuple, string, or callable.
            ys: A list of elements or a single element to compare with x. Elements can be vectors, matrices, tuples, strings, or callables.

        Returns:
            Union[float, List[float]]: A measure of dissimilarity (or dissimilarities) between x and each element in ys.

        Raises:
            TypeError: If input types are not supported.
        """
        pass

    @abstractmethod
    def check_boundedness(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is bounded.

        Args:
            x: The first element to compare. Can be a vector, matrix, tuple, string, or callable.
            y: The second element to compare. Can be a vector, matrix, tuple, string, or callable.

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        pass

    @abstractmethod
    def check_reflexivity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is reflexive (s(x,x) = 0).

        Args:
            x: The element to check reflexivity for. Can be a vector, matrix, tuple, string, or callable.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        pass

    @abstractmethod
    def check_symmetry(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure is symmetric (s(x,y) = s(y,x)).

        Args:
            x: The first element to compare. Can be a vector, matrix, tuple, string, or callable.
            y: The second element to compare. Can be a vector, matrix, tuple, string, or callable.

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        pass

    @abstractmethod
    def check_identity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Check if the similarity measure satisfies identity (s(x,y) = 1 if and only if x == y).

        Args:
            x: The first element to compare. Can be a vector, matrix, tuple, string, or callable.
            y: The second element to compare. Can be a vector, matrix, tuple, string, or callable.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        pass

    pass