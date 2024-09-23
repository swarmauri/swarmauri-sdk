import json
from typing import List, Literal, Dict
from mistralai import Mistral
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class MistralModel(LLMBase):
    """Provider resources: https://docs.mistral.ai/getting-started/models/"""

    api_key: str
    allowed_models: List[str] = [
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest",
        "open-mistral-nemo",
        "codestral-latest",
        "open-codestral-mamba",
    ]
    name: str = "open-mixtral-8x7b"
    type: Literal["MistralModel"] = "MistralModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ):

        formatted_messages = self._format_messages(conversation.history)

        client = Mistral(api_key=self.api_key)
        if enable_json:
            response = client.chat.complete(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )
        else:
            response = client.chat.complete(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )

        result = json.loads(response.json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
