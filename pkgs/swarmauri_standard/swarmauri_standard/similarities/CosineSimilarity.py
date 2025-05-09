from typing import Literal, Sequence, Tuple
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', np.ndarray, Sequence[float])
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_type(SimilarityBase, "CosineSimilarity")
class CosineSimilarity(SimilarityBase):
    """
    Computes the cosine similarity between vectors.

    The cosine similarity is a measure of similarity between two non-zero vectors
    of an inner product space that measures the cosine of the angle between them.
    The cosine of the angle between them is equivalent to their dot product divided
    by the product of their magnitudes.

    Attributes:
        type: Literal["CosineSimilarity"]
            The type identifier for this similarity measure.
    """
    type: Literal["CosineSimilarity"] = "CosineSimilarity"

    def __init__(self):
        """
        Initialize the CosineSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized CosineSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> OutputType:
        """
        Calculate the cosine similarity between two vectors.

        Args:
            x: InputType
                The first vector to compare
            y: InputType
                The second vector to compare

        Returns:
            OutputType:
                The cosine similarity between x and y, ranging from 0 to 1.

        Raises:
            ValueError:
                If either vector is zero or if the vectors are of different lengths.
        """
        logger.debug("Calculating cosine similarity between two vectors")
        
        # Convert input to numpy arrays if they are not already
        x = np.asarray(x)
        y = np.asarray(y)
        
        # Check if vectors are non-zero
        if np.allclose(x, np.zeros_like(x)) or np.allclose(y, np.zeros_like(y)):
            raise ValueError("Non-zero vectors only")
            
        # Calculate the dot product
        dot_product = np.dot(x, y)
        
        # Calculate the norms
        norm_x = np.linalg.norm(x)
        norm_y = np.linalg.norm(y)
        
        # Avoid division by zero
        if norm_x == 0 or norm_y == 0:
            raise ValueError("Non-zero vectors only")
            
        # Compute cosine similarity
        similarity = dot_product / (norm_x * norm_y)
        
        return similarity

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[OutputType]:
        """
        Calculate cosine similarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[OutputType]:
                A sequence of cosine similarity scores corresponding to each pair.
        """
        logger.debug("Calculating cosine similarities for multiple pairs")
        
        # Calculate similarity for each pair
        return [self.similarity(x, y) for x, y in pairs]

    def dissimilarity(self, x: InputType, y: InputType) -> OutputType:
        """
        Calculate the cosine dissimilarity between two vectors.

        Dissimilarity is 1 minus similarity.

        Args:
            x: InputType
                The first vector to compare
            y: InputType
                The second vector to compare

        Returns:
            OutputType:
                The cosine dissimilarity between x and y, ranging from 0 to 1.
        """
        logger.debug("Calculating cosine dissimilarity between two vectors")
        
        return 1.0 - self.similarity(x, y)

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[OutputType]:
        """
        Calculate cosine dissimilarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[OutputType]:
                A sequence of cosine dissimilarity scores corresponding to each pair.
        """
        logger.debug("Calculating cosine dissimilarities for multiple pairs")
        
        # Calculate dissimilarity for each pair
        return [self.dissimilarity(x, y) for x, y in pairs]