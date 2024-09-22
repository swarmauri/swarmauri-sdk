import json
from typing import List, Dict, Literal
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class OpenAIModel(LLMBase):
    """
    Provider resources: https://platform.openai.com/docs/models
    """

    api_key: str
    allowed_models: List[str] = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo",
        "gpt-4o-mini",
        "chatgpt-4o-latest",
        "gpt-3.5-turbo-instruct",
        "o1-preview",
        "o1-mini",
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "o1-preview-2024-09-12",
        "o1-mini-2024-09-12",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-4-0314",
        "gpt-3.5-turbo-0125",
    ]
    name: str = "gpt-3.5-turbo"
    type: Literal["OpenAIModel"] = "OpenAIModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = None,
    ):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.

        Returns:
        - The generated message content.
        """
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(api_key=self.api_key)

        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop,
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop,
            )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
