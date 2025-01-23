from abc import ABC, abstractmethod
from swarmauri.vectors.IVector import IVector

class IUseInnerProduct(ABC):
    """
    Abstract base class for norms using inner products, defining inner-product-specific methods.
    """

    @abstractmethod
    def angle_between_vectors(self, x: IVector, y: IVector) -> float:
        """
        Compute the angle between two vectors.
        """
        pass

    @abstractmethod
    def verify_orthogonality(self, x: IVector, y: IVector) -> bool:
        """
        Verify if two vectors are orthogonal.
        """
        pass

    @abstractmethod
    def project(self, x: IVector, y: IVector) -> IVector:
        """
        Compute the projection of vector x onto vector y.
        """
        pass

    @abstractmethod
    def verify_parallelogram_law(self, x: IVector, y: IVector):
        """
        Verify the parallelogram law.
        """
        pass
