from typing import Any, Optional, Dict, Literal
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

@ComponentBase.register_type(AgentBase, "ExampleCommunityAgent")
class ExampleCommunityAgent(AgentBase):
    conversation: SubclassUnion[ConversationBase]
    type: Literal["ExampleCommunityAgent"] = "ExampleCommunityAgent"

    def exec(
        self, input_str: Optional[str] = "", llm_kwargs: Optional[Dict] = {}
    ) -> Any:
        pass
