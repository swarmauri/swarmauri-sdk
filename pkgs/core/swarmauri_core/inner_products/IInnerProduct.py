from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class IInnerProduct(ABC):
    """Interface defining the contract for inner product operations.
    
    This interface requires implementation of core functionality for computing
    inner products between vectors. It also provides methods for validating key
    properties of inner products: conjugate symmetry, linearity, and positivity.
    """

    @abstractmethod
    def compute(self, x: "IVector", y: "IVector") -> float:
        """Compute the inner product between two vectors.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            The inner product of x and y as a scalar value.
        """
        pass

    def check_conjugate_symmetry(self, x: "IVector", y: "IVector") -> bool:
        """Check if the inner product satisfies conjugate symmetry.
        
        Conjugate symmetry requires that the inner product of x and y is
        equal to the conjugate of the inner product of y and x.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            True if conjugate symmetry holds, False otherwise.
        """
        inner_xy = self.compute(x, y)
        inner_yx = self.compute(y, x)
        
        # For real vectors, this should be exact equality
        # For complex vectors, inner_xy should be the conjugate of inner_yx
        if inner_xy == inner_yx.conjugate():
            logger.debug("Conjugate symmetry holds")
            return True
        else:
            logger.warning("Conjugate symmetry does not hold")
            return False

    def check_linearity_first_argument(self, 
                                       x: "IVector", 
                                       y: "IVector", 
                                       z: "IVector",
                                       a: float = 1.0, 
                                       b: float = 1.0) -> bool:
        """Check if the inner product is linear in the first argument.
        
        Linearity in the first argument requires that for any vectors x, y, z
        and scalars a, b, the following holds:
        <ax + by, z> = a<x, z> + b<y, z>
        
        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y
            
        Returns:
            True if linearity holds, False otherwise.
        """
        ax_plus_by = a * x + b * y
        left_side = self.compute(ax_plus_by, z)
        right_side = a * self.compute(x, z) + b * self.compute(y, z)
        
        if left_side == right_side:
            logger.debug("Linearity in first argument holds")
            return True
        else:
            logger.warning("Linearity in first argument does not hold")
            return False

    def check_positivity(self, x: "IVector") -> bool:
        """Check if the inner product is positive definite.
        
        Positive definiteness requires that for any non-zero vector x,
        the inner product <x, x> is positive.
        
        Args:
            x: Vector to check
            
        Returns:
            True if positivity holds, False otherwise.
        """
        inner_xx = self.compute(x, x)
        
        if inner_xx > 0:
            logger.debug("Positivity holds")
            return True
        else:
            logger.warning("Positivity does not hold")
            return False