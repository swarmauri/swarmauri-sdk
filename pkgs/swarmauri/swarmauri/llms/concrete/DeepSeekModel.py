import json
from typing import List, Dict, Literal
import openai
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class DeepSeekModel(LLMBase):
    """
    Provider resources: https://platform.deepseek.com/api-docs/quick_start/pricing
    """

    api_key: str
    allowed_models: List[str] = [
        "deepseek-chat"
    ]
    name: str = "deepseek-chat"
    type: Literal["DeepSeekModel"] = "DeepSeekModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [
            message.model_dump(include=message_properties) for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        stream=False,
        top_p=1.0,
    ):

        # Create client
        client = openai.OpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )

        # Get system_context from last message with system context in it
        formatted_messages = self._format_messages(conversation.history)

        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=stream,
            top_p=top_p,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
