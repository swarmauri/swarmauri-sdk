import json
from typing import List, Dict, Literal
from openai import OpenAI
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


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
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-3.5-turbo-0125",
        # "gpt-3.5-turbo-instruct", # gpt-3.5-turbo-instruct does not support v1/chat/completions endpoint. only supports (/v1/completions)
        # "o1-preview",   # Does not support max_tokens and temperature
        # "o1-mini",      # Does not support max_tokens and temperature
        # "o1-preview-2024-09-12", # Does not support max_tokens and temperature
        # "o1-mini-2024-09-12",   # Does not support max_tokens and temperature
        # "gpt-4-0314",  #  it's deprecated
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
        stop: List[str] = ["\n"],
    ):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        - stop (List[str]): List of tokens at which to stop generation.
                being None causes some models to throw status 400
                 (*chatgpt-4o-latest*)

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
