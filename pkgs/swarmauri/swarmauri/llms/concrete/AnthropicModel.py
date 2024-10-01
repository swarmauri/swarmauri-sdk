import json
from typing import List, Dict, Literal
import anthropic
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class AnthropicModel(LLMBase):
    """
    Provider resources: https://docs.anthropic.com/en/docs/about-claude/models#model-names
    """

    api_key: str
    allowed_models: List[str] = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
    ]
    name: str = "claude-3-haiku-20240307"
    type: Literal["AnthropicModel"] = "AnthropicModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [
            message.model_dump(include=message_properties)
            for message in messages
            if message.role != "system"
        ]
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

    def predict(self, conversation, temperature=0.7, max_tokens=256):

        # Create client
        client = anthropic.Anthropic(api_key=self.api_key)

        # Get system_context from last message with system context in it
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        if system_context:
            response = client.messages.create(
                model=self.name,
                messages=formatted_messages,
                system=system_context,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            response = client.messages.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        message_content = response.content[0].text
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
