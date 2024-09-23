from typing import Literal
from swarmauri.chains.base.ChainStepBase import ChainStepBase

class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """
    type: Literal['ChainStep'] = 'ChainStep'
