from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.chains.IChainStep import IChainStep

class IChainProcessingStrategy(ABC):
    """
    Interface for defining the strategy to process the execution of chain steps.
    """
    
    @abstractmethod
    def execute_steps(self, steps: List[IChainStep]):
        """
        Executes the given list of ordered chain steps based on the specific strategy.
        
        Parameters:
            steps (List[IChainStep]): The ordered list of chain steps to be executed.
        """
        pass