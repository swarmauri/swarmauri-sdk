import warnings

from typing import Any, Optional, Dict, Literal
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(AgentBase, "ExampleAgent")
class ExampleAgent(AgentBase):
    conversation: SubclassUnion[ConversationBase]
    type: Literal["ExampleAgent"] = "ExampleAgent"

    def exec(
        self, input_str: Optional[str] = "", llm_kwargs: Optional[Dict] = {}
    ) -> Any:
        pass
