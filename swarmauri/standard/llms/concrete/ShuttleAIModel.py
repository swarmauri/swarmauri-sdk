import logging
import json
from typing import List, Dict, Literal
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase 

import requests 

class ShuttleAIModel(LLMBase):
    api_key: str
    allowed_models: List[str] = [
    "shuttle-2-turbo", "shuttle-turbo", "gpt-4o-2024-05-13", "gpt-4-turbo-2024-04-09",
    "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4-1106-vision-preview", "gpt-4-0613",
    "gpt-4-bing", "gpt-4-turbo-bing", "gpt-4-32k-0613", "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-1106", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
    "claude-2.1", "claude-2.0", "claude-instant-1.2", "claude-instant-1.1",
    "claude-instant-1.0", "meta-llama-3-70b-instruct", "meta-llama-3-8b-instruct", "llama-3-sonar-large-32k-online",
    "llama-3-sonar-small-32k-online", "llama-3-sonar-large-32k-chat", "llama-3-sonar-small-32k-chat", "blackbox",
    "blackbox-code", "wizardlm-2-8x22b", "wizardlm-2-70b", "dolphin-2.6-mixtral-8x7b",
    "codestral-latest", "mistral-large", "mistral-next", "mistral-medium",
    "mistral-small", "mistral-tiny", "mixtral-8x7b-instruct-v0.1", "mixtral-8x22b-instruct-v0.1",
    "mistral-7b-instruct-v0.2", "mistral-7b-instruct-v0.1", "nous-hermes-2-mixtral-8x7b", "gemini-1.5-pro-latest",
    "gemini-1.0-pro-latest", "gemini-1.0-pro-vision", "lzlv-70b", "figgs-rp", "cinematika-7b"
    ]
    name: str = "shuttle-2-turbo"
    type: Literal['ShuttleAIModel'] = 'ShuttleAIModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
       # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    
    def predict(self, 
            conversation, 
            temperature=0.7, 
            max_tokens=256, 
            top_p=1, 
            internet=False, 
            citations=False, 
            tone='precise', 
            raw=False, 
            image=None): 

            formatted_messages = self._format_messages(conversation.history) 

            url = "https://api.shuttleai.app/v1/chat/completions" 
            payload = { 
                "model": self.name, 
                "messages": formatted_messages, 
                "max_tokens": max_tokens, 
                "temperature": temperature, 
                "top_p": top_p
            } 

            if raw:
                payload['raw'] = True

            if internet:
                payload['internet'] = True

            # Only include the 'image' field if it's not None
            if image is not None:
                payload["image"] = image

            if self.name in ['gpt-4-bing', 'gpt-4-turbo-bing']: 
                payload['tone'] = tone
                
                # Include citations only if citations is True
                if citations:
                    payload['citations'] = True

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
                message_content = response.json()['choices'][0]['message']['content']
            except KeyError as e:
                logging.info(f"Error parsing response: {response.text}")
                raise e

            conversation.add_message(AgentMessage(content=message_content))  
            return conversation
