from abc import ABC, abstractmethod
from typing import (
    Tuple,
    List,
    TypeVar,
    Union,
    Iterator,
    Sequence,
    Protocol,
    Literal,
)

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

T = TypeVar("T", bound=Union[int, float, complex])
Shape = Tuple[int, ...]
Index = Union[int, slice, Tuple[Union[int, slice], ...]]


class SupportsArray(Protocol):
    """Protocol for objects that support array-like behavior."""

    @abstractmethod
    def __array__(self) -> "ITensor": ...


class ITensor(ABC):
    """
    Core interface for tensorial algebra components.

    This interface specifies required tensor operations and structural properties
    that all tensor implementations must support, providing a common API for
    n-dimensional arrays and mathematical operations.
    """

    @abstractmethod
    def __getitem__(self, key: Index) -> Union["ITensor", IMatrix, IVector, T]:
        """
        Get an element, slice, or subtensor using indexing/slicing.

        Parameters
        ----------
        key : Index
            The index or slice to access

        Returns
        -------
        Union[ITensor, IMatrix, IVector, T]
            The requested element, vector, matrix, or subtensor

        Raises
        ------
        IndexError
            If the index is out of bounds
        """
        pass

    @abstractmethod
    def __setitem__(
        self, key: Index, value: Union["ITensor", IMatrix, IVector, T, Sequence]
    ) -> None:
        """
        Set an element, slice, or subtensor using indexing/slicing.

        Parameters
        ----------
        key : Index
            The index or slice to modify
        value : Union[ITensor, IMatrix, IVector, T, Sequence]
            The value to set

        Raises
        ------
        IndexError
            If the index is out of bounds
        ValueError
            If the value has incompatible dimensions
        """
        pass

    @property
    @abstractmethod
    def shape(self) -> Shape:
        """
        Get the shape of the tensor.

        Returns
        -------
        Shape
            The dimensions of the tensor
        """
        pass

    @abstractmethod
    def reshape(self, shape: Shape) -> "ITensor":
        """
        Reshape the tensor to the specified dimensions.

        Parameters
        ----------
        shape : Shape
            The new dimensions

        Returns
        -------
        ITensor
            A reshaped tensor

        Raises
        ------
        ValueError
            If the new shape is incompatible with the total number of elements
        """
        pass

    @property
    @abstractmethod
    def dtype(self) -> type:
        """
        Get the data type of the tensor elements.

        Returns
        -------
        type
            The data type of the elements
        """
        pass

    @abstractmethod
    def tolist(self) -> List:
        """
        Convert the tensor to a nested list.

        Returns
        -------
        List
            A nested list representing the tensor
        """
        pass

    @abstractmethod
    def __add__(self, other: Union["ITensor", T]) -> "ITensor":
        """
        Add another tensor or scalar to this tensor.

        Parameters
        ----------
        other : Union[ITensor, T]
            The tensor or scalar to add

        Returns
        -------
        ITensor
            The resulting tensor

        Raises
        ------
        ValueError
            If the tensors have incompatible dimensions
        """
        pass

    @abstractmethod
    def __sub__(self, other: Union["ITensor", T]) -> "ITensor":
        """
        Subtract another tensor or scalar from this tensor.

        Parameters
        ----------
        other : Union[ITensor, T]
            The tensor or scalar to subtract

        Returns
        -------
        ITensor
            The resulting tensor

        Raises
        ------
        ValueError
            If the tensors have incompatible dimensions
        """
        pass

    @abstractmethod
    def __mul__(self, other: Union["ITensor", T]) -> "ITensor":
        """
        Element-wise multiply this tensor by another tensor or scalar.

        Parameters
        ----------
        other : Union[ITensor, T]
            The tensor or scalar to multiply by

        Returns
        -------
        ITensor
            The resulting tensor

        Raises
        ------
        ValueError
            If the tensors have incompatible dimensions
        """
        pass

    @abstractmethod
    def __matmul__(self, other: "ITensor") -> "ITensor":
        """
        Perform tensor contraction with another tensor.

        Parameters
        ----------
        other : ITensor
            The tensor to contract with

        Returns
        -------
        ITensor
            The resulting tensor

        Raises
        ------
        ValueError
            If the tensors have incompatible dimensions for contraction
        """
        pass

    @abstractmethod
    def __truediv__(self, other: Union["ITensor", T]) -> "ITensor":
        """
        Element-wise divide this tensor by another tensor or scalar.

        Parameters
        ----------
        other : Union[ITensor, T]
            The tensor or scalar to divide by

        Returns
        -------
        ITensor
            The resulting tensor

        Raises
        ------
        ValueError
            If the tensors have incompatible dimensions
        ZeroDivisionError
            If dividing by zero
        """
        pass

    @abstractmethod
    def __neg__(self) -> "ITensor":
        """
        Negate all elements in the tensor.

        Returns
        -------
        ITensor
            The negated tensor
        """
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """
        Check if this tensor is equal to another tensor.

        Parameters
        ----------
        other : object
            The object to compare with

        Returns
        -------
        bool
            True if the tensors are equal, False otherwise
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Union["ITensor", IMatrix, IVector]]:
        """
        Iterate over the first dimension of the tensor.

        Returns
        -------
        Iterator[Union[ITensor, IMatrix, IVector]]
            An iterator yielding subtensors, matrices, or vectors
        """
        pass

    @abstractmethod
    def transpose(self, axes: Union[None, Tuple[int, ...]] = None) -> "ITensor":
        """
        Transpose (permute) the tensor's axes.

        Parameters
        ----------
        axes : Union[None, Tuple[int, ...]], optional
            The new order of dimensions. If None, reverse the dimensions.

        Returns
        -------
        ITensor
            The transposed tensor

        Raises
        ------
        ValueError
            If the axes specification is invalid
        """
        pass

    @abstractmethod
    def broadcast(self, shape: Shape) -> "ITensor":
        """
        Broadcast the tensor to a new shape.

        Parameters
        ----------
        shape : Shape
            The shape to broadcast to

        Returns
        -------
        ITensor
            The broadcasted tensor

        Raises
        ------
        ValueError
            If the tensor cannot be broadcast to the given shape
        """
        pass

    @abstractmethod
    def __array__(self) -> "ITensor":
        """
        Support for array protocol.

        Returns
        -------
        ITensor
            The tensor itself or a compatible representation
        """
        pass

    @abstractmethod
    def astype(self, dtype: type) -> "ITensor":
        """
        Cast the tensor to a specified data type.

        Parameters
        ----------
        dtype : type
            The target data type

        Returns
        -------
        ITensor
            A new tensor with the specified data type
        """
        pass

    @abstractmethod
    def to_matrix(self) -> Literal[IMatrix]:
        """
        Convert the tensor to a matrix if possible.

        Returns
        -------
        IMatrix
            The tensor as a matrix

        Raises
        ------
        ValueError
            If the tensor cannot be converted to a matrix
        """
        pass

    @abstractmethod
    def to_vector(self) -> Literal[IVector]:
        """
        Convert the tensor to a vector if possible.

        Returns
        -------
        IVector
            The tensor as a vector

        Raises
        ------
        ValueError
            If the tensor cannot be converted to a vector
        """
        pass
