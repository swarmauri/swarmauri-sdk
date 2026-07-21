from typing import List, Literal, Optional

from pydantic import SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.OpenAIModel import OpenAIModel


@ComponentBase.register_type(VLMBase, "OpenAIVLM")
class OpenAIVLM(VLMBase):
    """
    OpenAIVLM is a compatibility VLM facade over ``OpenAIModel`` for
    multimodal image-first workflows.

    Args:
        api_key: API key for OpenAI access.
        allowed_models: List of allowed model names.
        name: Default model name to use.
        timeout: Request timeout in seconds.
    """

    api_key: SecretStr
    allowed_models: List[str] = [*OpenAIModel.allowed_models]
    name: str = OpenAIModel.allowed_models[0]
    type: Literal["OpenAIVLM"] = "OpenAIVLM"
    timeout: float = 600.0

    def _delegate(self) -> OpenAIModel:
        return OpenAIModel(
            api_key=self.api_key,
            name=self.name,
            timeout=self.timeout,
        )

    def predict_vision(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        return self._delegate().predict(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop or [],
        )

    async def apredict_vision(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        return await self._delegate().apredict(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop or [],
        )

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> List[Conversation]:
        return self._delegate().batch(
            conversations=conversations,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop or [],
        )

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        return await self._delegate().abatch(
            conversations=conversations,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop or [],
            max_concurrent=max_concurrent,
        )

    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ):
        yield from self._delegate().stream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop or [],
        )

    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ):
        async for chunk in self._delegate().astream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop or [],
        ):
            yield chunk
