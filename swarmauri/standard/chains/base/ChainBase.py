from typing import List, Dict, Any
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep

class ChainBase(IChain):
    """
    A base implementation of the IChain interface.
    """

    def __init__(self, 
                 steps: List[IChainStep] = None,
                 **configs):
        self.steps = steps if steps is not None else []
        self.configs = configs

    def add_step(self, step: IChainStep) -> None:
        self.steps.append(step)

    def remove_step(self, step: IChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (IChainStep): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError('this is not yet implemented')

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError('this is not yet implemented')

    def get_schema_info(self) -> Dict[str, Any]:
        # Return a serialized version of the Chain instance's configuration
        return {
            "steps": [str(step) for step in self.steps],
            "configs": self.configs
        }