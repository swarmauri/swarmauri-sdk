from typing import Set, List, Dict
from ....core.vector_stores.ISimilarity import ISimilarity
from ....core.vectors.IVector import IVector


class SSASimilarity(ISimilarity):
    """
    Implements the State Similarity in Arity (SSA) similarity measure to
    compare states (sets of variables) for their similarity.
    """

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Calculate the SSA similarity between two documents by comparing their metadata,
        assumed to represent states as sets of variables.

        Args:
        - vector_a (IDocument): The first document.
        - vector_b (IDocument): The second document to compare with the first document.

        Returns:
        - float: The SSA similarity measure between vector_a and vector_b, ranging from 0 to 1
                 where 0 represents no similarity and 1 represents identical states.
        """
        state_a = set(vector_a.metadata.keys())
        state_b = set(vector_b.metadata.keys())

        return self.calculate_ssa(state_a, state_b)

    @staticmethod
    def calculate_ssa(state_a: Set[str], state_b: Set[str]) -> float:
        """
        Calculate the State Similarity in Arity (SSA) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.

        Returns:6
        - float: The SSA similarity measure, ranging from 0 (no similarity) to 1 (identical states).
        """
        # Calculate the intersection (shared variables) between the two states
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the union (total unique variables) of the two states
        total_variables = state_a.union(state_b)
        
        # Calculate the SSA measure as the ratio of shared to total variables
        ssa = len(shared_variables) / len(total_variables) if total_variables else 1
        
        return ssa