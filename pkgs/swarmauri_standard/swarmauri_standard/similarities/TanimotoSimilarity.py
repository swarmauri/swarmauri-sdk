import numpy as np
from typing import Union, List, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TanimotoSimilarity")
class TanimotoSimilarity(SimilarityBase):
    """
    Implementation of the Tanimoto similarity measure for real vectors.
    
    This class provides functionality to calculate the Tanimoto similarity between vectors.
    The Tanimoto similarity is a generalization of the Jaccard similarity for real-valued
    vectors and is commonly used in cheminformatics for comparing molecular fingerprints.
    
    Attributes:
        type: Type identifier for the similarity measure.
    """
    type: str = "TanimotoSimilarity"

    def __init__(self):
        """
        Initializes the Tanimoto similarity measure.
        """
        super().__init__()

    def similarity(
        self, 
        x: Union[np.ndarray, list], 
        y: Union[np.ndarray, list]
    ) -> float:
        """
        Calculate the Tanimoto similarity between two vectors.
        
        The Tanimoto similarity is calculated as:
        \[
            \text{similarity} = \frac{x \cdot y}{|x|^2 + |y|^2 - x \cdot y}
        \]
        where \( x \cdot y \) is the dot product of vectors x and y, and \( |x| \) denotes
        the Euclidean norm (magnitude) of vector x.
        
        Args:
            x: First vector for comparison.
            y: Second vector for comparison.
            
        Returns:
            float: Tanimoto similarity score between vectors x and y.
            
        Raises:
            ValueError: If either vector has a zero magnitude.
        """
        # Calculate the dot product of x and y
        dot_product = np.dot(x, y)
        
        # Calculate the magnitudes of x and y
        mag_x = np.dot(x, x)
        mag_y = np.dot(y, y)
        
        # Check for zero magnitude vectors
        if mag_x == 0 or mag_y == 0:
            raise ValueError("Vectors must be non-zero")
            
        # Calculate the Tanimoto similarity
        similarity = dot_product / (mag_x + mag_y - dot_product)
        
        # Ensure the result is a float
        return float(similarity)

    def similarities(
        self, 
        x: Union[np.ndarray, list],
        ys: Union[List[Union[np.ndarray, list]], Union[np.ndarray, list]]
    ) -> Union[float, List[float]]:
        """
        Calculate Tanimoto similarities between vector x and multiple vectors ys.
        
        Args:
            x: Reference vector for comparison.
            ys: List of vectors or single vector to compare with x.
            
        Returns:
            Union[float, List[float]]: List of similarity scores or single score.
        """
        # If ys is a single vector, convert it to a list
        if not isinstance(ys, list):
            ys = [ys]
            
        # Calculate similarities for each vector
        return [self.similarity(x, y) for y in ys]

    def dissimilarity(
        self, 
        x: Union[np.ndarray, list], 
        y: Union[np.ndarray, list]
    ) -> float:
        """
        Calculate the dissimilarity based on Tanimoto similarity.
        
        Args:
            x: First vector for comparison.
            y: Second vector for comparison.
            
        Returns:
            float: Dissimilarity score.
        """
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self, 
        x: Union[np.ndarray, list],
        ys: Union[List[Union[np.ndarray, list]], Union[np.ndarray, list]]
    ) -> Union[float, List[float]]:
        """
        Calculate dissimilarities between vector x and multiple vectors ys.
        
        Args:
            x: Reference vector for comparison.
            ys: List of vectors or single vector to compare with x.
            
        Returns:
            Union[float, List[float]]: List of dissimilarity scores or single score.
        """
        if not isinstance(ys, list):
            ys = [ys]
            
        return [1.0 - self.similarity(x, y) for y in ys]

    def check_boundedness(
        self, 
        x: Union[np.ndarray, list], 
        y: Union[np.ndarray, list]
    ) -> bool:
        """
        Check if the similarity measure is bounded.
        
        The Tanimoto similarity ranges between 0 (dissimilar) and 1 (identical),
        making it a bounded measure.
        
        Args:
            x: First vector for comparison.
            y: Second vector for comparison.
            
        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[np.ndarray, list]
    ) -> bool:
        """
        Check if the similarity measure is reflexive.
        
        A measure is reflexive if the similarity of any vector with itself is 1.
        
        Args:
            x: Vector to check reflexivity for.
            
        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return self.similarity(x, x) == 1.0

    def check_symmetry(
        self, 
        x: Union[np.ndarray, list], 
        y: Union[np.ndarray, list]
    ) -> bool:
        """
        Check if the similarity measure is symmetric.
        
        Args:
            x: First vector for comparison.
            y: Second vector for comparison.
            
        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return self.similarity(x, y) == self.similarity(y, x)

    def check_identity(
        self, 
        x: Union[np.ndarray, list], 
        y: Union[np.ndarray, list]
    ) -> bool:
        """
        Check if the similarity measure satisfies identity.
        
        A measure satisfies identity if the similarity of identical vectors is 1.
        
        Args:
            x: First vector for comparison.
            y: Second vector for comparison.
            
        Returns:
            bool: True if identical vectors have maximum similarity, False otherwise.
        """
        return self.similarity(x, y) == 1.0