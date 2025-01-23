# SobolevInnerProduct.py
import numpy as np
from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase
from typing import Callable, Union

class SobolevInnerProduct(InnerProductBase):
    """
    A class representing the Sobolev inner product, which considers the function and its derivatives up to order k.
    """

    type: Literal['SobolevInnerProduct'] = 'SobolevInnerProduct'

    def compute(self, f: Callable[[float], Union[float, complex]], g: Callable[[float], Union[float, complex]], 
                a: float, b: float, num_points: int = 1000, k: int = 1) -> Union[float, complex]:
        """
        Compute the Sobolev inner product of two functions over the interval [a, b], considering derivatives up to order k.

        Args:
            f: The first function.
            g: The second function.
            a: The start of the interval.
            b: The end of the interval.
            num_points: The number of points for numerical integration.
            k: The order of derivatives to include in the Sobolev inner product (k >= 0).

        Returns:
            A scalar representing the Sobolev inner product.
        """
        if a >= b:
            raise ValueError("The start of the interval must be less than the end (a < b).")
        if k < 0:
            raise ValueError("The order of derivatives (k) must be non-negative.")

        # Discretize the interval
        x_values = np.linspace(a, b, num_points)
        
        # Initialize the Sobolev inner product with the zeroth-order term (function values)
        inner_product = np.trapz([f(x) * np.conj(g(x)) for x in x_values], x_values)
        
        # Add contributions from derivatives up to order k
        f_derivative = np.array([f(x) for x in x_values])  # Zeroth derivative
        g_derivative = np.array([g(x) for x in x_values])  # Zeroth derivative
        
        for order in range(1, k + 1):
            f_derivative = np.gradient(f_derivative, x_values)  # Compute the next derivative
            g_derivative = np.gradient(g_derivative, x_values)  # Compute the next derivative
            
            # Add the contribution of the current derivative to the inner product
            inner_product += np.trapz(f_derivative * np.conj(g_derivative), x_values)
        
        return inner_product
