from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union, TypeVar, Generic, Iterator, Iterable, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class IMatrix(ABC, Generic[T]):
    """
    Interface abstraction for matrix operations.
    
    This interface defines the contract for linear operators and 2D structures,
    providing methods for matrix operations such as multiplication, row and column access.
    """
    
    @abstractmethod
    def __getitem__(self, key: Union[int, Tuple[int, int]]) -> Union[T, List[T]]:
        """
        Get an element or a row from the matrix.
        
        Parameters
        ----------
        key : Union[int, Tuple[int, int]]
            Index or tuple of indices for accessing the matrix elements.
            If key is an integer, return the entire row.
            If key is a tuple of integers, return the specific element.
        
        Returns
        -------
        Union[T, List[T]]
            The element or row at the specified position.
        
        Raises
        ------
        IndexError
            If the indices are out of bounds.
        """
        pass
    
    @abstractmethod
    def __setitem__(self, key: Union[int, Tuple[int, int]], value: Union[T, List[T]]) -> None:
        """
        Set an element or a row in the matrix.
        
        Parameters
        ----------
        key : Union[int, Tuple[int, int]]
            Index or tuple of indices for accessing the matrix elements.
            If key is an integer, set the entire row.
            If key is a tuple of integers, set the specific element.
        value : Union[T, List[T]]
            The value to set at the specified position.
        
        Raises
        ------
        IndexError
            If the indices are out of bounds.
        ValueError
            If the value type or dimensions don't match the matrix requirements.
        """
        pass
    
    @abstractmethod
    def __matmul__(self, other: 'IMatrix[T]') -> 'IMatrix[T]':
        """
        Perform matrix multiplication with another matrix.
        
        Parameters
        ----------
        other : IMatrix[T]
            The matrix to multiply with.
        
        Returns
        -------
        IMatrix[T]
            The result of the matrix multiplication.
        
        Raises
        ------
        ValueError
            If the matrices have incompatible dimensions for multiplication.
        """
        pass
    
    @abstractmethod
    def get_row(self, row_index: int) -> List[T]:
        """
        Get a specific row from the matrix.
        
        Parameters
        ----------
        row_index : int
            The index of the row to retrieve.
        
        Returns
        -------
        List[T]
            The row at the specified index.
        
        Raises
        ------
        IndexError
            If the row index is out of bounds.
        """
        pass
    
    @abstractmethod
    def get_column(self, col_index: int) -> List[T]:
        """
        Get a specific column from the matrix.
        
        Parameters
        ----------
        col_index : int
            The index of the column to retrieve.
        
        Returns
        -------
        List[T]
            The column at the specified index.
        
        Raises
        ------
        IndexError
            If the column index is out of bounds.
        """
        pass
    
    @abstractmethod
    def set_row(self, row_index: int, values: List[T]) -> None:
        """
        Set values for a specific row in the matrix.
        
        Parameters
        ----------
        row_index : int
            The index of the row to set.
        values : List[T]
            The values to set for the row.
        
        Raises
        ------
        IndexError
            If the row index is out of bounds.
        ValueError
            If the length of values doesn't match the matrix width.
        """
        pass
    
    @abstractmethod
    def set_column(self, col_index: int, values: List[T]) -> None:
        """
        Set values for a specific column in the matrix.
        
        Parameters
        ----------
        col_index : int
            The index of the column to set.
        values : List[T]
            The values to set for the column.
        
        Raises
        ------
        IndexError
            If the column index is out of bounds.
        ValueError
            If the length of values doesn't match the matrix height.
        """
        pass
    
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """
        Get the dimensions of the matrix.
        
        Returns
        -------
        Tuple[int, int]
            A tuple containing the number of rows and columns (height, width).
        """
        pass
    
    @abstractmethod
    def transpose(self) -> 'IMatrix[T]':
        """
        Transpose the matrix.
        
        Returns
        -------
        IMatrix[T]
            A new matrix that is the transpose of the current matrix.
        """
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator[List[T]]:
        """
        Iterate through the rows of the matrix.
        
        Returns
        -------
        Iterator[List[T]]
            An iterator that yields each row of the matrix.
        """
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """
        Get the number of rows in the matrix.
        
        Returns
        -------
        int
            The number of rows in the matrix.
        """
        pass