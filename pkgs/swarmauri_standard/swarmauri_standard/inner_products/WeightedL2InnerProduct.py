"""Module implementing the WeightedL2 inner product for swarmauri_standard package."""

from abc import ABC, abstractmethod
import logging
from typing import Literal, Union, Optional, Callable
from scipy import integrate

# Set up logger
logger = logging.getLogger(__name__)


class WeightedL2InnerProduct(InnerProductBase):
    """
    A concrete implementation of the InnerProductBase class for computing weighted L2 inner products.

    This class provides functionality for computing inner products of real or complex functions
    with position-dependent weights. The weight function must be strictly positive.

    Attributes:
        weight_function: A callable representing the weight function.
        domain: Tuple containing the lower and upper bounds of the domain.
        quadrature_method: Optional parameter for specifying the quadrature method.

    Methods:
        compute: Computes the weighted L2 inner product of two functions.
        check_conjugate_symmetry: Checks if the inner product is conjugate symmetric.
        check_linearity: Checks if the inner product is linear in the first argument.
        check_positivity: Checks if the inner product is positive definite.
    """

    type: Literal["WeightedL2InnerProduct"] = "WeightedL2InnerProduct"

    def __init__(self, weight_function: Callable, domain: tuple, quadrature_method: Optional[str] = None):
        """
        Initializes the WeightedL2InnerProduct instance.

        Args:
            weight_function: A strictly positive function used for weighting the inner product.
            domain: A tuple containing the lower and upper bounds of the domain.
            quadrature_method: Optional parameter for specifying the quadrature method.

        Raises:
            ValueError: If the weight function is not strictly positive.
        """
        super().__init__()
        self.weight_function = weight_function
        self.domain = domain
        self.quadrature_method = quadrature_method

        # Validate weight function
        if not self._is_weight_positive():
            raise ValueError("Weight function must be strictly positive over the domain.")

    def compute(self, a: Union[Callable, complex], b: Union[Callable, complex]) -> float:
        """
        Computes the weighted L2 inner product of two functions.

        Args:
            a: The first function or value.
            b: The second function or value.

        Returns:
            A float representing the inner product result.

        Raises:
            ValueError: If the functions are not compatible.
        """
        logger.debug("Computing weighted L2 inner product")
        
        # Ensure a and b are callable or constants
        if not (callable(a) or isinstance(a, (int, float, complex))):
            raise ValueError("a must be a callable or a constant value")
        if not (callable(b) or isinstance(b, (int, float, complex))):
            raise ValueError("b must be a callable or a constant value")

        # Convert constants to functions
        if not callable(a):
            a = lambda x: a
        if not callable(b):
            b = lambda x: b

        # Define the integrand
        def integrand(x):
            return a(x) * b(x).conjugate() * self.weight_function(x)

        # Perform numerical integration
        result, error = integrate.quad(integrand, self.domain[0], self.domain[1], method=self.quadrature_method)

        logger.debug(f"Inner product result: {result}")
        return result

    def check_conjugate_symmetry(self, a: Union[Callable, complex], b: Union[Callable, complex]) -> bool:
        """
        Checks if the inner product is conjugate symmetric.

        For real-valued functions, this means <a, b> = <b, a>.
        For complex-valued functions, this means <a, b> = conjugate(<b, a>).

        Args:
            a: The first function or value.
            b: The second function or value.

        Returns:
            bool: True if the inner product is conjugate symmetric, False otherwise.
        """
        logger.debug("Checking conjugate symmetry")

        inner_product_ab = self.compute(a, b)
        inner_product_ba = self.compute(b, a)

        if a is b and (isinstance(a, Callable) or isinstance(b, Callable)):
            # For identical callables, check exact equality
            return inner_product_ab == inner_product_ba
        else:
            # For different functions, check conjugate symmetry
            return inner_product_ab == inner_product_ba.conjugate()

    def check_linearity(self, a: Union[Callable, complex], b: Union[Callable, complex], c: Union[Callable, complex, float, int]) -> bool:
        """
        Checks if the inner product is linear in the first argument.

        Args:
            a: The first function or value.
            b: The second function or value.
            c: A scalar for linearity check.

        Returns:
            bool: True if the inner product is linear, False otherwise.
        """
        logger.debug("Checking linearity")

        # Test additivity: <a + c, b> = <a, b> + <c, b>
        additivity = self.compute(lambda x: a(x) + c(x), b) == self.compute(a, b) + self.compute(c, b)

        # Test homogeneity: <k*a, b> = k*<a, b>
        k = 2.0  # Test scalar
        homogeneity = self.compute(lambda x: k * a(x), b) == k * self.compute(a, b)

        return additivity and homogeneity

    def check_positivity(self, a: Union[Callable, complex]) -> bool:
        """
        Checks if the inner product is positive definite.

        Args:
            a: The function or value to check.

        Returns:
            bool: True if the inner product is positive definite, False otherwise.
        """
        logger.debug("Checking positivity")

        inner_product = self.compute(a, a)
        
        # For real numbers, check if the result is positive
        if isinstance(inner_product, float):
            return inner_product > 0
        # For complex numbers, check if the real part is positive
        else:
            return inner_product.real > 0

    def _is_weight_positive(self) -> bool:
        """
        Helper method to check if the weight function is strictly positive over the domain.

        Returns:
            bool: True if the weight function is strictly positive, False otherwise.
        """
        # Sample the weight function at multiple points
        x_values = [self.domain[0] + i*(self.domain[1] - self.domain[0])*0.1 for i in range(10)]
        for x in x_values:
            if self.weight_function(x) <= 0:
                return False
        return True