from typing import List
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainProcessingStrategyBase(IChainProcessingStrategy):
    """
    A base implementation of the IChainProcessingStrategy interface.
    """
    
    def execute_steps(self, steps: List[IChainStep]):
        """
        Default implementation which should be overridden by specific processing strategies.
        """
        for step in steps:
            print(step)
            step.method(*step.args, **step.kwargs)