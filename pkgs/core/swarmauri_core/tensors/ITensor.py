from abc import ABC, abstractmethod
from typing import Any, Tuple, Union
import logging
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class ITensor(ABC):
    """
    Interface for an n-dimensional tensor. This interface defines the basic operations
    and properties for working with tensors in various applications, such as machine
    learning, linear algebra, and data processing.

    All implementing classes must provide the functionality for tensor operations,
    indexing, shape manipulation, and data type handling.
    """

    @property
    def shape(self) -> Tuple[int, ...]:
        """
        Gets the shape of the tensor as a tuple of integers.
        
        Returns:
            Tuple[int, ...]: The dimensions of the tensor
        """
        raise NotImplementedError("shape property must be implemented")

    @property
    def dtype(self) -> type:
        """
        Gets the data type of the elements in the tensor.
        
        Returns:
            type: The data type of the tensor elements
        """
        raise NotImplementedError("dtype property must be implemented")

    def reshape(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Reshapes the tensor to the specified shape.
        
        Args:
            new_shape: Tuple[int, ...]
                The new dimensions for the tensor
        
        Returns:
            ITensor: The reshaped tensor
        """
        raise NotImplementedError("reshape method must be implemented")

    def transpose(self) -> 'ITensor':
        """
        Returns a new tensor with its dimensions reversed.
        
        Returns:
            ITensor: The transposed tensor
        """
        raise NotImplementedError("transpose method must be implemented")

    def broadcast(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Broadcasts the tensor to the specified shape.
        
        Args:
            new_shape: Tuple[int, ...]
                The new shape to broadcast the tensor to
        
        Returns:
            ITensor: The broadcasted tensor
        """
        raise NotImplementedError("broadcast method must be implemented")

    def __getitem__(self, indices: Union[int, slice, Tuple[int, ...]]) -> Union[float, IVector, IMatrix, 'ITensor']:
        """
        Gets an element, slice, or sub-tensor from the tensor using numpy-like indexing.
        
        Args:
            indices: Union[int, slice, Tuple[int, ...]]
                The indices to access the elements. Can be a single integer,
                slice, or tuple of integers and slices for n-dimensional access.
        
        Returns:
            Union[float, IVector, IMatrix, ITensor]: The accessed element(s)
        """
        raise NotImplementedError("__getitem__ method must be implemented")

    def __setitem__(self, indices: Union[int, slice, Tuple[int, ...]], value: Union[float, IVector, IMatrix, 'ITensor']):
        """
        Sets an element, slice, or sub-tensor in the tensor using numpy-like indexing.
        
        Args:
            indices: Union[int, slice, Tuple[int, ...]]
                The indices where the value(s) will be set
            value: Union[float, IVector, IMatrix, ITensor]
                The value(s) to be set in the tensor
        """
        raise NotImplementedError("__setitem__ method must be implemented")

    def __add__(self, other: 'ITensor') -> 'ITensor':
        """
        Performs element-wise addition with another tensor.
        
        Args:
            other: ITensor
                The tensor to add element-wise
        
        Returns:
            ITensor: The resulting tensor after addition
        """
        raise NotImplementedError("__add__ method must be implemented")

    def __sub__(self, other: 'ITensor') -> 'ITensor':
        """
        Performs element-wise subtraction with another tensor.
        
        Args:
            other: ITensor
                The tensor to subtract element-wise
        
        Returns:
            ITensor: The resulting tensor after subtraction
        """
        raise NotImplementedError("__sub__ method must be implemented")

    def __mul__(self, other: Union[float, IVector, IMatrix, 'ITensor']) -> Union['ITensor', IVector, float]:
        """
        Performs multiplication with a scalar, vector, matrix, or tensor.
        
        Args:
            other: Union[float, IVector, IMatrix, ITensor]
                The scalar, vector, matrix, or tensor to multiply with
        
        Returns:
            Union[ITensor, IVector, float]: The result of the multiplication
        """
        raise NotImplementedError("__mul__ method must be implemented")

    def __matmul__(self, other: 'ITensor') -> 'ITensor':
        """
        Performs tensor multiplication with another tensor.
        
        Args:
            other: ITensor
                The tensor to multiply with
        
        Returns:
            ITensor: The resulting tensor after multiplication
        """
        raise NotImplementedError("__matmul__ method must be implemented")

    def __truediv__(self, other: Union[float, IVector, IMatrix, 'ITensor']) -> Union['ITensor', IVector, float]:
        """
        Performs element-wise division by a scalar, vector, matrix, or tensor.
        
        Args:
            other: Union[float, IVector, IMatrix, ITensor]
                The scalar, vector, matrix, or tensor to divide by
        
        Returns:
            Union[ITensor, IVector, float]: The result of the division
        """
        raise NotImplementedError("__truediv__ method must be implemented")

    def __radd__(self, other: float) -> 'ITensor':
        """
        Performs right-side addition with a scalar.
        
        Args:
            other: float
                The scalar to add
        
        Returns:
            ITensor: The resulting tensor after addition
        """
        return self.__add__(other)

    def __rsub__(self, other: float) -> 'ITensor':
        """
        Performs right-side subtraction with a scalar.
        
        Args:
            other: float
                The scalar to subtract
        
        Returns:
            ITensor: The resulting tensor after subtraction
        """
        return self.__sub__(other)

    def __rmul__(self, other: float) -> 'ITensor':
        """
        Performs right-side multiplication with a scalar.
        
        Args:
            other: float
                The scalar to multiply with
        
        Returns:
            ITensor: The resulting tensor after multiplication
        """
        return self.__mul__(other)

    def __rtruediv__(self, other: float) -> 'ITensor':
        """
        Performs right-side division by a scalar.
        
        Args:
            other: float
                The scalar to divide by
        
        Returns:
            ITensor: The resulting tensor after division
        """
        return self.__truediv__(other)

    def tolist(self) -> list:
        """
        Converts the tensor to a nested list representation.
        
        Returns:
            list: A nested list representation of the tensor
        """
        raise NotImplementedError("tolist method must be implemented")

    def __str__(self) -> str:
        """
        Returns a string representation of the tensor.
        
        Returns:
            str: The string representation of the tensor
        """
        raise NotImplementedError("__str__ method must be implemented")

    def __repr__(self) -> str:
        """
        Returns the official string representation of the tensor.
        
        Returns:
            str: The official string representation
        """
        return f"<{self.__class__.__name__} shape={self.shape} dtype={self.dtype}>"