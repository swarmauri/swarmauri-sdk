from typing import List, Dict, Literal
import google.generativeai as genai
from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase
import asyncio

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class GeminiProModel(LLMBase):
    """
    Provider resources: https://deepmind.google/technologies/gemini/pro/
    """

    api_key: str
    allowed_models: List[str] = ["gemini-1.5-pro", "gemini-1.5-flash"]
    name: str = "gemini-1.5-pro"
    type: Literal["GeminiProModel"] = "GeminiProModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ["content", "role"]
        sanitized_messages = [
            message.model_dump(include=message_properties)
            for message in messages
            if message.role != "system"
        ]

        for message in sanitized_messages:
            if message["role"] == "assistant":
                message["role"] = "model"

            # update content naming
            message["parts"] = message.pop("content")

        return sanitized_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float,
        completion_time: float,
    ):
        """
        Prepares and extracts usage data and response timing.
        """

        total_time = prompt_time + completion_time

        usage = UsageData(
            prompt_tokens=usage_data.prompt_token_count,
            completion_tokens=usage_data.candidates_token_count,
            total_tokens=usage_data.total_token_count,
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    def predict(self, conversation, temperature=0.7, max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        next_message = formatted_messages.pop()

        client = genai.GenerativeModel(
            model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_context,
        )

        with DurationManager() as prompt_timer:
            convo = client.start_chat(
                history=formatted_messages,
            )

        with DurationManager() as completion_timer:
            response = convo.send_message(next_message["parts"])
            message_content = convo.last.text

        usage_data = response.usage_metadata

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
            completion_timer.duration,
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    async def apredict(self, conversation, temperature=0.7, max_tokens=256):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.predict, conversation, temperature, max_tokens
        )

    def stream(self, conversation, temperature=0.7, max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        next_message = formatted_messages.pop()

        client = genai.GenerativeModel(
            model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_context,
        )

        with DurationManager() as prompt_timer:
            convo = client.start_chat(
                history=formatted_messages,
            )
            response = convo.send_message(next_message["parts"], stream=True)

        with DurationManager() as completion_timer:
            full_response = ""
            for chunk in response:
                chunk_text = chunk.text
                full_response += chunk_text
                yield chunk_text

        usage_data = response.usage_metadata

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=full_response, usage=usage))

    async def astream(self, conversation, temperature=0.7, max_tokens=256):
        loop = asyncio.get_event_loop()
        stream_gen = self.stream(conversation, temperature, max_tokens)

        def safe_next(gen):
            try:
                return next(gen), False
            except StopIteration:
                return None, True

        while True:
            try:
                chunk, done = await loop.run_in_executor(None, safe_next, stream_gen)
                if done:
                    break
                yield chunk
            except Exception as e:
                print(f"Error in astream: {e}")
                break

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        max_concurrent: int = 5,
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
