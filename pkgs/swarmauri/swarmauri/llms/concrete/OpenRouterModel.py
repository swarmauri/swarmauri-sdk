import requests
import json
from typing import List, Dict, Literal, Optional
from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class OpenRouterModel(LLMBase):
    """
    Provider resources: https://openrouter.ai/models
    """

    api_key: str
    allowed_models: List[str] = [
        "ai21/jamba-1-5-large",
        "ai21/jamba-1-5-mini",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-haiku:beta",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-opus:beta",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-sonnet:beta",
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-sonnet:beta",
        "deepseek/deepseek-chat",
        "google/gemini-flash-1.5",
        #"google/gemini-flash-1.5-exp", # experimental model continues to report 429 errors
        #"google/gemini-flash-8b-1.5-exp", # experimental model continues to report 429 errors
        "google/gemini-pro",
        "google/gemini-pro-1.5",
        #"google/gemini-pro-1.5-exp", # experimental model continues to report 429 errors
        "google/gemini-pro-vision",
        "meta-llama/llama-3-70b-instruct",
        "meta-llama/llama-3.1-405b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mistral-7b-instruct",
        "mistralai/mistral-7b-instruct-v0.1",
        "mistralai/mistral-7b-instruct-v0.3",
        "mistralai/mistral-large",
        "mistralai/mistral-nemo",
        "mistralai/mistral-small",
        "mistralai/mixtral-8x22b-instruct",
        "mistralai/mixtral-8x7b-instruct",
        "mistralai/mixtral-8x7b-instruct:nitro",
        "openai/gpt-3.5-turbo",
        "openai/gpt-3.5-turbo-0125",
        "openai/gpt-3.5-turbo-0613",
        "openai/gpt-3.5-turbo-1106",
        "openai/gpt-3.5-turbo-16k",
        "openai/gpt-4",
        "openai/gpt-4-32k",
        "openai/gpt-4-1106-preview",
        "openai/gpt-4-turbo",
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4-vision-preview",
        "openai/gpt-4o",
        "openai/gpt-4o-2024-05-13",
        "openai/gpt-4o-2024-08-06",
        "openai/gpt-4o-extended",
        "openai/gpt-4o-mini",
        "openai/gpt-4o-mini-2024-07-18",
        "qwen/qwen-2.5-72b-instruct",
    ]
    name: str = "mistralai/mistral-7b-instruct-v0.1"
    type: Literal["OpenRouterModel"] = "OpenRouterModel"
    app_name: Optional[str] = None
    site_url: Optional[str] = None

    def _validate_parameters(
        self,
        temperature,
        max_tokens,
        top_p,
        top_k,
        frequency_penalty,
        presence_penalty,
        repetition_penalty,
    ):
        if not (0 <= temperature <= 2):
            raise ValueError("Temperature must be between 0 and 2.")

        if not (0 <= top_p <= 1):
            raise ValueError("Top P must be between 0 and 1.")

        if top_k is not None and top_k < 1:
            raise ValueError("Top K must be 1 or higher.")

        if not (-2 <= frequency_penalty <= 2):
            raise ValueError("Frequency penalty must be between -2 and 2.")

        if not (-2 <= presence_penalty <= 2):
            raise ValueError("Presence penalty must be between -2 and 2.")

        if not (0 <= repetition_penalty <= 2):
            raise ValueError("Repetition penalty must be between 0 and 2.")

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

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
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = 1,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        stream: bool = False,
        response_format: Optional[Dict[str, str]] = None,
    ):

        self._validate_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            repetition_penalty=repetition_penalty,
        )
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        url = "https://openrouter.ai/api/v1/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "repetition_penalty": repetition_penalty,
            "min_p": min_p,
            "top_a": top_a,
            "stream": stream,
            "response_format": response_format,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.app_name:
            headers["X-Title"] = self.app_name
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url

        if system_context:
            payload["messages"] = [
                {"role": "system", "content": system_context},
                formatted_messages[0],
            ]
            response = requests.post(url, json=payload, headers=headers)
        else:
            response = requests.post(url, json=payload, headers=headers)
        response_json = json.loads(response.text)
        if "error" in response_json:
            raise ValueError(response_json["error"])
        print(response_json)
        message_content = response_json["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))
        return conversation
