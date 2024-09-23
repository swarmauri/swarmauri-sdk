from typing import Literal
from swarmauri.chains.base.PromptContextChainBase import PromptContextChainBase

class PromptContextChain(PromptContextChainBase):
    type: Literal['PromptContextChain'] = 'PromptContextChain'