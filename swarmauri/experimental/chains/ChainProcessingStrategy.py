from typing import List, Any
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainProcessingStrategy(IChainProcessingStrategy):
    def execute_steps(self, steps: List[IChainStep]) -> Any:
        """
        Executes the given list of ordered chain steps based on the specific strategy 
        and collects their results.

        Args:
            steps (List[IChainStep]): The ordered list of chain steps to be executed.
        
        Returns:
            Any: The result of executing the steps. This could be tailored as per requirement.
        """
        results = []
        for step in steps:
            result = step.method(*step.args, **step.kwargs)
            results.append(result)
        return results