from typing import List, Dict, Set
from ....core.vector_stores.ISimilarity import ISimilarity

class SSIVSimilarity(ISimilarity):
    """
    Concrete class that implements ISimilarity interface using
    State Similarity of Important Variables (SSIV) as the similarity measure.
    """

    def similarity(self, state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the SSIV between two states represented by sets of variables.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        """
        return self.calculate_ssiv(state_a, state_b, importance_a, importance_b)

    @staticmethod
    def calculate_ssiv(state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the State Similarity of Important Variables (SSIV) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        
        Note: It is assumed that the importance weights are non-negative.
        """
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the summed importance of shared variables
        shared_importance_sum = sum(importance_a[var] for var in shared_variables) + sum(importance_b[var] for var in shared_variables)
        
        # Calculate the total importance of all variables in both states
        total_importance_sum = sum(importance_a.values()) + sum(importance_b.values())
        
        # Calculate and return the SSIV
        ssiv = (2 * shared_importance_sum) / total_importance_sum if total_importance_sum != 0 else 0
        return ssiv
