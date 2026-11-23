"""Research one file using an authorized tool in the agent's toolkit."""

import json
from inspect import Parameter, signature
from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_standard.agents.ToolAgent import ToolAgent
from swarmauri_standard.conversations.Conversation import Conversation


@ComponentBase.register_type(AgentBase, "WimseResearchAgent")
class WimseResearchAgent(ToolAgent):
    """Use the configured file tool to summarize an authorized resource."""

    type: Literal["WimseResearchAgent"] = "WimseResearchAgent"
    conversation: SubclassUnion[ConversationBase] = Field(
        default_factory=Conversation
    )

    def research(self, file: str) -> str:
        """Ask the tool-capable model to read and summarize the named file."""
        choice = signature(self.llm.predict).parameters.get("tool_choice")
        llm_kwargs = {}
        if choice is not None and choice.default is Parameter.empty:
            # The standard adapters use an empty choice for provider defaults.
            llm_kwargs["tool_choice"] = {}
        return self.exec(
            f"Use the read_file tool with file={json.dumps(file)} to read the "
            "authorized document. Return a concise summary of its contents.",
            llm_kwargs=llm_kwargs,
        )
