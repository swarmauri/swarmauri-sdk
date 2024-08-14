import numpy as np
from typing import List
from collections import Counter

from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SorensenDiceDistance(IDistanceSimilarity):
    """
    Implementing a concrete Vector Store class for calculating Sörensen-Dice Index Distance.
    The Sörensen-Dice Index, or Dice's coefficient, is a measure of the similarity between two sets.
    """

    def distance(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Compute the Sörensen-Dice distance between two vectors.
        
        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.
        
        Returns:
            float: The computed Sörensen-Dice distance between vector_a and vector_b.
        """
        # Convert vectors to binary sets
        set_a = set([i for i, val in enumerate(vector_a) if val])
        set_b = set([i for i, val in enumerate(vector_b) if val])
        
        # Calculate the intersection size
        intersection_size = len(set_a.intersection(set_b))
        
        # Sorensen-Dice Index calculation
        try:
            sorensen_dice_index = (2 * intersection_size) / (len(set_a) + len(set_b))
        except ZeroDivisionError:
            sorensen_dice_index = 0.0
        
        # Distance is inverse of similarity for Sörensen-Dice
        distance = 1 - sorensen_dice_index
        
        return distance
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarity(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")