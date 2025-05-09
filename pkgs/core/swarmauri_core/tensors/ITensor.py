from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional, Union, Literal, Type
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class ITensor(ABC):
    """
    Interface for tensor operations. This provides a blueprint for implementing
    tensor data structures with support for various operations, including
    indexing, slicing, shape manipulation, and tensor operations.

    The interface enforces type safety and provides a consistent API for
    different tensor implementations.
    """

    @abstractmethod
    def __getitem__(self, index: Union[Tuple[int, ...], int, slice, ...]) -> Union['ITensor', IMatrix, IVector, Any]:
        """
        Get item from tensor using indexing or slicing.

        Args:
            index: Index or slice to access elements. Can be a tuple of integers,
                single integer, slice object, or a tuple of slices/ints.

        Returns:
            Union[ITensor, IMatrix, IVector, Any]: The accessed element(s). Returns a
            new ITensor if slicing returns a subtensor, an IMatrix if slicing
            returns a matrix, an IVector if slicing returns a vector, or the element
            itself for single index.

        Raises:
            IndexError: If index is out of bounds.
            ValueError: If slice step is invalid.
        """
        pass

    @abstractmethod
    def __setitem__(self, index: Union[Tuple[int, ...], int, slice, ...], value: Any) -> None:
        """
        Set item in tensor using indexing or slicing.

        Args:
            index: Index or slice to access elements. Can be a tuple of integers,
                single integer, slice object, or a tuple of slices/ints.
            value: Value to set at the specified index. Can be a single value,
                vector, matrix, or another tensor of compatible shape.

        Raises:
            IndexError: If index is out of bounds.
            ValueError: If value shape is incompatible with index.
        """
        pass

    @abstractmethod
    def __iter__(self) -> iter:
        """
        Return an iterator over the tensor elements.

        Yields:
            Any: The next element in the tensor.
        """
        pass

    @abstractmethod
    def __add__(self, other: 'ITensor') -> 'ITensor':
        """
        Tensor addition.

        Args:
            other: Another tensor of the same shape and compatible dtype.

        Returns:
            ITensor: Result of element-wise addition.

        Raises:
            ValueError: If tensor shapes do not match.
            TypeError: If tensors have incompatible dtypes.
        """
        pass

    @abstractmethod
    def __sub__(self, other: 'ITensor') -> 'ITensor':
        """
        Tensor subtraction.

        Args:
            other: Another tensor of the same shape and compatible dtype.

        Returns:
            ITensor: Result of element-wise subtraction.

        Raises:
            ValueError: If tensor shapes do not match.
            TypeError: If tensors have incompatible dtypes.
        """
        pass

    @abstractmethod
    def __mul__(self, other: Union['ITensor', Any]) -> Union['ITensor', IMatrix, IVector]:
        """
        Tensor multiplication or element-wise multiplication.

        Args:
            other: Either another tensor for tensor multiplication or a scalar for
                element-wise multiplication.

        Returns:
            Union[ITensor, IMatrix, IVector]: Result of multiplication. Returns an
            ITensor for tensor multiplication, or an IMatrix/IVector if multiplying
            with a compatible lower-dimensional tensor, or the element-wise result
            if multiplying with a scalar.

        Raises:
            ValueError: If tensor dimensions are incompatible for multiplication.
            TypeError: If other is of unsupported type.
        """
        pass

    @abstractmethod
    def __matmul__(self, other: 'ITensor') -> 'ITensor':
        """
        Tensor matrix multiplication (Python 3.5+ matrix multiplication operator).

        Args:
            other: Another tensor of compatible dimensions for multiplication.

        Returns:
            ITensor: Result of matrix multiplication.

        Raises:
            ValueError: If number of dimensions or shapes are incompatible.
        """
        pass

    @abstractmethod
    def shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the tensor as a tuple of dimensions.

        Returns:
            Tuple[int, ...]: The shape of the tensor.
        """
        pass

    @abstractmethod
    def reshape(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Reshape the tensor to new dimensions.

        Args:
            new_shape: Tuple[int, ...] representing the new shape.

        Returns:
            ITensor: The reshaped tensor.

        Raises:
            ValueError: If the total number of elements does not match.
        """
        pass

    @abstractmethod
    def dtype(self) -> type:
        """
        Get the data type of the tensor elements.

        Returns:
            type: The dtype of the tensor elements.
        """
        pass

    @abstractmethod
    def transpose(self, axes: Optional[Tuple[int, ...]] = None) -> 'ITensor':
        """
        Transpose the tensor by swapping axes.

        Args:
            axes: Optional tuple of integers representing the new order of axes.
                If None, reverses the order of the axes.

        Returns:
            ITensor: The transposed tensor.

        Raises:
            ValueError: If the number of axes is invalid.
        """
        pass

    @abstractmethod
    def broadcast(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Broadcast the tensor to a new shape.

        Args:
            new_shape: Tuple[int, ...] representing the new shape.

        Returns:
            ITensor: The broadcasted tensor.

        Raises:
            ValueError: If broadcasting is not possible.
        """
        pass

    @classmethod
    @abstractmethod
    def from_numpy(cls, array: Any) -> 'ITensor':
        """
        Create a tensor from a numpy array.

        Args:
            array: Numpy array to convert to a tensor.

        Returns:
            ITensor: The constructed tensor.

        Raises:
            ValueError: If the input array is invalid.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        String representation of the tensor.

        Returns:
            str: A string representation of the tensor elements.
        """
        pass