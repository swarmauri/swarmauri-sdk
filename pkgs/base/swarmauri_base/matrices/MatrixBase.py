from abc import ABC, abstractmethod
from typing import Union, Tuple, List, Optional, Any
import logging

from swarmauri_core.matrices.IMatrix import IMatrix


logger = logging.getLogger(__name__)


class MatrixBase(IMatrix, ABC):
    """
    Base implementation for matrix operations. This class provides a basic 
    structure for implementing matrix functionality, including element-wise 
    operations and matrix transformations.
    
    Attributes:
        shape (Tuple[int, int]): The shape of the matrix (rows, columns)
        dtype (type): The data type of the elements in the matrix
        
    Methods:
        __getitem__: Gets elements using row and column indices or slices
        __setitem__: Sets elements using row and column indices or slices
        shape: Returns the shape of the matrix
        reshape: Reshapes the matrix to a new shape
        tolist: Converts the matrix to a list of lists
        __add__: Element-wise addition with another matrix
        __sub__: Element-wise subtraction with another matrix
        __mul__: Element-wise multiplication with another matrix
        __truediv__: Element-wise division with another matrix
    """
    
    def __init__(self):
        super().__init__()
        logger.debug("Initialized MatrixBase")

    def __getitem__(self, index: Union[Tuple[int, int], Tuple[slice, slice], int, slice]) -> Union[float, IMatrix, List[List[float]]]:
        """
        Gets elements using row and column indices or slices.
        
        Args:
            index: Tuple of indices or slices for row and column access
            
        Returns:
            Either a single element, a row vector, or a submatrix based on the index
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug(f"Getting item with index {index}")
        raise NotImplementedError("Method not implemented in base class")

    def __setitem__(self, index: Union[Tuple[int, int], Tuple[slice, slice], int, slice], value: Union[float, IMatrix, List[List[float]]]):
        """
        Sets elements using row and column indices or slices.
        
        Args:
            index: Tuple of indices or slices for row and column access
            value: Value or values to set at the specified index
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug(f"Setting item at index {index} with value {value}")
        raise NotImplementedError("Method not implemented in base class")

    def shape(self) -> Tuple[int, int]:
        """
        Returns the shape of the matrix as a tuple (rows, columns)
        
        Returns:
            Tuple[int, int]: Shape of the matrix
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug("Getting matrix shape")
        raise NotImplementedError("Method not implemented in base class")

    def reshape(self, new_shape: Tuple[int, int]) -> 'IMatrix':
        """
        Reshapes the matrix to a new shape.
        
        Args:
            new_shape: New shape as a tuple (new_rows, new_cols)
        
        Returns:
            Reshaped matrix
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug(f"Reshaping matrix to {new_shape}")
        raise NotImplementedError("Method not implemented in base class")

    def dtype(self) -> type:
        """
        Returns the data type of the elements in the matrix
        
        Returns:
            type: Data type of the matrix elements
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug("Getting matrix dtype")
        raise NotImplementedError("Method not implemented in base class")

    def tolist(self) -> List[List[float]]:
        """
        Converts the matrix to a list of lists of floats
        
        Returns:
            List[List[float]]: Matrix as a list of lists
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug("Converting matrix to list")
        raise NotImplementedError("Method not implemented in base class")

    def __add__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Element-wise addition with another matrix
        
        Args:
            other: Another matrix to add
            
        Returns:
            Resulting matrix after addition
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug("Performing matrix addition")
        if not isinstance(other, IMatrix):
            raise TypeError("Can only add another IMatrix instance")
        if self.shape() != other.shape():
            raise ValueError("Matrices must have the same shape for addition")
        raise NotImplementedError("Method not implemented in base class")

    def __sub__(self, other: 'IMatrix') -> 'IMatrix':
        """
        Element-wise subtraction with another matrix
        
        Args:
            other: Another matrix to subtract
            
        Returns:
            Resulting matrix after subtraction
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug("Performing matrix subtraction")
        if not isinstance(other, IMatrix):
            raise TypeError("Can only subtract another IMatrix instance")
        if self.shape() != other.shape():
            raise ValueError("Matrices must have the same shape for subtraction")
        raise NotImplementedError("Method not implemented in base class")

    def __mul__(self, other: Union[float, int, 'IMatrix']) -> 'IMatrix':
        """
        Element-wise multiplication with another matrix or scalar
        
        Args:
            other: Either a scalar or another matrix to multiply
            
        Returns:
            Resulting matrix after multiplication
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug(f"Performing matrix multiplication with {other}")
        if isinstance(other, IMatrix):
            if self.shape()[1] != other.shape()[0]:
                raise ValueError("Incompatible shapes for matrix multiplication")
        elif not isinstance(other, (float, int)):
            raise TypeError("Can only multiply by a scalar or another IMatrix")
        raise NotImplementedError("Method not implemented in base class")

    def __truediv__(self, other: Union[float, int, 'IMatrix']) -> 'IMatrix':
        """
        Element-wise division with another matrix or scalar
        
        Args:
            other: Either a scalar or another matrix to divide by
            
        Returns:
            Resulting matrix after division
            
        Raises:
            NotImplementedError: Always raised as this is a base implementation
        """
        logger.debug(f"Performing matrix division by {other}")
        if isinstance(other, IMatrix):
            if self.shape() != other.shape():
                raise ValueError("Matrices must have the same shape for division")
        elif not isinstance(other, (float, int)):
            raise TypeError("Can only divide by a scalar or another IMatrix")
        raise NotImplementedError("Method not implemented in base class")

    def __str__(self) -> str:
        """
        Returns a string representation of the matrix
        
        Returns:
            str: String representation of the matrix
        """
        return f"MatrixBase(shape={self.shape()}, dtype={self.dtype()})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the matrix
        
        Returns:
            str: Official string representation
        """
        return self.__str__()