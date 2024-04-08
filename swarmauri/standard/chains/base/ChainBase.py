from typing import List
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy

from typing import Dict, Any
class ChainBase(IChain):
    """
    A base implementation of the IChain interface.
    """

    def __init__(self, 
                 order_strategy: IChainOrderStrategy, 
                 processing_strategy: IChainProcessingStrategy, 
                 steps: List[IChainStep] = None,
                 **configs):
        self.order_strategy = order_strategy
        self.processing_strategy = processing_strategy
        self.steps = steps if steps is not None else []
        self.configs = configs

    def add_step(self, step: IChainStep):
        self.steps.append(step)

    def invoke(self, *args, **kwargs) -> Any:
        ordered_steps = self.order_strategy.order_steps(self.steps)
        self.processing_strategy.execute_steps(ordered_steps)
        pass

    async def ainvoke(self, *args, **kwargs) -> Any:
        # Implement asynchronous invocation logic here
        pass

    def batch(self, requests: List[Dict[str, Any]]) -> List[Any]:
        # Implement batch processing logic heres
        pass

    async def abatch(self, requests: List[Dict[str, Any]]) -> List[Any]:
        # Implement asynchronous batch processing logic here
        pass
    
    def stream(self, *args, **kwargs) -> Any:
        # Implement streaming logic here
        pass

    def get_schema_info(self) -> Dict[str, Any]:
        # Return a serialized version of the Chain instance's configuration
        return {
            "order_strategy": str(self.order_strategy),
            "processing_strategy": str(self.processing_strategy),
            "steps": [str(step) for step in self.steps],
            "configs": self.configs
        }