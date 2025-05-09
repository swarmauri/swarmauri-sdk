from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional, Union, Literal
from swarmauri_core.vectors.IVector import IVector
import logging

logger = logging.getLogger(__name__)


class IMatrix(ABC):
    """
    Interface for matrix operations. This provides a blueprint for implementing
    matrix data structures with support for various operations, including
    indexing, slicing, shape manipulation, and matrix operations.

    The interface enforces type safety and provides a consistent API for
    different matrix implementations.
    """

    @abstractmethod
    def __getitem__(self, index: Union[Tuple[int, int], int, slice, tuple]) -> Union['IMatrix', IVector, Any]:
        """
        Get item from matrix using indexing or slicing.

        Args:
            index: Index or slice to access elements. Can be a tuple of integers,
                single integer, slice object, or a tuple of slices/ints.

        Returns:
            Union[IMatrix, IVector, Any]: The accessed element(s). Returns a
            new IMatrix if slicing returns a submatrix, an IVector if slicing
            returns a row/column vector, or the element itself for single index.

        Raises:
            IndexError: If index is out of bounds.
            ValueError: If slice step is invalid.
        """
        pass

    @abstractmethod
    def __setitem__(self, index: Union[Tuple[int, int], int, slice, tuple], value: Any) -> None:
        """
        Set item in matrix using indexing or slicing.

        Args:
            index: Index or slice to access elements. Can be a tuple of integers,
                single integer, slice object, or a tuple of slices/ints.
            value: Value to set at the specified index. Can be a single value,
                vector, or another matrix of compatible shape.

        Raises:
            IndexError: If index is out of bounds.
            ValueError: If value shape is incompatible with index.
        """
        pass

    @abstractmethod
    def __iter__(self) -> iter:
        """
        Return an iterator over the matrix rows.

        Yields:
            IVector: The next row vector in the matrix.
        """
        pass

    @abstractmethod
    def __add__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Matrix addition.

        Args:
            other: Another matrix of the same shape and compatible dtype.

        Returns:
            IMatrix: Result of element-wise addition.

        Raises:
            ValueError: If matrix shapes do not match.
            TypeError: If matrices have incompatible dtypes.
        """
        pass

    @abstractmethod
    def __sub__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Matrix subtraction.

        Args:
            other: Another matrix of the same shape and compatible dtype.

        Returns:
            IMatrix: Result of element-wise subtraction.

        Raises:
            ValueError: If matrix shapes do not match.
            TypeError: If matrices have incompatible dtypes.
        """
        pass

    @abstractmethod
    def __mul__(self, other: Union['IMatrix', Any]) -> Union['IMatrix', IVector]:
        """
        Matrix multiplication or element-wise multiplication.

        Args:
            other: Either another matrix for matrix multiplication or a scalar for
                element-wise multiplication.

        Returns:
            Union[IMatrix, IVector]: Result of multiplication. Returns an
            IMatrix for matrix multiplication, or an IVector if multiplying
            with a vector, or the element-wise result if multiplying with a scalar.

        Raises:
            ValueError: If matrix dimensions are incompatible for multiplication.
            TypeError: If other is of unsupported type.
        """
        pass

    @abstractmethod
    def __matmul__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Matrix multiplication (Python 3.5+ matrix multiplication operator).

        Args:
            other: Another matrix of compatible dimensions for multiplication.

        Returns:
            IMatrix: Result of matrix multiplication.

        Raises:
            ValueError: If number of columns in self does not match number of rows in other.
        """
        pass

    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """
        Get the shape of the matrix as (rows, columns).

        Returns:
            Tuple[int, int]: The shape of the matrix.
        """
        pass

    @abstractmethod
    def reshape(self, new_shape: Tuple[int, int]) -> 'IMatrix':
        """
        Reshape the matrix to new dimensions.

        Args:
            new_shape: Tuple[int, int] representing the new (rows, columns).

        Returns:
            IMatrix: The reshaped matrix.

        Raises:
            ValueError: If the total number of elements does not match.
        """
        pass

    @abstractmethod
    def dtype(self) -> type:
        """
        Get the data type of the matrix elements.

        Returns:
            type: The dtype of the matrix elements.
        """
        pass

    @abstractmethod
    def tolist(self) -> list:
        """
        Convert the matrix to a nested list representation.

        Returns:
            list: A list of lists, where each sublist represents a row of the matrix.
        """
        pass

    @abstractmethod
    def row(self, index: int) -> IVector:
        """
        Get a specific row as a vector.

        Args:
            index: The row index to access.

        Returns:
            IVector: The row vector at the specified index.

        Raises:
            IndexError: If index is out of bounds.
        """
        pass

    @abstractmethod
    def column(self, index: int) -> IVector:
        """
        Get a specific column as a vector.

        Args:
            index: The column index to access.

        Returns:
            IVector: The column vector at the specified index.

        Raises:
            IndexError: If index is out of bounds.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        Get the number of rows in the matrix.

        Returns:
            int: Number of rows.
        """
        pass

    @classmethod
    @abstractmethod
    def from_list(cls, data: list) -> 'IMatrix':
        """
        Create a matrix from a nested list.

        Args:
            data: A list of lists, where each sublist is a row of the matrix.

        Returns:
            IMatrix: The constructed matrix.

        Raises:
            ValueError: If the input data is invalid or inconsistent.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        String representation of the matrix.

        Returns:
            str: A string representation of the matrix elements.
        """
        pass

    pass