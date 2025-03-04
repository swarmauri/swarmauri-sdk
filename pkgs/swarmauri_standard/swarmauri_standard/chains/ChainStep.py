from typing import Literal
from swarmauri_base.chains.ChainStepBase import ChainStepBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ChainStepBase, "ChainStep")
class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """

    type: Literal["ChainStep"] = "ChainStep"
