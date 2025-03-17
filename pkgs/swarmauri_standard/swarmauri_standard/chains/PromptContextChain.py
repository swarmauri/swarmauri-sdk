from typing import Literal
from swarmauri_base.chains.PromptContextChainBase import PromptContextChainBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptContextChainBase, "PromptContextChain")
class PromptContextChain(PromptContextChainBase):
    type: Literal["PromptContextChain"] = "PromptContextChain"
