from typing import Union, Literal
import numpy as np
import logging

from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Define logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "WeightedL2InnerProduct")
class WeightedL2InnerProduct(InnerProductBase):
    """
    A concrete implementation of the InnerProductBase class for weighted L2 inner products.

    This class provides functionality for computing inner products in weighted L2 spaces.
    The weights are position-dependent and must be strictly positive.
    """

    type: Literal["WeightedL2InnerProduct"] = "WeightedL2InnerProduct"

    def __init__(self, weight: Union[np.ndarray, callable]):
        """
        Initializes the WeightedL2InnerProduct instance.

        Args:
            weight: Either a numpy array of weights or a callable that returns weights.
                   The weights must be strictly positive.

        Raises:
            ValueError: If weights are not strictly positive
        """
        super().__init__()
        self.weight = weight

        # Validate weights if they are provided as an array
        if isinstance(weight, np.ndarray):
            if not np.all(weight > 0):
                logger.error("Weights must be strictly positive")
                raise ValueError("Weights must be strictly positive")

    def compute(
        self, a: Union[object, object], b: Union[object, object]
    ) -> Union[float, complex]:
        """
        Computes the weighted L2 inner product between two elements.

        Args:
            a: The first element for the inner product
            b: The second element for the inner product

        Returns:
            Union[float, complex]: The result of the weighted L2 inner product

        Raises:
            ValueError: If the dimensions of a and b do not match the weights
        """
        try:
            # Get the weights
            if callable(self.weight):
                weight = self.weight(a)
            else:
                weight = self.weight

            # Ensure the weights shape matches the input
            if len(weight.shape) == 1 and len(a.shape) > 1:
                weight = weight[:, None]

            # Compute the weighted inner product
            weighted_a = a * np.sqrt(weight)
            weighted_b = b * np.sqrt(weight)
            return np.vdot(weighted_a.ravel(), weighted_b.ravel())

        except Exception as e:
            logger.error(f"Error in compute method: {str(e)}")
            raise

    def check_conjugate_symmetry(
        self, a: Union[object, object], b: Union[object, object]
    ) -> bool:
        """
        Checks if the inner product implementation satisfies conjugate symmetry.

        Args:
            a: The first element to check
            b: The second element to check

        Returns:
            bool: True if conjugate symmetry holds, False otherwise
        """
        try:
            inner_product_ab = self.compute(a, b)
            inner_product_ba = self.compute(b, a)

            # Check if inner_product_ab equals the conjugate of inner_product_ba
            if isinstance(inner_product_ab, (float, np.floating)) or isinstance(
                inner_product_ab, (complex, np.complex_)
            ):
                return np.isclose(inner_product_ab, np.conj(inner_product_ba))
            else:
                logger.error("Unexpected type in conjugate symmetry check")
                return False

        except Exception as e:
            logger.error(f"Error in check_conjugate_symmetry method: {str(e)}")
            return False

    def check_linearity_first_argument(
        self,
        a: Union[object, object],
        b: Union[object, object],
        c: Union[object, object],
    ) -> bool:
        """
        Checks if the inner product implementation is linear in the first argument.

        Args:
            a: The first element for linearity check
            b: The second element for linearity check
            c: The third element for linearity check

        Returns:
            bool: True if linearity in the first argument holds, False otherwise
        """
        try:
            # Check additivity: <a + c, b> = <a, b> + <c, b>
            inner_product_add = self.compute(a + c, b)
            inner_product_sum = self.compute(a, b) + self.compute(c, b)

            # Check homogeneity: <s*a, b> = s*<a, b> for scalar s
            scalar = 2.0
            inner_product_scale = self.compute(scalar * a, b)
            inner_product_scaled = scalar * self.compute(a, b)

            # Check if both conditions hold
            return np.isclose(inner_product_add, inner_product_sum) and np.isclose(
                inner_product_scale, inner_product_scaled
            )

        except Exception as e:
            logger.error(f"Error in check_linearity_first_argument method: {str(e)}")
            return False

    def check_positivity(self, a: Union[object, object]) -> bool:
        """
        Checks if the inner product implementation satisfies positive definiteness.

        Args:
            a: The element to check for positivity

        Returns:
            bool: True if positivity holds, False otherwise
        """
        try:
            inner_product = self.compute(a, a)

            if isinstance(inner_product, (float, np.floating)):
                return inner_product > 0
            elif isinstance(inner_product, (complex, np.complex_)):
                return inner_product.real > 0  # For complex numbers, check real part
            else:
                logger.error("Unexpected type in positivity check")
                return False

        except Exception as e:
            logger.error(f"Error in check_positivity method: {str(e)}")
            return False
