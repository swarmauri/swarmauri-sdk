from typing import Any, List, Tuple, Union, Iterator, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.matrices.IMatrix import IMatrix, T

# Set up logging
logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class MatrixBase(IMatrix[T], ComponentBase):
    """
    Base implementation for matrix operations.
    
    This class provides a concrete implementation of the IMatrix interface,
    serving as a base class for specific matrix implementations.
    It abstracts common matrix operations such as multiplication, transposition,
    and element access.
    """
    
    resource: Optional[str] = ResourceTypes.MATRICE.value
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Accessing matrix element at {key}")
        raise NotImplementedError("__getitem__ method must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Setting matrix element at {key} to {value}")
        raise NotImplementedError("__setitem__ method must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Performing matrix multiplication with {other}")
        raise NotImplementedError("__matmul__ method must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Getting row at index {row_index}")
        raise NotImplementedError("get_row method must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Getting column at index {col_index}")
        raise NotImplementedError("get_column method must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Setting row at index {row_index} to {values}")
        raise NotImplementedError("set_row method must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug(f"Setting column at index {col_index} to {values}")
        raise NotImplementedError("set_column method must be implemented by subclasses")
    
    def shape(self) -> Tuple[int, int]:
        """
        Get the dimensions of the matrix.
        
        Returns
        -------
        Tuple[int, int]
            A tuple containing the number of rows and columns (height, width).
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug("Getting matrix shape")
        raise NotImplementedError("shape method must be implemented by subclasses")
    
    def transpose(self) -> 'IMatrix[T]':
        """
        Transpose the matrix.
        
        Returns
        -------
        IMatrix[T]
            A new matrix that is the transpose of the current matrix.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug("Transposing matrix")
        raise NotImplementedError("transpose method must be implemented by subclasses")
    
    def __iter__(self) -> Iterator[List[T]]:
        """
        Iterate through the rows of the matrix.
        
        Returns
        -------
        Iterator[List[T]]
            An iterator that yields each row of the matrix.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug("Iterating through matrix rows")
        raise NotImplementedError("__iter__ method must be implemented by subclasses")
    
    def __len__(self) -> int:
        """
        Get the number of rows in the matrix.
        
        Returns
        -------
        int
            The number of rows in the matrix.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        logger.debug("Getting matrix length")
        raise NotImplementedError("__len__ method must be implemented by subclasses")