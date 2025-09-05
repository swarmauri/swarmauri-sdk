from abc import ABC, abstractmethod
from typing import List, Tuple, Callable, Sequence, Union, TypeVar
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Set up logger
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T", bound=Union[float, int])
VectorLike = Union[IVector, List[T], Tuple[T, ...]]
MatrixLike = Union[IMatrix, List[List[T]], Tuple[Tuple[T, ...], ...]]
SequenceLike = Union[Sequence[T], str]
ComparableType = Union[VectorLike, MatrixLike, SequenceLike, Callable]


class ISimilarity(ABC):
    """
    Interface for abstract similarity measures.

    This interface defines methods for computing similarity and dissimilarity
    between various data types including vectors, matrices, sequences, and
    callable objects. It supports both direction-based and bounded comparisons.

    Similarity measures quantify how alike two objects are, with higher values
    indicating greater similarity. Dissimilarity measures represent the opposite.
    """

    @abstractmethod
    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the similarity between two objects.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        float
            Similarity score between x and y

        Raises
        ------
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        pass

    @abstractmethod
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
            If any objects are incomparable or have incompatible dimensions
        TypeError
            If any input types are not supported
        """
        pass

    @abstractmethod
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
            Dissimilarity score between x and y

        Raises
        ------
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        pass

    @abstractmethod
    def dissimilarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate dissimilarities between one object and multiple other objects.

        Parameters
        ----------
        x : ComparableType
            Reference object
        ys : Sequence[ComparableType]
            Sequence of objects to compare against the reference

        Returns
        -------
        List[float]
            List of dissimilarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any objects are incomparable or have incompatible dimensions
        TypeError
            If any input types are not supported
        """
        pass

    @abstractmethod
    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        A bounded similarity measure has values within a fixed range,
        typically [0,1] for similarities.

        Returns
        -------
        bool
            True if the similarity measure is bounded, False otherwise
        """
        pass

    @abstractmethod
    def check_reflexivity(self, x: ComparableType) -> bool:
        """
        Check if the similarity measure is reflexive: s(x,x) = 1.

        Parameters
        ----------
        x : ComparableType
            Object to check reflexivity with

        Returns
        -------
        bool
            True if s(x,x) = 1, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        """
        pass

    @abstractmethod
    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the similarity measure is symmetric: s(x,y) = s(y,x).

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        bool
            True if s(x,y) = s(y,x), False otherwise

        Raises
        ------
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        pass

    @abstractmethod
    def check_identity_of_discernibles(
        self, x: ComparableType, y: ComparableType
    ) -> bool:
        """
        Check if the similarity measure satisfies the identity of discernibles: s(x,y) = 1 ⟺ x = y.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        bool
            True if the identity of discernibles property holds, False otherwise

        Raises
        ------
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        pass
