import logging
from typing import Callable, Literal, Optional, TypeVar, Union

import numpy as np
from pydantic import ConfigDict
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

from swarmauri_standard.vectors.Vector import Vector

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "TraceFormWeightedInnerProduct")
class TraceFormWeightedInnerProduct(InnerProductBase):
    """
    Matrix-based inner product where trace is modulated by an external weight matrix.

    This class implements an inner product calculation between matrices where the
    inner product is defined as trace(A^T * W * B), where W is a weight matrix.
    The weight matrix modulates the importance of different elements in the matrices.

    Attributes
    ----------
    type : Literal["TraceFormWeightedInnerProduct"]
        The type identifier for this inner product implementation
    resource : str
        The resource type identifier, defaulting to INNER_PRODUCT
    weight_matrix : np.ndarray
        The weight matrix used to modulate the inner product calculation
    """

    type: Literal["TraceFormWeightedInnerProduct"] = "TraceFormWeightedInnerProduct"
    weight_matrix: np.ndarray
    model_config = ConfigDict(
        arbitrary_types_allowed=True, json_encoders={np.ndarray: lambda v: v.tolist()}
    )

    def __init__(self, weight_matrix: Optional[np.ndarray] = None, **kwargs):
        """
        Initialize the TraceFormWeightedInnerProduct with an optional weight matrix.

        Parameters
        ----------
        weight_matrix : Optional[np.ndarray], default=None
            The weight matrix to use for inner product calculations.
            If None, an identity matrix will be used.
        """
        if weight_matrix is None:
            # Default to identity matrix if no weight matrix is provided
            weight_matrix = np.eye(1)
            logger.info("No weight matrix provided, using identity matrix.")
        else:
            # Ensure the weight matrix is a numpy array
            weight_matrix = np.array(weight_matrix)
            logger.info(
                f"Initialized with weight matrix of shape {weight_matrix.shape}"
            )
        kwargs["weight_matrix"] = weight_matrix
        super().__init__(**kwargs)

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the weighted trace inner product between two matrices.

        The inner product is defined as trace(A^T * W * B), where W is the weight matrix.
        For complex matrices, we use the conjugate transpose A^H instead of transpose A^T.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first matrix for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second matrix for inner product calculation

        Returns
        -------
        float
            The inner product value

        Raises
        ------
        ValueError
            If the input objects are not matrices or have incompatible dimensions
        """
        logger.debug(
            f"Computing weighted trace inner product between {type(a)} and {type(b)}"
        )

        # Convert inputs to numpy arrays if they aren't already
        if not isinstance(a, np.ndarray):
            a = np.array(a)
        if not isinstance(b, np.ndarray):
            b = np.array(b)

        # Check if dimensions are compatible
        if (
            a.shape[0] != self.weight_matrix.shape[0]
            or b.shape[0] != self.weight_matrix.shape[1]
        ):
            error_msg = (
                f"Incompatible dimensions: a.shape={a.shape}, "
                f"weight_matrix.shape={self.weight_matrix.shape}, b.shape={b.shape}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Compute the weighted trace inner product
        try:
            # For complex matrices, use conjugate transpose (Hermitian)
            if (
                np.iscomplexobj(a)
                or np.iscomplexobj(b)
                or np.iscomplexobj(self.weight_matrix)
            ):
                # Calculate A^H * W * B (conjugate transpose)
                weighted_product = np.matmul(
                    a.conj().T, np.matmul(self.weight_matrix, b)
                )
            else:
                # Calculate A^T * W * B (regular transpose for real matrices)
                weighted_product = np.matmul(a.T, np.matmul(self.weight_matrix, b))

            # Take the trace
            result = np.trace(weighted_product)
            logger.debug(f"Inner product result: {result}")
            return result if np.iscomplexobj(result) else float(result)
        except Exception as e:
            logger.error(f"Error computing inner product: {str(e)}")
            raise

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the inner product satisfies the conjugate symmetry property:
        <a, b> = <b, a>* (complex conjugate).

        For the weighted trace inner product, this property holds if the weight matrix is Hermitian
        (equal to its own conjugate transpose).

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first matrix
        b : Union[Vector, Matrix, Callable]
            The second matrix

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug(f"Checking conjugate symmetry for {type(a)} and {type(b)}")

        # First, check if the weight matrix is Hermitian
        is_hermitian = np.allclose(
            self.weight_matrix, self.weight_matrix.T.conj(), rtol=1e-5, atol=1e-8
        )

        if not is_hermitian:
            logger.debug(
                "Weight matrix is not Hermitian, conjugate symmetry does not hold"
            )
            return False

        # If weight matrix is Hermitian, compute both inner products to verify
        try:
            ip_ab = self.compute(a, b)
            ip_ba = self.compute(b, a)

            # For complex matrices, we need to take the complex conjugate
            ip_ba_conj = np.conj(ip_ba)

            # Use more relaxed tolerances for complex numbers
            result = np.isclose(ip_ab, ip_ba_conj, rtol=1e-4, atol=1e-6)

            logger.debug(
                f"Conjugate symmetry values: <a,b>={ip_ab}, <b,a>*={ip_ba_conj}, diff={abs(ip_ab - ip_ba_conj)}"
            )
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking conjugate symmetry: {str(e)}")
            return False

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the inner product satisfies linearity in the first argument:
        <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
            The second matrix
        alpha : float
            Scalar multiplier for a1
        beta : float
            Scalar multiplier for a2

        Returns
        -------
        bool
            True if linearity in the first argument holds, False otherwise
        """
        logger.debug(
            f"Checking linearity in first argument with alpha={alpha}, beta={beta}"
        )

        try:
            # Convert inputs to numpy arrays if they aren't already
            if not isinstance(a1, np.ndarray):
                a1 = np.array(a1)
            if not isinstance(a2, np.ndarray):
                a2 = np.array(a2)
            if not isinstance(b, np.ndarray):
                b = np.array(b)

            # Check if dimensions are compatible
            if a1.shape != a2.shape:
                logger.error(
                    f"Incompatible dimensions: a1.shape={a1.shape}, a2.shape={a2.shape}"
                )
                return False

            # Compute left-hand side: <alpha*a1 + beta*a2, b>
            linear_combination = alpha * a1 + beta * a2
            lhs = self.compute(linear_combination, b)

            # Compute right-hand side: alpha*<a1, b> + beta*<a2, b>
            rhs = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            result = np.isclose(lhs, rhs)
            logger.debug(f"Linearity check result: {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking linearity: {str(e)}")
            return False

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        For the weighted trace inner product, this property holds if the weight matrix is positive semi-definite.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The matrix to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for {type(a)}")

        # First, check if the weight matrix is positive semi-definite
        try:
            # Compute eigenvalues of the weight matrix
            eigenvalues = np.linalg.eigvalsh(self.weight_matrix)
            is_psd = np.all(eigenvalues >= -1e-10)  # Allow for small numerical errors

            if not is_psd:
                logger.debug(
                    "Weight matrix is not positive semi-definite, positivity does not hold"
                )
                return False

            # Convert input to numpy array if it isn't already
            if not isinstance(a, np.ndarray):
                a = np.array(a)

            # Check if a is zero
            is_zero = np.allclose(a, np.zeros_like(a))

            # Compute <a, a>
            inner_product = self.compute(a, a)

            # Check if inner product is non-negative
            is_non_negative = (
                inner_product >= -1e-10
            )  # Allow for small numerical errors

            # Check if <a, a> = 0 iff a = 0
            if is_zero:
                is_zero_condition = np.isclose(inner_product, 0)
            else:
                is_zero_condition = inner_product > 0

            result = is_non_negative and is_zero_condition
            logger.debug(f"Positivity check result: {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking positivity: {str(e)}")
            return False

    def set_weight_matrix(self, weight_matrix: np.ndarray) -> None:
        """
        Set a new weight matrix for the inner product calculations.

        Parameters
        ----------
        weight_matrix : np.ndarray
            The new weight matrix to use
        """
        logger.info(f"Setting new weight matrix of shape {weight_matrix.shape}")
        self.weight_matrix = np.array(weight_matrix)

    def get_weight_matrix(self) -> np.ndarray:
        """
        Get the current weight matrix.

        Returns
        -------
        np.ndarray
            The current weight matrix
        """
        return self.weight_matrix
