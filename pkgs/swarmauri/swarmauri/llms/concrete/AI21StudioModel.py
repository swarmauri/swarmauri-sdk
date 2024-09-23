import logging
import json
from typing import List, Dict, Literal
import ai21
from ai21.models.chat import ChatMessage
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class AI21StudioModel(LLMBase):
    """
    Provider resources: https://docs.ai21.com/reference/jamba-15-api-ref

    """

    api_key: str
    allowed_models: List[str] = [
        "jamba-1.5-large",
        "jamba-1.5-mini",
    ]
    name: str = "jamba-1.5-mini"
    type: Literal["AI21StudioModel"] = "AI21StudioModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [
            ChatMessage(content=message.content, role=message.role)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
        stream=False,
    ):
        """
        Args:
            top_p (0.01 to 1.0)  Limit the pool of next tokens in each step to the top {top_p*100} percentile of possible tokens
            stop: stop the message when model generates one of these strings.
            n: how many chat responses to generate
            stream: whether or not to stream the result, for long answers. if set to true n must be 1.
        """

        # Create client
        client = ai21.AI21Client(api_key=self.api_key)

        # Get system_context from last message with system context in it
        formatted_messages = self._format_messages(conversation.history)

        parameters = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop,
            "n": n,
            "stream": stream,
        }

        response = client.chat.completions.create(**parameters)
        logging.info(f"response: {response}")

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
