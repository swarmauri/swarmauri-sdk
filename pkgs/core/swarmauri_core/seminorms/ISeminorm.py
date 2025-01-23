# swarmauri_core/norms/INorm.py
from abc import ABC, abstractmethod
from swarmauri.vectors.IVector import IVector

class ISeminorm(ABC):
    """
    Abstract base class for a norm.

    A norm ∥⋅∥ satisfies the following axioms:
    1. Non-negativity: ∥x∥ ≥ 0 and ∥x∥ = 0 ⟺ x = 0
    2. Absolute scalability: ∥αx∥ = |α| ⋅ ∥x∥
    3. Triangle inequality: ∥x + y∥ ≤ ∥x∥ + ∥y∥
    """

    @abstractmethod
    def compute(self, x: IVector) -> float:
        """
        Compute the norm of a vector x.

        :param x: The vector for which to compute the norm.
        :return: The norm of x.
        """
        pass

    @abstractmethod
    def verify_non_negativity(self, x: IVector):
        """
        Verify non-negativity: ∥x∥ ≥ 0 and ∥x∥ = 0 ⟺ x = 0

        :param x: The vector to verify.
        """
        pass

    @abstractmethod
    def verify_absolute_scalability(self, alpha: float, x: IVector):
        """
        Verify absolute scalability: ∥αx∥ = |α| ⋅ ∥x∥

        :param alpha: The scalar multiplier.
        :param x: The vector to verify.
        """
        pass

    @abstractmethod
    def verify_triangle_inequality(self, x: IVector, y: IVector):
        """
        Verify triangle inequality: ∥x + y∥ ≤ ∥x∥ + ∥y∥

        :param x: The first vector (an instance of IVector).
        :param y: The second vector (an instance of IVector).
        """
        pass