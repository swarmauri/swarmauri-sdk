from typing import List, Literal

from pydantic import SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.AnthropicModel import AnthropicModel


@ComponentBase.register_type(VLMBase, "AnthropicVLM")
class AnthropicVLM(VLMBase):
    """
    AnthropicVLM is a compatibility VLM facade over ``AnthropicModel`` for
    multimodal workflows.
    """

    api_key: SecretStr
    allowed_models: List[str] = [*AnthropicModel.allowed_models]
    name: str = AnthropicModel.allowed_models[0]
    type: Literal["AnthropicVLM"] = "AnthropicVLM"
    timeout: float = 600.0

    def _delegate(self) -> AnthropicModel:
        return AnthropicModel(
            api_key=self.api_key,
            name=self.name,
            timeout=self.timeout,
        )

    def predict_vision(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Conversation:
        return self._delegate().predict(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def apredict_vision(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Conversation:
        return await self._delegate().apredict(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> List[Conversation]:
        return self._delegate().batch(
            conversations=conversations,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        return await self._delegate().abatch(
            conversations=conversations,
            temperature=temperature,
            max_tokens=max_tokens,
            max_concurrent=max_concurrent,
        )

    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ):
        yield from self._delegate().stream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ):
        async for chunk in self._delegate().astream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk
