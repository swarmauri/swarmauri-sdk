import json
from openai import OpenAI
from typing import List, Dict, Literal, Optional
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class QwenModel(LLMBase):
    """
    Provider resources: https://deepinfra.com/models/text-generation?q=Qwen
    """

    api_key: str
    allowed_models: List[str] = [
        "Qwen2-72B-Instruct",
        "Qwen2-7B-Instruct",
        "Qwen2.5-72B-Instruct"
    ]

    name: str = "Qwen2-7B-Instruct"
    type: Literal["QwenModel"] = "QwenModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

    def predict(
        self,
        conversation,
        temperature: Optional[float] = 1,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1,
        presence_penalty: Optional[float] = 0,
        frequency_penalty: Optional[float] = 0,
        stream: Optional[bool] = False,
    ):

        url = "https://api.deepinfra.com/v1/openai"
        client = OpenAI(base_url=url, api_key=self.api_key)

        formatted_messages = self._format_messages(conversation.history)
        system_context = self._get_system_context(conversation.history)
        if system_context:
            formatted_messages = [
                {"role": "system", "content": system_context},
                formatted_messages[-1],
            ]

        response = client.chat.completions.create(
            model="Qwen/"+self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stream=stream,
        )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
