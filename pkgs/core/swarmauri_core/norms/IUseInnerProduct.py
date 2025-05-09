import abc
import logging

logger = logging.getLogger("IUseInnerProduct")

class IUseInnerProduct(abc.ABC):
    """
    Interface marking components that utilize inner product geometry.
    
    This abstract base class provides a contract for components that require
    dependency on inner product structures. It defines methods for checking
    various properties related to inner product spaces such as angle between
    vectors, orthogonality, projections, and the parallelogram law.
    """
    
    @abc.abstractmethod
    def check_angle_between_vectors(self, a: object, b: object) -> float:
        """
        Calculate and return the angle between two vectors using the inner product.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            The angle in radians between the two vectors.
        """
        pass
    
    @abc.abstractmethod
    def check_verify_orthogonality(self, a: object, b: object) -> bool:
        """
        Check if two vectors are orthogonal using the inner product.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            True if the vectors are orthogonal, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def check_xy_project(self, vector: object, basis: object) -> object:
        """
        Project a vector onto a specified basis using the inner product.
        
        Args:
            vector: Vector to be projected
            basis: Basis vectors for projection
            
        Returns:
            Projected vector onto the specified basis.
        """
        pass
    
    @abc.abstractmethod
    def check_verify_parallelogram_law(self, a: object, b: object) -> bool:
        """
        Verify the parallelogram law using the inner product.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            True if the parallelogram law holds, False otherwise.
        """
        pass