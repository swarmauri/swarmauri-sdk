from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase
from typing import Callable, Literal

class L2InnerProduct(InnerProductBase):
    """
    A class representing the integral inner product of two functions over an interval.

    The integral inner product computes the integral of the product of two functions.
    """

    type: Literal['L2InnerProduct'] = 'L2InnerProduct'

    def adaptive_simpsons(self, f: Callable[[float], float], g: Callable[[float], float], a: float, b: float, tol=1e-6, max_depth=10) -> float:
        """
        Compute the integral of the product of two functions using an adaptive Simpson's rule.

        Args:
            f: The first function.
            g: The second function.
            a: The lower limit of the interval.
            b: The upper limit of the interval.
            tol: The tolerance for error (default is 1e-6).
            max_depth: Maximum recursion depth to avoid infinite loops (default is 10).

        Returns:
            A float representing the integral.
        """
        def simpsons_rule(func, x0, x1, x2):
            """Compute Simpson's rule for a single interval [x0, x2] with midpoint x1."""
            h = (x2 - x0) / 2
            return (h / 3) * (func(x0) + 4 * func(x1) + func(x2))

        def recursive_integration(func, x0, x1, x2, whole, tol, depth):
            """Perform adaptive Simpson's integration recursively."""
            if depth > max_depth:
                raise RecursionError("Maximum recursion depth reached.")
            
            # Midpoints for subintervals
            x01 = (x0 + x1) / 2
            x12 = (x1 + x2) / 2
            
            # Compute subinterval integrals
            left = simpsons_rule(func, x0, x01, x1)
            right = simpsons_rule(func, x1, x12, x2)
            refined = left + right
            
            # Check if error is within tolerance
            if abs(refined - whole) < 15 * tol:
                return refined
            else:
                # Recursively refine subintervals
                left_refined = recursive_integration(func, x0, x01, x1, left, tol / 2, depth + 1)
                right_refined = recursive_integration(func, x1, x12, x2, right, tol / 2, depth + 1)
                return left_refined + right_refined

        # Function to integrate
        func = lambda x: f(x) * g(x)
        
        # Initial points
        mid = (a + b) / 2
        whole = simpsons_rule(func, a, mid, b)
        
        # Start recursive integration
        return recursive_integration(func, a, mid, b, whole, tol, 0)

    def compute(self, f: Callable[[float], float], g: Callable[[float], float], a: float, b: float) -> float:
        """
        Compute the integral inner product of two functions over an interval [a, b].

        Args:
            f: The first function.
            g: The second function.
            a: The lower limit of the interval.
            b: The upper limit of the interval.

        Returns:
            A float representing the integral inner product.

        Raises:
            ValueError: If the interval [a, b] is invalid.
        """
        if a >= b:
            raise ValueError("The lower limit 'a' must be less than the upper limit 'b'.")

        # Use the custom adaptive Simpson's rule
        return self.adaptive_simpsons(f, g, a, b)
