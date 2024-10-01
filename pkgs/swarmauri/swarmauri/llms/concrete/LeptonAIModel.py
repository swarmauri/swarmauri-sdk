import json
from openai import OpenAI
from typing import List, Dict, Literal, Optional
from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class LeptonAIModel(LLMBase):
    """
    Provider resources: https://www.lepton.ai/playground
    """

    api_key: str
    allowed_models: List[str] = [
        "llama2-13b",
        "llama3-1-405b",
        "llama3-1-70b",
        "llama3-1-8b",
        "llama3-70b",
        "llama3-8b",
        "mixtral-8x7b",
        "mistral-7b",
        "nous-hermes-llama2-13b",
        "openchat-3-5",
        "qwen2-72b",
        "toppy-m-7b",
        "wizardlm-2-7b",
        "wizardlm-2-8x22b",
    ]

    name: str = "llama3-8b"
    type: Literal["LeptonAIModel"] = "LeptonAIModel"

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
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
        stream: Optional[bool] = False,
    ):

        url = f"https://{self.name}.lepton.run/api/v1/"
        client = OpenAI(base_url=url, api_key=self.api_key)

        formatted_messages = self._format_messages(conversation.history)
        system_context = self._get_system_context(conversation.history)
        if system_context:
            formatted_messages = [
                {"role": "system", "content": system_context},
                formatted_messages[-1],
            ]

        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream,
        )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
