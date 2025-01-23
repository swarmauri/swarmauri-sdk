# swarmauri_core/innerproducts/IInnerProduct.py
from abc import ABC, abstractmethod
from typing import Union
from swarmauri_core.vectors.IVector import IVector

class IInnerProduct(ABC):
    """
    Abstract class for an inner product.
    Enforces a strict structure with only abstract methods.
    """

    @abstractmethod
    def compute(self, u: IVector, v: IVector) -> Union[float, complex]:
        """
        Compute the inner product ⟨u, v⟩.
        """
        pass

    @abstractmethod
    def check_conjugate_symmetry(self, u: IVector, v: IVector) -> bool:
        """
        Checks conjugate symmetry: ⟨u, v⟩ = conjugate(⟨v, u⟩).
        """
        pass

    @abstractmethod
    def check_linearity_first_argument(self, u: IVector, v: IVector, w: IVector, alpha: complex) -> bool:
        """
        Checks linearity in the first argument:
        ⟨αu + v, w⟩ = α⟨u, w⟩ + ⟨v, w⟩.
        """
        pass

    @abstractmethod
    def check_positivity(self, v: IVector) -> bool:
        """
        Checks positivity: ⟨v, v⟩ ≥ 0 and ⟨v, v⟩ = 0 iff v = 0.
        """
        pass

    @abstractmethod
    def check_all_axioms(self, u: IVector, v: IVector, w: IVector, alpha: complex) -> bool:
        """
        Checks all axioms for a given set of vectors and a scalar.
        Returns True if all checks pass.
        """
        pass
