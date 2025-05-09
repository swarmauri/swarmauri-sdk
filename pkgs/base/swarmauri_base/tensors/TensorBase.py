from typing import Any, Tuple, Optional, Union, Type
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.tensors.ITensor import ITensor
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class TensorBase(ITensor, ComponentBase):
    """
    A base implementation of the ITensor interface providing basic tensor operations.

    This class provides a foundational structure for tensor operations, including
    indexing, shape manipulation, and basic tensor arithmetic. It is designed to be
    extended by specific tensor implementations.

    All methods in this class are abstract and raise NotImplementedError. Subclasses
    should implement these methods according to their specific requirements.
    """
    resource: Optional[str] = Field(default=ComponentBase.ResourceTypes.TENSOR.value)

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
            NotImplementedError: This method is not implemented in the base class.
            IndexError: If index is out of bounds.
            ValueError: If slice step is invalid.
        """
        logger.error("Method __getitem__ not implemented in base class")
        raise NotImplementedError("__getitem__ must be implemented in a subclass")

    def __setitem__(self, index: Union[Tuple[int, ...], int, slice, ...], value: Any) -> None:
        """
        Set item in tensor using indexing or slicing.

        Args:
            index: Index or slice to access elements. Can be a tuple of integers,
                single integer, slice object, or a tuple of slices/ints.
            value: Value to set at the specified index. Can be a single value,
                vector, matrix, or another tensor of compatible shape.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            IndexError: If index is out of bounds.
            ValueError: If value shape is incompatible with index.
        """
        logger.error("Method __setitem__ not implemented in base class")
        raise NotImplementedError("__setitem__ must be implemented in a subclass")

    def __iter__(self) -> iter:
        """
        Return an iterator over the tensor elements.

        Yields:
            Any: The next element in the tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Method __iter__ not implemented in base class")
        raise NotImplementedError("__iter__ must be implemented in a subclass")

    def __add__(self, other: 'ITensor') -> 'ITensor':
        """
        Tensor addition.

        Args:
            other: Another tensor of the same shape and compatible dtype.

        Returns:
            ITensor: Result of element-wise addition.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If tensor shapes do not match.
            TypeError: If tensors have incompatible dtypes.
        """
        logger.error("Method __add__ not implemented in base class")
        raise NotImplementedError("__add__ must be implemented in a subclass")

    def __sub__(self, other: 'ITensor') -> 'ITensor':
        """
        Tensor subtraction.

        Args:
            other: Another tensor of the same shape and compatible dtype.

        Returns:
            ITensor: Result of element-wise subtraction.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If tensor shapes do not match.
            TypeError: If tensors have incompatible dtypes.
        """
        logger.error("Method __sub__ not implemented in base class")
        raise NotImplementedError("__sub__ must be implemented in a subclass")

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
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If tensor dimensions are incompatible for multiplication.
            TypeError: If other is of unsupported type.
        """
        logger.error("Method __mul__ not implemented in base class")
        raise NotImplementedError("__mul__ must be implemented in a subclass")

    def __matmul__(self, other: 'ITensor') -> 'ITensor':
        """
        Tensor matrix multiplication (Python 3.5+ matrix multiplication operator).

        Args:
            other: Another tensor of compatible dimensions for multiplication.

        Returns:
            ITensor: Result of matrix multiplication.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If number of dimensions or shapes are incompatible.
        """
        logger.error("Method __matmul__ not implemented in base class")
        raise NotImplementedError("__matmul__ must be implemented in a subclass")

    def shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the tensor as a tuple of dimensions.

        Returns:
            Tuple[int, ...]: The shape of the tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Method shape not implemented in base class")
        raise NotImplementedError("shape must be implemented in a subclass")

    def reshape(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Reshape the tensor to new dimensions.

        Args:
            new_shape: Tuple[int, ...] representing the new shape.

        Returns:
            ITensor: The reshaped tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If the total number of elements does not match.
        """
        logger.error("Method reshape not implemented in base class")
        raise NotImplementedError("reshape must be implemented in a subclass")

    def dtype(self) -> type:
        """
        Get the data type of the tensor elements.

        Returns:
            type: The dtype of the tensor elements.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Method dtype not implemented in base class")
        raise NotImplementedError("dtype must be implemented in a subclass")

    def transpose(self, axes: Optional[Tuple[int, ...]] = None) -> 'ITensor':
        """
        Transpose the tensor by swapping axes.

        Args:
            axes: Optional tuple of integers representing the new order of axes.
                If None, reverses the order of the axes.

        Returns:
            ITensor: The transposed tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If the number of axes is invalid.
        """
        logger.error("Method transpose not implemented in base class")
        raise NotImplementedError("transpose must be implemented in a subclass")

    def broadcast(self, new_shape: Tuple[int, ...]) -> 'ITensor':
        """
        Broadcast the tensor to a new shape.

        Args:
            new_shape: Tuple[int, ...] representing the new shape.

        Returns:
            ITensor: The broadcasted tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If broadcasting is not possible.
        """
        logger.error("Method broadcast not implemented in base class")
        raise NotImplementedError("broadcast must be implemented in a subclass")

    @classmethod
    def from_numpy(cls, array: Any) -> 'ITensor':
        """
        Create a tensor from a numpy array.

        Args:
            array: Numpy array to convert to a tensor.

        Returns:
            ITensor: The constructed tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
            ValueError: If the input array is invalid.
        """
        logger.error("Method from_numpy not implemented in base class")
        raise NotImplementedError("from_numpy must be implemented in a subclass")

    def __str__(self) -> str:
        """
        String representation of the tensor.

        Returns:
            str: A string representation of the tensor elements.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Method __str__ not implemented in base class")
        raise NotImplementedError("__str__ must be implemented in a subclass")

    @property
    def ndim(self) -> int:
        """
        Get the number of dimensions in the tensor.

        Returns:
            int: The number of dimensions.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Property ndim not implemented in base class")
        raise NotImplementedError("ndim must be implemented in a subclass")

    @property
    def size(self) -> int:
        """
        Get the total number of elements in the tensor.

        Returns:
            int: The total number of elements.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Property size not implemented in base class")
        raise NotImplementedError("size must be implemented in a subclass")

    @property
    def T(self) -> 'ITensor':
        """
        Get the transposed tensor.

        Returns:
            ITensor: The transposed tensor.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        logger.error("Property T not implemented in base class")
        raise NotImplementedError("T must be implemented in a subclass")