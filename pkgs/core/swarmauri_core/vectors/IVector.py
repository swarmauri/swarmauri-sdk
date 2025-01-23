from abc import ABC, abstractmethod


class IVector(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    @abstractmethod
    def check_closure_addition(self, other: "IVector") -> bool:
        """
        Checks if the result of vector addition is a valid vector.
        """
        pass

    @abstractmethod
    def check_closure_scalar_multiplication(self, scalar: float) -> bool:
        """
        Checks if the result of scalar multiplication is a valid vector.
        """
        pass

    @abstractmethod
    def check_additive_identity(self) -> bool:
        """
        Checks if adding the zero vector to this vector returns the original vector.
        """
        pass

    @abstractmethod
    def check_additive_inverse(self) -> bool:
        """
        Checks if adding the additive inverse of this vector results in the zero vector.
        """
        pass

    @abstractmethod
    def check_commutativity_addition(self, other: "IVector") -> bool:
        """
        Checks if vector addition is commutative.
        """
        pass

    @abstractmethod
    def check_distributivity_scalar_vector(self, scalar: float, other: "IVector") -> bool:
        """
        Checks if scalar multiplication distributes over vector addition.
        """
        pass

    @abstractmethod
    def check_distributivity_scalar_scalar(self, scalar1: float, scalar2: float) -> bool:
        """
        Checks if scalar multiplication distributes over scalar addition.
        """
        pass

    @abstractmethod
    def check_compatibility_scalar_multiplication(self, scalar1: float, scalar2: float) -> bool:
        """
        Checks if scalar multiplication is compatible with field multiplication.
        """
        pass

    @abstractmethod
    def check_scalar_multiplication_identity(self) -> bool:
        """
        Checks if scalar multiplication by 1 returns the original vector.
        """
        pass

    @abstractmethod
    def check_all_axioms(self, other: "IVector", scalar1: float, scalar2: float) -> bool:
        """
        Verifies if the vector satisfies all vector space axioms.
        """
        pass
