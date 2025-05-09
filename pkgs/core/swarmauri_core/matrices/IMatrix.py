from abc import ABC, abstractmethod
from typing import Tuple, Any, Union
import logging
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


class IMatrix(ABC):
    """
    Interface for a matrix data structure. This interface defines the basic operations
    and properties for working with matrices in various applications, such as linear
    algebra, machine learning, and data processing.

    All implementing classes must provide the functionality for matrix operations,
    indexing, shape manipulation, and data type handling.
    """

    def __init__(self):
        super().__init__()

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Gets the shape of the matrix as a tuple (rows, columns).
        
        Returns:
            Tuple[int, int]: The dimensions of the matrix
        """
        raise NotImplementedError("shape property must be implemented")

    @property
    def dtype(self) -> type:
        """
        Gets the data type of the elements in the matrix.
        
        Returns:
            type: The data type of the matrix elements
        """
        raise NotImplementedError("dtype property must be implemented")

    @property
    def row(self) -> IVector:
        """
        Gets a specific row from the matrix as an IVector.
        
        Returns:
            IVector: The row as a vector
        """
        raise NotImplementedError("row property must be implemented")

    @property
    def column(self) -> IVector:
        """
        Gets a specific column from the matrix as an IVector.
        
        Returns:
            IVector: The column as a vector
        """
        raise NotImplementedError("column property must be implemented")

    def reshape(self, new_shape: Tuple[int, int]) -> 'IMatrix':
        """
        Reshapes the matrix to the specified shape.
        
        Args:
            new_shape: Tuple[int, int]
                The new dimensions (rows, columns) for the matrix
        
        Returns:
            IMatrix: The reshaped matrix
        """
        raise NotImplementedError("reshape method must be implemented")

    def tolist(self) -> list:
        """
        Converts the matrix to a list of lists.
        
        Returns:
            list: A 2D list representation of the matrix
        """
        raise NotImplementedError("tolist method must be implemented")

    def __getitem__(self, indices: Union[int, slice, Tuple[int, int]]) -> Union[float, IVector, 'IMatrix']:
        """
        Gets an element, row, column, or submatrix from the matrix using numpy-like indexing.
        
        Args:
            indices: Union[int, slice, Tuple[int, int]]
                The indices to access the elements. Can be a single integer,
                slice, or tuple of integers and slices for 2D access.
        
        Returns:
            Union[float, IVector, IMatrix]: The accessed element(s)
        """
        raise NotImplementedError("__getitem__ method must be implemented")

    def __setitem__(self, indices: Union[int, slice, Tuple[int, int]], value: Union[float, IVector, 'IMatrix']):
        """
        Sets an element, row, column, or submatrix in the matrix using numpy-like indexing.
        
        Args:
            indices: Union[int, slice, Tuple[int, int]]
                The indices where the value(s) will be set
            value: Union[float, IVector, IMatrix]
                The value(s) to be set in the matrix
        """
        raise NotImplementedError("__setitem__ method must be implemented")

    def __add__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Performs element-wise addition with another matrix.
        
        Args:
            other: IMatrix
                The matrix to add element-wise
        
        Returns:
            IMatrix: The resulting matrix after addition
        """
        raise NotImplementedError("__add__ method must be implemented")

    def __sub__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Performs element-wise subtraction with another matrix.
        
        Args:
            other: IMatrix
                The matrix to subtract element-wise
        
        Returns:
            IMatrix: The resulting matrix after subtraction
        """
        raise NotImplementedError("__sub__ method must be implemented")

    def __mul__(self, other: Union[float, IVector, 'IMatrix']) -> Union['IMatrix', IVector, float]:
        """
        Performs multiplication with a scalar, vector, or matrix.
        
        Args:
            other: Union[float, IVector, IMatrix]
                The scalar, vector, or matrix to multiply with
        
        Returns:
            Union[IMatrix, IVector, float]: The result of the multiplication
        """
        raise NotImplementedError("__mul__ method must be implemented")

    def __matmul__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Performs matrix multiplication with another matrix.
        
        Args:
            other: IMatrix
                The matrix to multiply with
        
        Returns:
            IMatrix: The resulting matrix after multiplication
        """
        raise NotImplementedError("__matmul__ method must be implemented")

    def __truediv__(self, other: Union[float, IVector, 'IMatrix']) -> Union['IMatrix', IVector, float]:
        """
        Performs element-wise division by a scalar, vector, or matrix.
        
        Args:
            other: Union[float, IVector, IMatrix]
                The scalar, vector, or matrix to divide by
        
        Returns:
            Union[IMatrix, IVector, float]: The result of the division
        """
        raise NotImplementedError("__truediv__ method must be implemented")

    def __str__(self) -> str:
        """
        Returns a string representation of the matrix.
        
        Returns:
            str: The string representation of the matrix
        """
        raise NotImplementedError("__str__ method must be implemented")

    def __repr__(self) -> str:
        """
        Returns the official string representation of the matrix.
        
        Returns:
            str: The official string representation
        """
        return f"<{self.__class__.__name__} shape={self.shape} dtype={self.dtype}>"