from typing import Any, Optional, Dict, Literal
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion


@ComponentBase.register_type(AgentBase, "ExampleAgent")
class ExampleAgent(AgentBase):
    conversation: SubclassUnion[ConversationBase]
    type: Literal["ExampleAgent"] = "ExampleAgent"

    def exec(
        self, input_str: Optional[str] = "", llm_kwargs: Optional[Dict] = {}
    ) -> Any:
        pass

    async def aexec(
        self, input_str: Optional[str] = "", llm_kwargs: Optional[Dict] = {}
    ) -> Any:
        return self.exec(input_str, llm_kwargs=llm_kwargs)
