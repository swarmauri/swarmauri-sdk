import requests
import json
from typing import List, Dict, Literal, Optional
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class OpenRouterModel(LLMBase):
    api_key: str
    allowed_models: List[str] = [
        "aetherwiing/mn-starcannon-12b",
        "ai21/jamba-1-5-large",
        "ai21/jamba-1-5-mini",
        "ai21/jamba-instruct",
        "alpindale/goliath-120b",
        "alpindale/magnum-72b",
        "anthropic/claude-1",
        "anthropic/claude-1.2",
        "anthropic/claude-2",
        "anthropic/claude-2.0",
        "anthropic/claude-2.0:beta",
        "anthropic/claude-2.1",
        "anthropic/claude-2.1:beta",
        "anthropic/claude-2:beta",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-haiku:beta",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-opus:beta",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-sonnet:beta",
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-sonnet:beta",
        "anthropic/claude-instant-1",
        "anthropic/claude-instant-1.0",
        "anthropic/claude-instant-1.1",
        "anthropic/claude-instant-1:beta",
        "austism/chronos-hermes-13b",
        "cognitivecomputations/dolphin-mixtral-8x22b",
        "cognitivecomputations/dolphin-mixtral-8x7b",
        "cohere/command",
        "cohere/command-r",
        "cohere/command-r-03-2024",
        "cohere/command-r-08-2024",
        "cohere/command-r-plus",
        "cohere/command-r-plus-04-2024",
        "cohere/command-r-plus-08-2024",
        "databricks/dbrx-instruct",
        "deepseek/deepseek-chat",
        "google/gemini-flash-1.5",
        "google/gemini-flash-1.5-exp",
        "google/gemini-flash-8b-1.5-exp",
        "google/gemini-pro",
        "google/gemini-pro-1.5",
        "google/gemini-pro-1.5-exp",
        "google/gemini-pro-vision",
        "google/gemma-2-27b-it",
        "google/gemma-2-9b-it",
        "google/gemma-2-9b-it:free",
        "google/palm-2-chat-bison",
        "google/palm-2-chat-bison-32k",
        "google/palm-2-codechat-bison",
        "google/palm-2-codechat-bison-32k",
        "gryphe/mythomax-l2-13b",
        "gryphe/mythomax-l2-13b:extended",
        "gryphe/mythomax-l2-13b:nitro",
        "gryphe/mythomist-7b",
        "gryphe/mythomist-7b:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "jondurbin/airoboros-l2-70b",
        "lizpreciatior/lzlv-70b-fp16-hf",
        "mancer/weaver",
        "mattshumer/reflection-70b",
        "mattshumer/reflection-70b:free",
        "meta-llama/llama-2-13b-chat",
        "meta-llama/llama-3-70b-instruct",
        "meta-llama/llama-3-70b-instruct:nitro",
        "meta-llama/llama-3-8b-instruct",
        "meta-llama/llama-3-8b-instruct:extended",
        "meta-llama/llama-3-8b-instruct:free",
        "meta-llama/llama-3-8b-instruct:nitro",
        "meta-llama/llama-3.1-405b",
        "meta-llama/llama-3.1-405b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-guard-2-8b",
        "microsoft/phi-3-medium-128k-instruct",
        "microsoft/phi-3-medium-128k-instruct:free",
        "microsoft/phi-3-medium-4k-instruct",
        "microsoft/phi-3-mini-128k-instruct",
        "microsoft/phi-3-mini-128k-instruct:free",
        "microsoft/phi-3.5-mini-128k-instruct",
        "microsoft/wizardlm-2-7b",
        "microsoft/wizardlm-2-8x22b",
        "mistralai/codestral-mamba",
        "mistralai/mistral-7b-instruct",
        "mistralai/mistral-7b-instruct-v0.1",
        "mistralai/mistral-7b-instruct-v0.2",
        "mistralai/mistral-7b-instruct-v0.3",
        "mistralai/mistral-7b-instruct:free",
        "mistralai/mistral-7b-instruct:nitro",
        "mistralai/mistral-large",
        "mistralai/mistral-medium",
        "mistralai/mistral-nemo",
        "mistralai/mistral-small",
        "mistralai/mistral-tiny",
        "mistralai/mixtral-8x22b-instruct",
        "mistralai/mixtral-8x7b",
        "mistralai/mixtral-8x7b-instruct",
        "mistralai/mixtral-8x7b-instruct:nitro",
        "mistralai/pixtral-12b:free",
        "neversleep/llama-3-lumimaid-70b",
        "neversleep/llama-3-lumimaid-8b",
        "neversleep/llama-3-lumimaid-8b:extended",
        "neversleep/llama-3.1-lumimaid-8b",
        "neversleep/noromaid-20b",
        "nothingiisreal/mn-celeste-12b",
        "nousresearch/hermes-2-pro-llama-3-8b",
        "nousresearch/hermes-2-theta-llama-3-8b",
        "nousresearch/hermes-3-llama-3.1-405b",
        "nousresearch/hermes-3-llama-3.1-405b:extended",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "nousresearch/hermes-3-llama-3.1-70b",
        "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        "nousresearch/nous-hermes-llama2-13b",
        "nousresearch/nous-hermes-yi-34b",
        "openai/chatgpt-4o-latest",
        "openai/gpt-3.5-turbo",
        "openai/gpt-3.5-turbo-0125",
        "openai/gpt-3.5-turbo-0301",
        "openai/gpt-3.5-turbo-0613",
        "openai/gpt-3.5-turbo-1106",
        "openai/gpt-3.5-turbo-16k",
        "openai/gpt-3.5-turbo-instruct",
        "openai/gpt-4",
        "openai/gpt-4-0314",
        "openai/gpt-4-1106-preview",
        "openai/gpt-4-32k",
        "openai/gpt-4-32k-0314",
        "openai/gpt-4-turbo",
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4-vision-preview",
        "openai/gpt-4o",
        "openai/gpt-4o-2024-05-13",
        "openai/gpt-4o-2024-08-06",
        "openai/gpt-4o-mini",
        "openai/gpt-4o-mini-2024-07-18",
        "openai/gpt-4o:extended",
        "openai/o1-mini",
        "openai/o1-mini-2024-09-12",
        "openai/o1-preview",
        "openai/o1-preview-2024-09-12",
        "openchat/openchat-7b",
        "openchat/openchat-7b:free",
        "openrouter/auto",
        "perplexity/llama-3-sonar-large-32k-chat",
        "perplexity/llama-3-sonar-large-32k-online",
        "perplexity/llama-3-sonar-small-32k-chat",
        "perplexity/llama-3-sonar-small-32k-online",
        "perplexity/llama-3.1-sonar-huge-128k-online",
        "perplexity/llama-3.1-sonar-large-128k-chat",
        "perplexity/llama-3.1-sonar-large-128k-online",
        "perplexity/llama-3.1-sonar-small-128k-chat",
        "perplexity/llama-3.1-sonar-small-128k-online",
        "pygmalionai/mythalion-13b",
        "qwen/qwen-110b-chat",
        "qwen/qwen-2-72b-instruct",
        "qwen/qwen-2-7b-instruct",
        "qwen/qwen-2-7b-instruct:free",
        "qwen/qwen-2-vl-7b-instruct:free",
        "qwen/qwen-72b-chat",
        "sao10k/fimbulvetr-11b-v2",
        "sao10k/l3-euryale-70b",
        "sao10k/l3-lunaris-8b",
        "sao10k/l3-stheno-8b",
        "sao10k/l3.1-euryale-70b",
        "sophosympatheia/midnight-rose-70b",
        "teknium/openhermes-2.5-mistral-7b",
        "togethercomputer/stripedhyena-nous-7b",
        "undi95/remm-slerp-l2-13b",
        "undi95/remm-slerp-l2-13b:extended",
        "undi95/toppy-m-7b",
        "undi95/toppy-m-7b:free",
        "undi95/toppy-m-7b:nitro",
        "xwin-lm/xwin-lm-70b",
    ]
    name: str = "mistralai/pixtral-12b:free"
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
        print(response_json)
        message_content = response_json["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))
        return conversation
