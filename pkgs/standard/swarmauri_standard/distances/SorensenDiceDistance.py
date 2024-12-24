import numpy as np
from typing import List, Literal
from collections import Counter

from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase

class SorensenDiceDistance(DistanceBase):
    """
    Implementing a concrete Vector Store class for calculating Sörensen-Dice Index Distance.
    The Sörensen-Dice Index, or Dice's coefficient, is a measure of the similarity between two sets.
    """
    type: Literal['SorensenDiceDistance'] = 'SorensenDiceDistance'   
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
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
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarity(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")