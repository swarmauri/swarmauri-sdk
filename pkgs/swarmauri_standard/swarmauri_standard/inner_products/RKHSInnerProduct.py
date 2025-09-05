import logging
from typing import Callable, Literal, TypeVar, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
Vector = TypeVar("Vector", bound="IVector")
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "RKHSInnerProduct")
class RKHSInnerProduct(InnerProductBase):
    """
    Implements inner product from a reproducing kernel.

    This class induces an inner product via kernel evaluation in a
    Reproducing Kernel Hilbert Space (RKHS). The kernel function must be
    positive-definite to ensure that the induced inner product satisfies
    all properties of an inner product.

    Attributes
    ----------
    type : Literal["RKHSInnerProduct"]
        The type identifier for this inner product implementation
    resource : str
        The resource type identifier, defaulting to INNER_PRODUCT
    kernel_function : Callable
        The kernel function used to compute the inner product
    """

    type: Literal["RKHSInnerProduct"] = "RKHSInnerProduct"
    kernel_function: Callable

    def __init__(self, kernel_function: Callable, **kwargs):
        """
        Initialize the RKHS inner product with a kernel function.

        Parameters
        ----------
        kernel_function : Callable
            A positive-definite kernel function that takes two arguments
            and returns a scalar value
        **kwargs
            Additional keyword arguments
        """
        kwargs["kernel_function"] = kernel_function
        super().__init__(**kwargs)
        logger.info("Initialized RKHSInnerProduct with kernel function")

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the inner product between two objects using the kernel function.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second object for inner product calculation

        Returns
        -------
        float
            The inner product value computed using the kernel function

        Raises
        ------
        TypeError
            If the input types are not supported by the kernel function
        """
        logger.debug(f"Computing RKHS inner product between {type(a)} and {type(b)}")
        try:
            result = self.kernel_function(a, b)
            logger.debug(f"Inner product result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error computing RKHS inner product: {str(e)}")
            raise TypeError(f"Inputs not supported by kernel function: {str(e)}")

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the kernel-induced inner product satisfies the conjugate symmetry property.

        For real-valued kernels, this checks if K(a,b) = K(b,a).
        For complex-valued kernels, this checks if K(a,b) = K(b,a)*.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object
        b : Union[Vector, Matrix, Callable]
            The second object

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug("Checking conjugate symmetry for RKHS inner product")

        # Compute inner products in both directions
        inner_ab = self.compute(a, b)
        inner_ba = self.compute(b, a)

        # Check if they are equal (for real values) or complex conjugates
        if isinstance(inner_ab, complex) or isinstance(inner_ba, complex):
            # For complex values, check conjugate symmetry
            is_symmetric = np.isclose(inner_ab, np.conj(inner_ba))
        else:
            # For real values, they should be equal
            is_symmetric = np.isclose(inner_ab, inner_ba)

        logger.debug(f"Conjugate symmetry check result: {is_symmetric}")
        return is_symmetric

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the kernel-induced inner product satisfies linearity in the first argument.

        This verifies if K(alpha*a1 + beta*a2, b) = alpha*K(a1, b) + beta*K(a2, b).
        Note: This check may not be applicable for all kernel functions, especially
        if they don't support linear combinations of inputs directly.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
            The second object
        alpha : float
            Scalar multiplier for a1
        beta : float
            Scalar multiplier for a2

        Returns
        -------
        bool
            True if linearity in the first argument holds, False otherwise

        Raises
        ------
        TypeError
            If the inputs don't support linear combinations
        """
        logger.debug(
            f"Checking linearity in first argument with alpha={alpha}, beta={beta}"
        )

        # Check if inputs support linear combinations
        if isinstance(a1, np.ndarray) and isinstance(a2, np.ndarray):
            # Compute the linear combination
            linear_combo = alpha * a1 + beta * a2

            # Compute the left side of the linearity equation
            left_side = self.compute(linear_combo, b)

            # Compute the right side of the linearity equation
            right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            # Check if they are approximately equal
            is_linear = np.isclose(left_side, right_side)
            logger.debug(f"Linearity check result: {is_linear}")
            return is_linear
        else:
            logger.warning("Linearity check not supported for non-array inputs")
            raise TypeError("Linearity check requires numpy array inputs")

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the kernel-induced inner product satisfies the positivity property.

        This verifies if K(a, a) >= 0 for all a.
        For a valid positive-definite kernel, this property should always hold.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The object to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for RKHS inner product with {type(a)}")

        # Compute the inner product of a with itself
        inner_aa = self.compute(a, a)

        # For a valid kernel, K(a,a) should always be non-negative
        is_positive = inner_aa >= 0

        logger.debug(f"Positivity check result: {is_positive}")
        return is_positive

    def is_positive_definite(self, vectors: list) -> bool:
        """
        Check if the kernel function is positive definite.

        This method constructs the Gram matrix for a set of vectors and
        checks if it is positive definite by verifying that all eigenvalues
        are positive.

        Parameters
        ----------
        vectors : list
            A list of vectors to use for constructing the Gram matrix

        Returns
        -------
        bool
            True if the kernel is positive definite, False otherwise
        """
        logger.debug(
            f"Checking if kernel is positive definite using {len(vectors)} vectors"
        )

        n = len(vectors)
        # Construct the Gram matrix
        gram_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                gram_matrix[i, j] = self.compute(vectors[i], vectors[j])

        # Check if the Gram matrix is positive definite
        # A matrix is positive definite if all eigenvalues are positive
        eigenvalues = np.linalg.eigvals(gram_matrix)
        is_pd = np.all(eigenvalues > -1e-10)  # Allow for numerical errors

        logger.debug(f"Positive definiteness check result: {is_pd}")
        return is_pd
