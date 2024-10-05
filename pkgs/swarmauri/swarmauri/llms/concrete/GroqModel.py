import json
from typing import List, Optional, Dict, Literal
from groq import Groq
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class GroqModel(LLMBase):
    """Provider resources: https://console.groq.com/docs/models"""

    api_key: str
    allowed_models: List[str] = [
        'gemma-7b-it',
        'gemma2-9b-it',
        'llama-3.1-70b-versatile',
        'llama-3.1-8b-instant',
        'llama-3.2-11b-text-preview',
        'llama-3.2-1b-preview',
        'llama-3.2-3b-preview',
        'llama-3.2-90b-text-preview',
        'llama-guard-3-8b',
        'llama3-70b-8192',
        'llama3-8b-8192',
        'llama3-groq-70b-8192-tool-use-preview',
        'llama3-groq-8b-8192-tool-use-preview',
        'llava-v1.5-7b-4096-preview',
        'mixtral-8x7b-32768'
    ]
    name: str = "gemma-7b-it"
    type: Literal["GroqModel"] = "GroqModel"

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
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> str:

        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        stop = stop or []

        response_format = {"type": "json_object"} if enable_json else None
        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop,
        )

        result = json.loads(response.json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))
        return conversation
