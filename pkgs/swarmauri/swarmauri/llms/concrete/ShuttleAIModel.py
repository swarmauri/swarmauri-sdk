import logging
import json
from typing import List, Dict, Literal
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

import requests


class ShuttleAIModel(LLMBase):
    """
    Provider resources: https://docs.shuttleai.com/getting-started/models

    """

    api_key: str
    allowed_models: List[str] = [
        'alibaba-cloud/qwen-2.5-72b-instruct',
     'alibaba-cloud/qwen-2.5-coder-7b',
     'alibaba-cloud/qwen-2.5-math-72b',
     'anthropic/claude-3-5-sonnet-20240620',
     'anthropic/claude-3-haiku-20240307',
     'anthropic/claude-3-opus-20240229',
     'black-forest-labs/flux1-dev',
     'black-forest-labs/flux1-pro',
     'black-forest-labs/flux1-schnell',
     'cliffweitzma/speechify',
     'cohere/command-r',
     'cohere/command-r-08-2024',
     'cohere/command-r-plus',
     'cohere/command-r-plus-08-2024',
     'duckduckgo/search-ddg',
     'elevenlabs/eleven_multilingual_v2',
     'elevenlabs/eleven_turbo_v2_5',
     'google/gemini-1.5-flash',
     'google/gemini-1.5-flash-8b-exp-0827',
     'google/gemini-1.5-flash-exp-0827',
     'google/gemini-1.5-pro',
     'google/gemini-1.5-pro-exp-0827',
     'google/search-google',
     'mattshumer/reflection-llama-3.1-70b',
     'meta-llama/meta-llama-3.1-405b-instruct',
     'meta-llama/meta-llama-3.1-70b-instruct',
     'meta-llama/meta-llama-3.1-8b-instruct',
     'mistralai/codestral-2405',
     'mistralai/mistral-nemo-instruct-2407',
     'openai/chatgpt-4o-latest',
     'openai/dall-e-3',
     'openai/gpt-3.5-turbo-0125',
     'openai/gpt-3.5-turbo-1106',
     'openai/gpt-4-0125-preview',
     'openai/gpt-4-0613',
     'openai/gpt-4-1106-preview',
     'openai/gpt-4-turbo-2024-04-09',
     'openai/gpt-4o-2024-05-13',
     'openai/gpt-4o-2024-08-06',
     'openai/gpt-4o-mini-2024-07-18',
     'openai/o1-mini-2024-09-12',
     'openai/o1-preview-2024-09-12',
     'openai/text-embedding-3-large',
     'openai/text-embedding-3-small',
     'openai/text-moderation-007',
     'openai/tts-1',
     'openai/tts-1-hd',
     'openai/whisper-1',
     'perplexity/llama-3.1-sonar-large-128k-chat',
     'perplexity/llama-3.1-sonar-large-128k-online',
     'perplexity/llama-3.1-sonar-small-128k-chat',
     'perplexity/llama-3.1-sonar-small-128k-online',
     'shuttleai/s1',
     'shuttleai/s1-mini',
     'shuttleai/shuttle-2-diffusion',
     'shuttleai/shuttle-3',
     'shuttleai/shuttle-3-mini',
     'stabilityai/dreamshaperxl-v10',
     'stabilityai/juggernautxl',
     'stabilityai/realistic-vision-v5.1',
     'stabilityai/sdxl',
     'stabilityai/sdxl-inpaint',
     'stabilityai/turbovisionxl',
    ]
    
    name: str = "shuttle-2-turbo"
    type: Literal["ShuttleAIModel"] = "ShuttleAIModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
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
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
    ):

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        if raw:
            payload["raw"] = True

        if internet:
            payload["internet"] = True

        # Only include the 'image' field if it's not None
        if image is not None:
            payload["image"] = image

        if self.name in ["gpt-4-bing", "gpt-4-turbo-bing"]:
            payload["tone"] = tone

            # Include citations only if citations is True
            if citations:
                payload["citations"] = True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Log payload for debugging
        logging.info(f"Payload being sent: {payload}")

        # Send the request
        response = requests.post(url, json=payload, headers=headers)

        # Log response for debugging
        logging.info(f"Response received: {response.text}")

        # Parse response JSON safely
        try:
            message_content = response.json()["choices"][0]["message"]["content"]
        except KeyError as e:
            logging.info(f"Error parsing response: {response.text}")
            raise e

        conversation.add_message(AgentMessage(content=message_content))
        return conversation
