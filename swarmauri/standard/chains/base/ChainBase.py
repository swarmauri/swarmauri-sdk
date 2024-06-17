from typing import List, Dict, Any, Optional
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep


class ChainBase(IChain, ComponentBase):
    """
    A base implementation of the IChain interface.
    """
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    steps: List[IChainStep] = []
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    configs: Dict

    def add_step(self, step: IChainStep) -> None:
        self.steps.append(step)

    def remove_step(self, step: IChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (IChainStep): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError('This is not yet implemented')

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError('This is not yet implemented')

