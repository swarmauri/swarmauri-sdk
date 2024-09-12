import json
from typing import List, Dict, Literal, Optional
import requests
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class PerplexityModel(LLMBase):
    api_key: str
    allowed_models: List[str] = [
        "llama-3-sonar-small-32k-chat",
        "llama-3-sonar-small-32k-online",
        "llama-3-sonar-large-32k-chat",
        "llama-3-sonar-large-32k-online",
        "llama-3-8b-instruct",
        "llama-3-70b-instruct",
        "llama-3.1-70b-instruct",
    ]
    name: str = "llama-3.1-70b-instruct"
    type: Literal["PerplexityModel"] = "PerplexityModel"

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
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ):

        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": True,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(url, json=payload, headers=headers)
        message_content = response.text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation
