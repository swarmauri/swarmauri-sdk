from abc import ABC, abstractmethod
from typing import Tuple, Union, List
import logging

from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


class ITensor(ABC):
    """
    Core interface for tensor operations. This class provides the foundation for
    implementing various tensor operations, including element-wise access,
    slicing, reshaping, and basic tensor transformations.

    Attributes:
        shape (Tuple[int, ...]): The shape of the tensor
        dtype (type): The data type of the elements in the tensor

    Methods:
        __getitem__: Gets elements using tensor indices or slices
        __setitem__: Sets elements using tensor indices or slices
        shape: Returns the shape of the tensor
        reshape: Reshapes the tensor to a new shape
        dtype: Returns the data type of the tensor elements
        tolist: Converts the tensor to a list of lists (if 2D) or nested lists
        __add__: Element-wise addition with another tensor or scalar
        __sub__: Element-wise subtraction with another tensor or scalar
        __mul__: Element-wise multiplication with another tensor or scalar
        __truediv__: Element-wise division with another tensor or scalar
        transpose: Transposes the tensor
        broadcast: Broadcasts the tensor to a new shape
    """

    def __init__(self):
        super().__init__()
        logger.debug("Initialized ITensor")

    @abstractmethod
    def shape(self) -> Tuple[int, ...]:
        """
        Returns the shape of the tensor as a tuple of integers.
        
        Returns:
            Tuple[int, ...]: Shape of the tensor
        """
        logger.debug("Getting tensor shape")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def reshape(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Reshapes the tensor to a new shape.
        
        Args:
            new_shape: New shape as a tuple of integers
            
        Returns:
            Reshaped tensor
        """
        logger.debug(f"Reshaping tensor to {new_shape}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def dtype(self) -> type:
        """
        Returns the data type of the elements in the tensor.
        
        Returns:
            type: Data type of the tensor elements
        """
        logger.debug("Getting tensor dtype")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def __getitem__(self, index: Union[Tuple[int, ...], Tuple[slice, ...], int, slice]) -> Union[float, IVector, 'ITensor']:
        """
        Gets elements using tensor indices or slices.
        
        Args:
            index: Tuple of indices or slices for multi-dimensional access
            
        Returns:
            Either a single element, a vector, or a subtensor based on the index
        """
        logger.debug(f"Getting item with index {index}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def __setitem__(self, index: Union[Tuple[int, ...], Tuple[slice, ...], int, slice], value: Union[float, IVector, 'ITensor']):
        """
        Sets elements using tensor indices or slices.
        
        Args:
            index: Tuple of indices or slices for multi-dimensional access
            value: Value or values to set at the specified index
        """
        logger.debug(f"Setting item at index {index} with value {value}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def tolist(self) -> Union[List[float], List[List[float]], ...]:
        """
        Converts the tensor to a nested list structure.
        
        Returns:
            Union[List[float], List[List[float]], ...]: Tensor as a nested list
        """
        logger.debug("Converting tensor to list")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def __add__(self, other: Union[float, int, 'ITensor']) -> 'ITensor':
        """
        Element-wise addition with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to add
            
        Returns:
            Resulting tensor after addition
        """
        logger.debug(f"Performing tensor addition with {other}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def __sub__(self, other: Union[float, int, 'ITensor']) -> 'ITensor':
        """
        Element-wise subtraction with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to subtract
            
        Returns:
            Resulting tensor after subtraction
        """
        logger.debug(f"Performing tensor subtraction with {other}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def __mul__(self, other: Union[float, int, 'ITensor']) -> 'ITensor':
        """
        Element-wise multiplication with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to multiply
            
        Returns:
            Resulting tensor after multiplication
        """
        logger.debug(f"Performing tensor multiplication with {other}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def __truediv__(self, other: Union[float, int, 'ITensor']) -> 'ITensor':
        """
        Element-wise division with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to divide by
            
        Returns:
            Resulting tensor after division
        """
        logger.debug(f"Performing tensor division by {other}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def transpose(self) -> 'ITensor':
        """
        Transposes the tensor.
        
        Returns:
            Transposed tensor
        """
        logger.debug("Transposing tensor")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def broadcast(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Broadcasts the tensor to a new shape.
        
        Args:
            new_shape: New shape as a tuple of integers
            
        Returns:
            Broadcasted tensor
        """
        logger.debug(f"Broadcasting tensor to {new_shape}")
        raise NotImplementedError("Method not implemented")

    def __str__(self) -> str:
        """
        Returns a string representation of the tensor.
        
        Returns:
            str: String representation of the tensor
        """
        return f"ITensor(shape={self.shape()}, dtype={self.dtype()})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the tensor.
        
        Returns:
            str: Official string representation
        """
        return self.__str__()