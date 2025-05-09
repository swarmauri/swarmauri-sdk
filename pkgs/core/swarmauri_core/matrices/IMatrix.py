from abc import ABC, abstractmethod
from typing import Any, Tuple, TypeVar, Union
import logging

from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', int, float, bool, slice, Tuple[Union[int, slice], ...])
S = TypeVar('S', int, float, bool, str)

class IMatrix(ABC):
    """
    Interface for matrix operations. This class defines the core functionality 
    required for matrix operations including indexing, slicing, reshaping, and 
    basic matrix operations.

    This interface provides a foundation for working with 2D data structures 
    and linear algebra operations while remaining agnostic to the underlying 
    implementation.
    """

    def __init__(self, shape: Tuple[int, int]):
        """
        Initialize the matrix with the specified shape.

        Args:
            shape: Tuple[int, int]
                The dimensions of the matrix (rows, columns)
        """
        self._shape = shape
        logger.debug(f"Matrix initialized with shape {shape}")

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Get the shape of the matrix.

        Returns:
            Tuple[int, int]: The dimensions of the matrix (rows, columns)
        """
        return self._shape

    @property
    def dtype(self) -> type:
        """
        Get the data type of the elements in the matrix.

        Returns:
            type: The data type of the elements
        """
        raise NotImplementedError("dtype must be implemented by subclass")

    @abstractmethod
    def get_row(self, index: int) -> IVector:
        """
        Get a row from the matrix as an IVector.

        Args:
            index: int
                The row index to retrieve

        Returns:
            IVector: The specified row as an IVector

        Raises:
            IndexError: If the index is out of bounds
        """
        pass

    @abstractmethod
    def get_column(self, index: int) -> IVector:
        """
        Get a column from the matrix as an IVector.

        Args:
            index: int
                The column index to retrieve

        Returns:
            IVector: The specified column as an IVector

        Raises:
            IndexError: If the index is out of bounds
        """
        pass

    @abstractmethod
    def reshape(self, new_shape: Tuple[int, int]) -> 'IMatrix':
        """
        Reshape the matrix to the specified dimensions.

        Args:
            new_shape: Tuple[int, int]
                The new dimensions (rows, columns)

        Returns:
            IMatrix: The reshaped matrix

        Raises:
            ValueError: If the new shape is incompatible with the data
        """
        pass

    @abstractmethod
    def __getitem__(self, index: T) -> Union['IMatrix', IVector, S]:
        """
        Get an element, row, or column from the matrix.

        Args:
            index: T
                The index or slice to retrieve

        Returns:
            Union['IMatrix', IVector, S]: 
                - If index is a tuple of slices: Returns a submatrix
                - If index is an integer: Returns the specified row as an IVector
                - If index is a slice: Returns a slice of rows as an IMatrix

        Raises:
            IndexError: If the index is out of bounds
            TypeError: If the index type is not supported
        """
        pass

    @abstractmethod
    def __setitem__(self, index: T, value: Union['IMatrix', IVector, S]) -> None:
        """
        Set an element, row, or column in the matrix.

        Args:
            index: T
                The index or slice to set
            value: Union['IMatrix', IVector, S]
                The value to set

        Raises:
            IndexError: If the index is out of bounds
            TypeError: If the value type is not compatible
        """
        pass

    @abstractmethod
    def tolist(self) -> list:
        """
        Convert the matrix to a list of lists.

        Returns:
            list: A list of lists representing the matrix
        """
        pass

    @abstractmethod
    def __add__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Element-wise addition of two matrices.

        Args:
            other: IMatrix
                The matrix to add

        Returns:
            IMatrix: The result of the addition

        Raises:
            ValueError: If the matrices have different shapes
        """
        pass

    @abstractmethod
    def __sub__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Element-wise subtraction of two matrices.

        Args:
            other: IMatrix
                The matrix to subtract

        Returns:
            IMatrix: The result of the subtraction

        Raises:
            ValueError: If the matrices have different shapes
        """
        pass

    @abstractmethod
    def __mul__(self, other: Union['IMatrix', S]) -> 'IMatrix':
        """
        Element-wise multiplication or matrix multiplication.

        Args:
            other: Union['IMatrix', S]
                - If IMatrix: Performs matrix multiplication
                - If scalar: Performs element-wise multiplication

        Returns:
            IMatrix: The result of the multiplication

        Raises:
            ValueError: If the shapes are incompatible for multiplication
            TypeError: If the multiplication type is not supported
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Get a string representation of the matrix.

        Returns:
            str: A string representation of the matrix
        """
        pass