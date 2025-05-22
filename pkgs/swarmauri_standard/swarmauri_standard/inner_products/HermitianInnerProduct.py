import logging
from typing import Callable, Literal, TypeVar, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

Vector = TypeVar("Vector", bound="IVector")
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "HermitianInnerProduct")
class HermitianInnerProduct(InnerProductBase):
    """
    Concrete implementation of InnerProductBase for Hermitian inner products.

    This class implements the Hermitian inner product, which is a complex inner product
    with conjugate symmetry, satisfying the properties of an inner product space.
    The Hermitian inner product is defined as <a, b> = Σ(a_i * conj(b_i)) for vectors.

    Attributes
    ----------
    type : Literal["HermitianInnerProduct"]
        The type identifier for this inner product implementation
    """

    type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> complex:
        """
        Compute the Hermitian inner product between two objects.

        For vectors: <a, b> = Σ(a_i * conj(b_i))
        For matrices: <A, B> = Tr(A† * B) where A† is the conjugate transpose of A
        For callables: Depends on implementation, typically involves integration

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second object for inner product calculation

        Returns
        -------
        complex
            The Hermitian inner product value

        Raises
        ------
        TypeError
            If the input types are not supported or compatible
        ValueError
            If the dimensions of the inputs don't match
        """
        logger.debug(
            f"Computing Hermitian inner product between {type(a)} and {type(b)}"
        )

        # ADDED: Handle mixed case where one is ndarray and one is Vector
        if isinstance(a, np.ndarray) and hasattr(b, "to_numpy"):
            # Convert Vector to numpy array and proceed
            b_array = b.to_numpy()
            return self.compute(a, b_array)

        # ADDED: Handle the reverse case
        if hasattr(a, "to_numpy") and isinstance(b, np.ndarray):
            # Convert Vector to numpy array and proceed
            a_array = a.to_numpy()
            return self.compute(a_array, b)

        # Handle vectors (including IVector implementations)
        if hasattr(a, "to_numpy") and hasattr(b, "to_numpy"):
            a_array = a.to_numpy()
            b_array = b.to_numpy()

            # Check dimensions
            if a_array.shape != b_array.shape:
                error_msg = (
                    f"Vector dimensions don't match: {a_array.shape} vs {b_array.shape}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Compute Hermitian inner product: a† * b
            result = np.vdot(a_array, b_array)
            logger.debug(f"Computed vector inner product: {result}")
            return result

        # Handle numpy arrays directly (including matrices)
        elif isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            # Check dimensions
            if a.shape != b.shape:
                error_msg = f"Array dimensions don't match: {a.shape} vs {b.shape}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if len(a.shape) == 1:  # Vector case
                # Compute Hermitian inner product: a† * b
                result = np.vdot(a, b)
                logger.debug(f"Computed array inner product: {result}")
                return result
            elif len(a.shape) == 2:  # Matrix case
                # For matrices, the Hermitian inner product is the trace of A† * B
                result = np.trace(a.conj().T @ b)
                logger.debug(f"Computed matrix inner product: {result}")
                return result
            else:
                error_msg = f"Unsupported array dimension: {len(a.shape)}"
                logger.error(error_msg)
                raise TypeError(error_msg)

        # Handle callables (functions)
        elif callable(a) and callable(b):
            error_msg = "Inner product for callable objects requires integration and is not directly implemented"
            logger.error(error_msg)
            raise NotImplementedError(error_msg)

        else:
            error_msg = f"Unsupported types for Hermitian inner product: {type(a)} and {type(b)}"
            logger.error(error_msg)
            raise TypeError(error_msg)

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the inner product satisfies the conjugate symmetry property:
        <a, b> = conj(<b, a>).

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
        logger.debug(f"Checking conjugate symmetry for {type(a)} and {type(b)}")

        try:
            # Compute <a, b>
            ab_inner = self.compute(a, b)

            # Compute <b, a>
            ba_inner = self.compute(b, a)

            # Check if <a, b> = conj(<b, a>)
            is_symmetric = np.isclose(ab_inner, np.conj(ba_inner))

            logger.debug(f"Conjugate symmetry check result: {is_symmetric}")
            logger.debug(f"<a, b> = {ab_inner}, conj(<b, a>) = {np.conj(ba_inner)}")

            return bool(is_symmetric)

        except Exception as e:
            logger.error(f"Error checking conjugate symmetry: {str(e)}")
            return False

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: complex,
        beta: complex,
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
            The second object
        alpha : complex
            Scalar multiplier for a1
        beta : complex
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
            # Handle vectors (including IVector implementations)
            if (
                hasattr(a1, "to_numpy")
                and hasattr(a2, "to_numpy")
                and hasattr(b, "to_numpy")
            ):
                # Create a linear combination: alpha*a1 + beta*a2
                a1_array = a1.to_numpy()
                a2_array = a2.to_numpy()
                linear_combo = alpha * a1_array + beta * a2_array

                # Create a new vector of the same type as a1
                if hasattr(a1, "from_numpy"):
                    linear_combo_vector = a1.from_numpy(linear_combo)
                else:
                    # If from_numpy is not available, use the array directly
                    linear_combo_vector = linear_combo

                # Compute <alpha*a1 + beta*a2, b>
                left_side = self.compute(linear_combo_vector, b)

                # Compute alpha*<a1, b> + beta*<a2, b>
                right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            # Handle numpy arrays directly
            elif (
                isinstance(a1, np.ndarray)
                and isinstance(a2, np.ndarray)
                and isinstance(b, np.ndarray)
            ):
                # Create a linear combination: alpha*a1 + beta*a2
                linear_combo = alpha * a1 + beta * a2

                # Compute <alpha*a1 + beta*a2, b>
                left_side = self.compute(linear_combo, b)

                # Compute alpha*<a1, b> + beta*<a2, b>
                right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            else:
                error_msg = f"Unsupported types for linearity check: {type(a1)}, {type(a2)}, and {type(b)}"
                logger.error(error_msg)
                raise TypeError(error_msg)

            # Check if the two sides are equal
            is_linear = np.isclose(left_side, right_side)

            logger.debug(f"Linearity check result: {is_linear}")
            logger.debug(f"Left side: {left_side}, Right side: {right_side}")

            return bool(is_linear)

        except Exception as e:
            logger.error(f"Error checking linearity: {str(e)}")
            return False

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The object to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for {type(a)}")

        try:
            # Compute <a, a>
            aa_inner = self.compute(a, a)

            # Check if <a, a> is real
            if not np.isclose(aa_inner.imag, 0):
                logger.warning(f"Inner product <a, a> is not real: {aa_inner}")
                return False

            # Check if <a, a> >= 0
            is_non_negative = (
                aa_inner.real >= -1e-10
            )  # Allow for small numerical errors

            # Convert to numpy array for zero check
            if hasattr(a, "to_numpy"):
                a_array = a.to_numpy()
            elif isinstance(a, np.ndarray):
                a_array = a
            else:
                error_msg = f"Unsupported type for zero check: {type(a)}"
                logger.error(error_msg)
                raise TypeError(error_msg)

            # Check if <a, a> = 0 iff a = 0
            if np.isclose(aa_inner.real, 0):
                is_zero_iff_a_zero = np.allclose(a_array, 0)
            else:
                is_zero_iff_a_zero = not np.allclose(a_array, 0)

            result = is_non_negative and is_zero_iff_a_zero

            logger.debug(f"Positivity check result: {result}")
            logger.debug(
                f"<a, a> = {aa_inner.real}, is_non_negative = {is_non_negative}, is_zero_iff_a_zero = {is_zero_iff_a_zero}"
            )

            return result

        except Exception as e:
            logger.error(f"Error checking positivity: {str(e)}")
            return False
