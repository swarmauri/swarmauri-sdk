import logging
from typing import Iterator, List, Optional, Sequence, Tuple, Union

from pydantic import Field
from swarmauri_core.matrices.IMatrix import IMatrix, Index, IVector, T

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class MatrixBase(IMatrix, ComponentBase):
    """
    Base class for matrix operations.

    Provides abstract implementations for matrix operations including addition,
    subtraction, multiplication, division, and other common matrix functions.
    This class serves as a foundation for concrete matrix implementations.

    Attributes
    ----------
    resource : Optional[str]
        The resource type of this component, defaults to MATRIX
    """

    resource: Optional[str] = Field(default=ResourceTypes.MATRIX.value)

    def __getitem__(self, key: Index) -> Union["IMatrix", IVector, T]:
        """
        Get an element, row, column, or submatrix using indexing/slicing.

        Parameters
        ----------
        key : Index
            The index or slice to access

        Returns
        -------
        Union[IMatrix, IVector, T]
            The requested element, vector, or submatrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError(
            "__getitem__ must be implemented by a concrete subclass"
        )

    def __setitem__(
        self, key: Index, value: Union["IMatrix", IVector, T, Sequence[Sequence[T]]]
    ) -> None:
        """
        Set an element, row, column, or submatrix using indexing/slicing.

        Parameters
        ----------
        key : Index
            The index or slice to modify
        value : Union[IMatrix, IVector, T, Sequence[Sequence[T]]]
            The value to set

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError(
            "__setitem__ must be implemented by a concrete subclass"
        )

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Get the shape of the matrix.

        Returns
        -------
        Tuple[int, int]
            The dimensions of the matrix as (rows, columns)

        Raises
        ------
        NotImplementedError
            This property must be implemented by subclasses
        """
        raise NotImplementedError(
            "shape property must be implemented by a concrete subclass"
        )

    def reshape(self, shape: Tuple[int, int]) -> "IMatrix":
        """
        Reshape the matrix to the specified dimensions.

        Parameters
        ----------
        shape : Tuple[int, int]
            The new dimensions as (rows, columns)

        Returns
        -------
        IMatrix
            A reshaped matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("reshape must be implemented by a concrete subclass")

    @property
    def dtype(self) -> type:
        """
        Get the data type of the matrix elements.

        Returns
        -------
        type
            The data type of the elements

        Raises
        ------
        NotImplementedError
            This property must be implemented by subclasses
        """
        raise NotImplementedError(
            "dtype property must be implemented by a concrete subclass"
        )

    def tolist(self) -> List[List[T]]:
        """
        Convert the matrix to a nested list.

        Returns
        -------
        List[List[T]]
            A list of lists representing the matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("tolist must be implemented by a concrete subclass")

    def row(self, index: int) -> IVector:
        """
        Get a specific row of the matrix.

        Parameters
        ----------
        index : int
            The row index

        Returns
        -------
        IVector
            The specified row as a vector

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("row must be implemented by a concrete subclass")

    def column(self, index: int) -> IVector:
        """
        Get a specific column of the matrix.

        Parameters
        ----------
        index : int
            The column index

        Returns
        -------
        IVector
            The specified column as a vector

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("column must be implemented by a concrete subclass")

    def __add__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Add another matrix or scalar to this matrix.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to add

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("__add__ must be implemented by a concrete subclass")

    def __sub__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Subtract another matrix or scalar from this matrix.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to subtract

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("__sub__ must be implemented by a concrete subclass")

    def __mul__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Element-wise multiply this matrix by another matrix or scalar.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to multiply by

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("__mul__ must be implemented by a concrete subclass")

    def __matmul__(self, other: "IMatrix") -> "IMatrix":
        """
        Perform matrix multiplication with another matrix.

        Parameters
        ----------
        other : IMatrix
            The matrix to multiply with

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError(
            "__matmul__ must be implemented by a concrete subclass"
        )

    def __truediv__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Element-wise divide this matrix by another matrix or scalar.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to divide by

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError(
            "__truediv__ must be implemented by a concrete subclass"
        )

    def __neg__(self) -> "IMatrix":
        """
        Negate all elements in the matrix.

        Returns
        -------
        IMatrix
            The negated matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("__neg__ must be implemented by a concrete subclass")

    def __eq__(self, other: object) -> bool:
        """
        Check if this matrix is equal to another matrix.

        Parameters
        ----------
        other : object
            The object to compare with

        Returns
        -------
        bool
            True if the matrices are equal, False otherwise

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("__eq__ must be implemented by a concrete subclass")

    def __iter__(self) -> Iterator[IVector]:
        """
        Iterate over the rows of the matrix.

        Returns
        -------
        Iterator[IVector]
            An iterator yielding rows as vectors

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("__iter__ must be implemented by a concrete subclass")

    def transpose(self) -> "IMatrix":
        """
        Transpose the matrix.

        Returns
        -------
        IMatrix
            The transposed matrix

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError(
            "transpose must be implemented by a concrete subclass"
        )

    def __array__(self) -> "IMatrix":
        """
        Support for numpy's array protocol.

        Returns
        -------
        IMatrix
            The matrix itself or a compatible representation

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError(
            "__array__ must be implemented by a concrete subclass"
        )
