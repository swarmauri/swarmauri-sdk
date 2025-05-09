from abc import ABC, abstractmethod
from typing import Any, Tuple, TypeVar, Union
import logging

from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', int, float, bool, slice, Tuple[Union[int, slice], ...])
S = TypeVar('S', int, float, bool, str)


class MatrixBase(IMatrix, ABC):
    """
    Base class for matrix operations providing concrete implementations of abstract
    methods from IMatrix interface. This class serves as a foundation for specific
    matrix implementations and should not be used directly.

    Subclasses must implement all methods marked as abstract or provide specific
    implementations tailored to their matrix representation.
    """

    def __init__(self, shape: Tuple[int, int]):
        """
        Initialize the base matrix with the specified shape.

        Args:
            shape: Tuple[int, int]
                The dimensions of the matrix (rows, columns)
        """
        super().__init__(shape)
        logger.debug(f"MatrixBase initialized with shape {shape}")

    @property
    def dtype(self) -> type:
        """
        Get the data type of the elements in the matrix.

        Returns:
            type: The data type of the elements

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("dtype must be implemented by subclass")

    def get_row(self, index: int) -> IMatrix:
        """
        Get a row from the matrix as an IVector.

        Args:
            index: int
                The row index to retrieve

        Returns:
            IVector: The specified row as an IVector

        Raises:
            NotImplementedError: Method must be implemented by subclass
            IndexError: If the index is out of bounds
        """
        raise NotImplementedError("get_row must be implemented by subclass")

    def get_column(self, index: int) -> IMatrix:
        """
        Get a column from the matrix as an IVector.

        Args:
            index: int
                The column index to retrieve

        Returns:
            IVector: The specified column as an IVector

        Raises:
            NotImplementedError: Method must be implemented by subclass
            IndexError: If the index is out of bounds
        """
        raise NotImplementedError("get_column must be implemented by subclass")

    def reshape(self, new_shape: Tuple[int, int]) -> 'IMatrix':
        """
        Reshape the matrix to the specified dimensions.

        Args:
            new_shape: Tuple[int, int]
                The new dimensions (rows, columns)

        Returns:
            IMatrix: The reshaped matrix

        Raises:
            NotImplementedError: Method must be implemented by subclass
            ValueError: If the new shape is incompatible with the data
        """
        raise NotImplementedError("reshape must be implemented by subclass")

    def __getitem__(self, index: T) -> Union['IMatrix', IMatrix, S]:
        """
        Get an element, row, or column from the matrix.

        Args:
            index: T
                The index or slice to retrieve

        Returns:
            Union['IMatrix', IMatrix, S]: 
                - If index is a tuple of slices: Returns a submatrix
                - If index is an integer: Returns the specified row as an IVector
                - If index is a slice: Returns a slice of rows as an IMatrix

        Raises:
            NotImplementedError: Method must be implemented by subclass
            IndexError: If the index is out of bounds
            TypeError: If the index type is not supported
        """
        raise NotImplementedError(" __getitem__ must be implemented by subclass")

    def __setitem__(self, index: T, value: Union['IMatrix', IMatrix, S]) -> None:
        """
        Set an element, row, or column in the matrix.

        Args:
            index: T
                The index or slice to set
            value: Union['IMatrix', IMatrix, S]
                The value to set

        Raises:
            NotImplementedError: Method must be implemented by subclass
            IndexError: If the index is out of bounds
            TypeError: If the value type is not compatible
        """
        raise NotImplementedError(" __setitem__ must be implemented by subclass")

    def tolist(self) -> list:
        """
        Convert the matrix to a list of lists.

        Returns:
            list: A list of lists representing the matrix

        Raises:
            NotImplementedError: Method must be implemented by subclass
        """
        raise NotImplementedError(" tolist must be implemented by subclass")

    def __add__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Element-wise addition of two matrices.

        Args:
            other: IMatrix
                The matrix to add

        Returns:
            IMatrix: The result of the addition

        Raises:
            NotImplementedError: Method must be implemented by subclass
            ValueError: If the matrices have different shapes
        """
        raise NotImplementedError(" __add__ must be implemented by subclass")

    def __sub__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Element-wise subtraction of two matrices.

        Args:
            other: IMatrix
                The matrix to subtract

        Returns:
            IMatrix: The result of the subtraction

        Raises:
            NotImplementedError: Method must be implemented by subclass
            ValueError: If the matrices have different shapes
        """
        raise NotImplementedError(" __sub__ must be implemented by subclass")

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
            NotImplementedError: Method must be implemented by subclass
            ValueError: If the shapes are incompatible for multiplication
            TypeError: If the multiplication type is not supported
        """
        raise NotImplementedError(" __mul__ must be implemented by subclass")

    def __str__(self) -> str:
        """
        Get a string representation of the matrix.

        Returns:
            str: A string representation of the matrix

        Raises:
            NotImplementedError: Method must be implemented by subclass
        """
        raise NotImplementedError(" __str__ must be implemented by subclass")