# swarmauri/innerproducts/base/InnerProductBase.py
from typing import Type, Union
from pydantic import Field, Optional, Literal
from math import sqrt
from swarmauri_core.innerproducts.IInnerProduct import IInnerProduct
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.vectors.concrete.Vector import Vector

class InnerProductBase(IInnerProduct, ComponentBase):
    """
    A base class for inner products, which provide a way to compute the inner product of two vectors.
    Subclasses must implement the `compute` method to provide a specific implementation of the inner product.
    """

    resource: Optional[str] = Field(default=ResourceTypes.INNERPRODUCT.value, frozen=True)
    type: Literal['InnerProductBase'] = 'InnerProductBase'

    @abstractmethod
    def compute(self, u: Vector, v: Vector) -> Union[float, complex]:
        """
        Compute the inner product ⟨u, v⟩.

        Args:
            u: The first vector.
            v: The second vector.

        Returns:
            A scalar representing the inner product, which can be either a float or a complex number.
        """
        raise NotImplementedError("Subclasses must implement compute.")

    def check_conjugate_symmetry(self, u: Vector, v: Vector) -> bool:
        """
        Check conjugate symmetry using the inner product defined in the concrete class.

        Args:
            u: The first vector.
            v: The second vector.

        Returns:
            True if the inner product is conjugate symmetric, False otherwise.
        """
        left = self.compute(u, v)
        right = self.compute(v, u)

        # Handle complex vs. real numbers
        if isinstance(left, complex) and isinstance(right, complex):
            return abs(left - right.conjugate()) < 1e-10  # Numerical tolerance
        elif isinstance(left, float) and isinstance(right, float):
            return abs(left - right) < 1e-10  # For real numbers, it's symmetric
        else:
            raise TypeError("The inner product must return consistent types for conjugate symmetry check.")


    def check_linearity_first_argument(self, u: Vector, v: Vector, w: Vector, alpha: complex) -> bool:
        """
        Check linearity in the first argument using the inner product defined in the concrete class.

        Args:
            u: The first vector.
            v: The second vector.
            w: The third vector.
            alpha: A complex scalar.

        Returns:
            True if the inner product is linear in the first argument, False otherwise.
        """
        # Manually compute αu + v
        scaled_u_values = [alpha * u_i for u_i in u.value]
        scaled_sum_values = [scaled_u_values[i] + v.value[i] for i in range(len(u.value))]

        # Create a temporary Vector instance for the scaled sum
        scaled_sum = Vector(value=scaled_sum_values)

        # Compute ⟨αu + v, w⟩
        left = self.compute(scaled_sum, w)
        # Compute α⟨u, w⟩ + ⟨v, w⟩
        right = alpha * self.compute(u, w) + self.compute(v, w)
        return abs(left - right) < 1e-10  # Numerical tolerance

    def check_positivity(self, v: Vector) -> bool:
        """
        Check positivity using the inner product defined in the concrete class.

        Args:
            v: The vector.

        Returns:
            True if the inner product is positive, False otherwise.
        """
        value = self.compute(v, v)
        # Manually check for zero vector
        is_zero_vector = all(component == 0 for component in v.value)
        if is_zero_vector:
            return abs(value) < 1e-10  # Tolerance for zero value
        return value > 0

    def check_all_axioms(self, u: Vector, v: Vector, w: Vector, alpha: complex) -> bool:
        """
        Check all axioms for the inner product using the inner product defined in the concrete class.

        Args:
            u: The first vector.
            v: The second vector.
            w: The third vector.
            alpha: A complex scalar.

        Returns:
            True if all axioms are satisfied, False otherwise.
        """
        return (
            self.check_conjugate_symmetry(u, v) and
            self.check_linearity_first_argument(u, v, w, alpha) and
            self.check_positivity(u)
        )

    def check_cauchy_schwarz_inequality(self, u: Vector, v: Vector) -> bool:
            """
            Check if the Cauchy-Schwarz inequality holds for the given vectors u and v.

            Args:
                u: The first vector.
                v: The second vector.

            Returns:
                True if the Cauchy-Schwarz inequality is satisfied, False otherwise.
            """
            inner_product = self.compute(u, v)
            norm_u = sqrt(self.compute(u, u))
            norm_v = sqrt(self.compute(v, v))

            # Compute the absolute value of the inner product
            abs_inner_product = abs(inner_product)

            # Compute the product of norms
            norm_product = norm_u * norm_v

            # Check if |⟨u, v⟩| <= ||u|| * ||v||
            return abs_inner_product <= norm_product + 1e-10  # Tolerance for numerical precision