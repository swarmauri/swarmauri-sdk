from typing import List, Dict, Any, Optional, Literal
from pydantic import Field, ConfigDict
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.chains.IChain import IChain
from swarmauri_base.chains.ChainStepBase import ChainStepBase
from swarmauri_core.typing import SubclassUnion


class ChainBase(IChain, ComponentBase):
    """
    A base implementation of the IChain interface.
    """

    steps: List[ChainStepBase] = []
    resource: Optional[str] = Field(default=ResourceTypes.CHAIN.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ChainBase"] = "ChainBase"

    def add_step(self, step: ChainStepBase) -> None:
        self.steps.append(step)

    def remove_step(self, step: ChainStepBase) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (ChainStepBase): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError("This is not yet implemented")

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("This is not yet implemented")
