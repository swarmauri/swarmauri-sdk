import logging
from typing import Iterator, List, Literal, Optional, Sequence, Tuple, Union

from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.tensors.ITensor import Index, ITensor, Shape, T
from swarmauri_core.vectors.IVector import IVector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class TensorBase(ITensor, ComponentBase):
    """
    Base implementation of the ITensor interface.

    This class provides a foundation for tensor operations including reshaping,
    contraction, and broadcasting. It implements the abstract methods defined in
    ITensor but raises NotImplementedError, serving as a template for concrete
    tensor implementations.

    Attributes
    ----------
    resource : Optional[str]
        Resource type identifier, defaults to TENSOR
    """

    resource: Optional[str] = ResourceTypes.TENSOR.value

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__getitem__ must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__setitem__ must be implemented by subclasses")

    @property
    def shape(self) -> Shape:
        """
        Get the shape of the tensor.

        Returns
        -------
        Shape
            The dimensions of the tensor

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("shape property must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("reshape method must be implemented by subclasses")

    @property
    def dtype(self) -> type:
        """
        Get the data type of the tensor elements.

        Returns
        -------
        type
            The data type of the elements

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("dtype property must be implemented by subclasses")

    def tolist(self) -> List:
        """
        Convert the tensor to a nested list.

        Returns
        -------
        List
            A nested list representing the tensor

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("tolist method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__add__ method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__sub__ method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__mul__ method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__matmul__ method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError(
            "__truediv__ method must be implemented by subclasses"
        )

    def __neg__(self) -> "ITensor":
        """
        Negate all elements in the tensor.

        Returns
        -------
        ITensor
            The negated tensor

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__neg__ method must be implemented by subclasses")

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

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__eq__ method must be implemented by subclasses")

    def __iter__(self) -> Iterator[Union["ITensor", IMatrix, IVector]]:
        """
        Iterate over the first dimension of the tensor.

        Returns
        -------
        Iterator[Union[ITensor, IMatrix, IVector]]
            An iterator yielding subtensors, matrices, or vectors

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__iter__ method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("transpose method must be implemented by subclasses")

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
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("broadcast method must be implemented by subclasses")

    def __array__(self) -> "ITensor":
        """
        Support for array protocol.

        Returns
        -------
        ITensor
            The tensor itself or a compatible representation

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("__array__ method must be implemented by subclasses")

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

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("astype method must be implemented by subclasses")

    def to_matrix(self) -> Literal[IMatrix]:
        """
        Convert the tensor to a matrix if possible.

        Returns
        -------
        IMatrix
            The tensor as a matrix

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("to_matrix method must be implemented by subclasses")

    def to_vector(self) -> Literal[IVector]:
        """
        Convert the tensor to a vector if possible.

        Returns
        -------
        IVector
            The tensor as a vector

        Raises
        ------
        NotImplementedError
            Method must be implemented by subclasses
        """
        raise NotImplementedError("to_vector method must be implemented by subclasses")
