from typing import Any, Tuple, TypeVar, Union, Optional, Iterator, overload
import logging
from abc import ABC, abstractmethod

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.tensors.ITensor import ITensor

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', int, float, bool, slice, Tuple[Union[int, slice], ...], ellipsis)
S = TypeVar('S', int, float, bool, str)
D = TypeVar('D', Any)
Shape = Tuple[int, ...]

@ComponentBase.register_model()
class TensorBase(ITensor, ComponentBase):
    """
    A base implementation of the ITensor interface. This class provides a foundation 
    for tensor operations including basic structure and logging functionality. 
    All specific tensor operations must be implemented in subclasses.

    Inherits:
        ITensor: The interface defining tensor operations.
        ComponentBase: Base class for components in the SwarmaUri framework.
    """
    
    def __init__(self, shape: Shape, dtype: type) -> None:
        """
        Initialize the tensor with the specified shape and data type.

        Args:
            shape: Shape
                The dimensions of the tensor
            dtype: type
                The data type of the elements
        """
        super().__init__(shape, dtype)
        self._shape = shape
        self._dtype = dtype
        logger.debug(f"TensorBase initialized with shape {shape} and dtype {dtype}")

    @property
    def shape(self) -> Shape:
        """
        Get the shape of the tensor.

        Returns:
            Shape: The dimensions of the tensor
        """
        return self._shape

    @property
    def dtype(self) -> type:
        """
        Get the data type of the elements in the tensor.

        Returns:
            type: The data type of the elements
        """
        return self._dtype

    @property
    def ndim(self) -> int:
        """
        Get the number of dimensions in the tensor.

        Returns:
            int: The number of dimensions
        """
        return len(self.shape)

    @property
    def size(self) -> int:
        """
        Get the total number of elements in the tensor.

        Returns:
            int: The total number of elements
        """
        return 1
        # TODO: Implement proper size calculation based on shape
        # from functools import reduce
        # import operator
        # return reduce(operator.mul, self.shape, 1)

    @abstractmethod
    def __getitem__(self, index: T) -> Union['ITensor', Any, Any, S]:
        """
        Get a slice, element, or view of the tensor.

        Args:
            index: T
                The index or slice to retrieve

        Returns:
            Union['ITensor', Any, Any, S]: 
                - If index is a tuple of slices: Returns a sub-tensor
                - If index is an integer: Returns the specified element
                - If index is a slice: Returns a slice of the tensor

        Raises:
            IndexError: If the index is out of bounds
            TypeError: If the index type is not supported
        """
        logger.debug("Getting item from tensor")
        raise NotImplementedError("Method __getitem__ must be implemented in a subclass")

    @abstractmethod
    def __setitem__(self, index: T, value: Union['ITensor', Any, Any, S]) -> None:
        """
        Set an element, slice, or view of the tensor.

        Args:
            index: T
                The index or slice to set
            value: Union['ITensor', Any, Any, S]
                The value to set

        Raises:
            IndexError: If the index is out of bounds
            TypeError: If the value type is not compatible
        """
        logger.debug("Setting item in tensor")
        raise NotImplementedError("Method __setitem__ must be implemented in a subclass")

    @abstractmethod
    def reshape(self, new_shape: Shape) -> 'ITensor':
        """
        Reshape the tensor to the specified dimensions.

        Args:
            new_shape: Shape
                The new dimensions for the tensor

        Returns:
            ITensor: The reshaped tensor

        Raises:
            ValueError: If the new shape is incompatible with the data
        """
        logger.debug(f"Reshaping tensor to {new_shape}")
        raise NotImplementedError("Method reshape must be implemented in a subclass")

    @abstractmethod
    def transpose(self, axes: Optional[Tuple[int, ...]] = None) -> 'ITensor':
        """
        Transpose the tensor along the specified axes.

        Args:
            axes: Optional[Tuple[int, ...]]
                The permutation of axes. If None, reverses the order of the axes.

        Returns:
            ITensor: The transposed tensor
        """
        logger.debug(f"Transposing tensor with axes {axes}")
        raise NotImplementedError("Method transpose must be implemented in a subclass")

    @abstractmethod
    def broadcast(self, new_shape: Shape) -> 'ITensor':
        """
        Broadcast the tensor to the specified shape.

        Args:
            new_shape: Shape
                The new shape to broadcast to

        Returns:
            ITensor: The broadcasted tensor

        Raises:
            ValueError: If broadcasting is not possible
        """
        logger.debug(f"Broadcasting tensor to {new_shape}")
        raise NotImplementedError("Method broadcast must be implemented in a subclass")

    @abstractmethod
    def get_vector(self, index: int) -> Any:
        """
        Get a vector from the tensor at the specified index.

        Args:
            index: int
                The index of the vector to retrieve

        Returns:
            Any: The specified vector

        Raises:
            IndexError: If the index is out of bounds
        """
        logger.debug(f"Getting vector at index {index}")
        raise NotImplementedError("Method get_vector must be implemented in a subclass")

    @abstractmethod
    def get_matrix(self, index: int) -> Any:
        """
        Get a matrix from the tensor at the specified index.

        Args:
            index: int
                The index of the matrix to retrieve

        Returns:
            Any: The specified matrix

        Raises:
            IndexError: If the index is out of bounds
        """
        logger.debug(f"Getting matrix at index {index}")
        raise NotImplementedError("Method get_matrix must be implemented in a subclass")

    @abstractmethod
    def tolist(self) -> list:
        """
        Convert the tensor to a nested list structure.

        Returns:
            list: A nested list representation of the tensor
        """
        logger.debug("Converting tensor to list")
        raise NotImplementedError("Method tolist must be implemented in a subclass")

    @abstractmethod
    def __add__(self, other: 'ITensor') -> 'ITensor':
        """
        Element-wise addition of two tensors.

        Args:
            other: 'ITensor'
                The tensor to add

        Returns:
            'ITensor': The result of the addition

        Raises:
            ValueError: If the tensors have different shapes
        """
        logger.debug("Adding tensors")
        raise NotImplementedError("Method __add__ must be implemented in a subclass")

    @abstractmethod
    def __sub__(self, other: 'ITensor') -> 'ITensor':
        """
        Element-wise subtraction of two tensors.

        Args:
            other: 'ITensor'
                The tensor to subtract

        Returns:
            'ITensor': The result of the subtraction

        Raises:
            ValueError: If the tensors have different shapes
        """
        logger.debug("Subtracting tensors")
        raise NotImplementedError("Method __sub__ must be implemented in a subclass")

    @abstractmethod
    def __mul__(self, other: Union['ITensor', S]) -> 'ITensor':
        """
        Element-wise multiplication or tensor product.

        Args:
            other: Union['ITensor', S]
                - If ITensor: Performs element-wise multiplication
                - If scalar: Performs scalar multiplication

        Returns:
            'ITensor': The result of the multiplication

        Raises:
            ValueError: If the shapes are incompatible for multiplication
            TypeError: If the multiplication type is not supported
        """
        logger.debug(f"Multiplying tensor with {other}")
        raise NotImplementedError("Method __mul__ must be implemented in a subclass")

    @overload
    def __mul__(self, other: 'ITensor') -> 'ITensor':
        ...

    @overload
    def __mul__(self, other: S) -> 'ITensor':
        ...

    @abstractmethod
    def __rmul__(self, other: S) -> 'ITensor':
        """
        Element-wise multiplication by a scalar (reverse operation).

        Args:
            other: S
                The scalar to multiply by

        Returns:
            'ITensor': The result of the multiplication
        """
        logger.debug(f"Multiplying tensor by scalar {other}")
        raise NotImplementedError("Method __rmul__ must be implemented in a subclass")

    @abstractmethod
    def __str__(self) -> str:
        """
        Get a string representation of the tensor.

        Returns:
            str: A string representation of the tensor
        """
        logger.debug("Getting string representation of tensor")
        raise NotImplementedError("Method __str__ must be implemented in a subclass")

    @abstractmethod
    def __repr__(self) -> str:
        """
        Get an official string representation of the tensor.

        Returns:
            str: An official string representation of the tensor
        """
        logger.debug("Getting official string representation of tensor")
        raise NotImplementedError("Method __repr__ must be implemented in a subclass")

    @abstractmethod
    def __iter__(self) -> Iterator['ITensor']:
        """
        Create an iterator over the tensor elements.

        Returns:
            Iterator['ITensor']: An iterator over the tensor elements
        """
        logger.debug("Creating iterator for tensor")
        raise NotImplementedError("Method __iter__ must be implemented in a subclass")

    @abstractmethod
    def __bool__(self) -> bool:
        """
        Determine if the tensor is non-zero.

        Returns:
            bool: True if the tensor is non-zero, False otherwise
        """
        logger.debug("Checking if tensor is non-zero")
        raise NotImplementedError("Method __bool__ must be implemented in a subclass")

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """
        Allow registration of additional subclasses without explicit registration.
        """
        return hasattr(subclass, '__getitem__') and hasattr(subclass, '__setitem__')