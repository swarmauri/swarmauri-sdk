from typing import List, Sequence, Union, Literal, Optional, Any
import numpy as np
import logging
from swarmauri_core.similarities.ISimilarity import ComparableType
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(SimilarityBase, "HellingerAffinitySimilarity")
class HellingerAffinitySimilarity(SimilarityBase):
    """
    Hellinger Affinity Similarity measure for probability distributions.
    
    This similarity measure works on discrete probability vectors and is based on
    the Hellinger distance. It measures the similarity between two probability
    distributions using a square-root based approach.
    
    The Hellinger Affinity is defined as:
    H(P, Q) = ∑(√(p_i * q_i))
    
    Attributes
    ----------
    type : Literal["HellingerAffinitySimilarity"]
        The type identifier for this similarity measure
    """
    
    type: Literal["HellingerAffinitySimilarity"] = "HellingerAffinitySimilarity"
    
    def __init__(self):
        """
        Initialize the Hellinger Affinity Similarity measure.
        """
        super().__init__()
        logger.debug("Initializing HellingerAffinitySimilarity")
    
    def _validate_probability_vector(self, vec: Any) -> np.ndarray:
        """
        Validate and convert input to a proper probability vector.
        
        Parameters
        ----------
        vec : Any
            Input vector to validate
            
        Returns
        -------
        np.ndarray
            Validated probability vector
            
        Raises
        ------
        ValueError
            If the input is not a valid probability vector
        TypeError
            If the input cannot be converted to a numpy array
        """
        try:
            # Convert to numpy array if not already
            arr = np.asarray(vec, dtype=float)
            
            # Check if all values are non-negative
            if np.any(arr < 0):
                raise ValueError("All values in probability vector must be non-negative")
            
            # Check if sum is approximately 1
            if not np.isclose(np.sum(arr), 1.0):
                raise ValueError(f"Probability vector must sum to 1, got {np.sum(arr)}")
            
            return arr
        except Exception as e:
            logger.error(f"Error validating probability vector: {str(e)}")
            raise
    
    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Hellinger Affinity similarity between two probability distributions.
        
        Parameters
        ----------
        x : ComparableType
            First probability distribution
        y : ComparableType
            Second probability distribution
            
        Returns
        -------
        float
            Hellinger Affinity similarity score between x and y
            
        Raises
        ------
        ValueError
            If the distributions have incompatible dimensions or are not valid probability vectors
        TypeError
            If the input types are not supported
        """
        try:
            # Validate and convert inputs to numpy arrays
            x_arr = self._validate_probability_vector(x)
            y_arr = self._validate_probability_vector(y)
            
            # Check if dimensions match
            if x_arr.shape != y_arr.shape:
                raise ValueError(f"Probability vectors must have the same shape, got {x_arr.shape} and {y_arr.shape}")
            
            # Calculate Hellinger Affinity: sum of square roots of products
            # H(P, Q) = ∑(√(p_i * q_i))
            affinity = np.sum(np.sqrt(x_arr * y_arr))
            
            return float(affinity)
        except Exception as e:
            logger.error(f"Error calculating Hellinger Affinity similarity: {str(e)}")
            raise
    
    def similarities(self, x: ComparableType, ys: Sequence[ComparableType]) -> List[float]:
        """
        Calculate Hellinger Affinity similarities between one distribution and multiple others.
        
        Parameters
        ----------
        x : ComparableType
            Reference probability distribution
        ys : Sequence[ComparableType]
            Sequence of probability distributions to compare against the reference
            
        Returns
        -------
        List[float]
            List of Hellinger Affinity similarity scores
            
        Raises
        ------
        ValueError
            If any distributions have incompatible dimensions or are not valid probability vectors
        TypeError
            If any input types are not supported
        """
        try:
            # Validate and convert reference input
            x_arr = self._validate_probability_vector(x)
            
            results = []
            for y in ys:
                # Validate and convert each comparison input
                y_arr = self._validate_probability_vector(y)
                
                # Check if dimensions match
                if x_arr.shape != y_arr.shape:
                    raise ValueError(f"Probability vectors must have the same shape, got {x_arr.shape} and {y_arr.shape}")
                
                # Calculate Hellinger Affinity
                affinity = np.sum(np.sqrt(x_arr * y_arr))
                results.append(float(affinity))
            
            return results
        except Exception as e:
            logger.error(f"Error calculating multiple Hellinger Affinity similarities: {str(e)}")
            raise
    
    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Hellinger dissimilarity between two probability distributions.
        
        The Hellinger dissimilarity is defined as 1 - H(P, Q), where H is the Hellinger Affinity.
        
        Parameters
        ----------
        x : ComparableType
            First probability distribution
        y : ComparableType
            Second probability distribution
            
        Returns
        -------
        float
            Hellinger dissimilarity score between x and y
            
        Raises
        ------
        ValueError
            If the distributions have incompatible dimensions or are not valid probability vectors
        TypeError
            If the input types are not supported
        """
        try:
            # Calculate the similarity first
            sim = self.similarity(x, y)
            
            # Dissimilarity is 1 - similarity
            return 1.0 - sim
        except Exception as e:
            logger.error(f"Error calculating Hellinger dissimilarity: {str(e)}")
            raise
    
    def dissimilarities(self, x: ComparableType, ys: Sequence[ComparableType]) -> List[float]:
        """
        Calculate Hellinger dissimilarities between one distribution and multiple others.
        
        Parameters
        ----------
        x : ComparableType
            Reference probability distribution
        ys : Sequence[ComparableType]
            Sequence of probability distributions to compare against the reference
            
        Returns
        -------
        List[float]
            List of Hellinger dissimilarity scores
            
        Raises
        ------
        ValueError
            If any distributions have incompatible dimensions or are not valid probability vectors
        TypeError
            If any input types are not supported
        """
        try:
            # Calculate similarities first
            sims = self.similarities(x, ys)
            
            # Convert to dissimilarities
            return [1.0 - sim for sim in sims]
        except Exception as e:
            logger.error(f"Error calculating multiple Hellinger dissimilarities: {str(e)}")
            raise
    
    def check_bounded(self) -> bool:
        """
        Check if the Hellinger Affinity similarity measure is bounded.
        
        The Hellinger Affinity is bounded between 0 and 1.
        
        Returns
        -------
        bool
            True, as the Hellinger Affinity is bounded
        """
        return True
    
    def check_reflexivity(self, x: ComparableType) -> bool:
        """
        Check if the Hellinger Affinity similarity measure is reflexive: s(x,x) = 1.
        
        For valid probability distributions, the Hellinger Affinity of a distribution
        with itself is always 1.
        
        Parameters
        ----------
        x : ComparableType
            Probability distribution to check reflexivity with
            
        Returns
        -------
        bool
            True if s(x,x) = 1, False otherwise
            
        Raises
        ------
        ValueError
            If x is not a valid probability vector
        TypeError
            If the input type is not supported
        """
        try:
            # Validate the input
            x_arr = self._validate_probability_vector(x)
            
            # Calculate self-similarity
            self_similarity = self.similarity(x_arr, x_arr)
            
            # Check if it's approximately 1
            return abs(self_similarity - 1.0) < 1e-10
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            raise
    
    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the Hellinger Affinity similarity measure is symmetric: s(x,y) = s(y,x).
        
        The Hellinger Affinity is symmetric by definition.
        
        Parameters
        ----------
        x : ComparableType
            First probability distribution
        y : ComparableType
            Second probability distribution
            
        Returns
        -------
        bool
            True if s(x,y) = s(y,x), False otherwise
            
        Raises
        ------
        ValueError
            If the distributions are not valid probability vectors
        TypeError
            If the input types are not supported
        """
        try:
            # Calculate both directions
            similarity_xy = self.similarity(x, y)
            similarity_yx = self.similarity(y, x)
            
            # Check if they're approximately equal
            return abs(similarity_xy - similarity_yx) < 1e-10
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise
    
    def check_identity_of_discernibles(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the Hellinger Affinity satisfies the identity of discernibles: s(x,y) = 1 ⟺ x = y.
        
        For Hellinger Affinity, this property holds: the similarity is 1 if and only if
        the two distributions are identical.
        
        Parameters
        ----------
        x : ComparableType
            First probability distribution
        y : ComparableType
            Second probability distribution
            
        Returns
        -------
        bool
            True if the identity of discernibles property holds, False otherwise
            
        Raises
        ------
        ValueError
            If the distributions are not valid probability vectors
        TypeError
            If the input types are not supported
        """
        try:
            # Validate inputs
            x_arr = self._validate_probability_vector(x)
            y_arr = self._validate_probability_vector(y)
            
            # Calculate similarity
            similarity_value = self.similarity(x_arr, y_arr)
            
            # Check if distributions are equal (element-wise)
            distributions_equal = np.allclose(x_arr, y_arr)
            
            # If distributions are equal, similarity should be 1
            # If distributions are different, similarity should be < 1
            if distributions_equal:
                return abs(similarity_value - 1.0) < 1e-10
            else:
                return similarity_value < 1.0 - 1e-10
        except Exception as e:
            logger.error(f"Error checking identity of discernibles: {str(e)}")
            raise