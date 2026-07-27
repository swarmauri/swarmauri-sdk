from typing import List, Literal

from pydantic import SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.GeminiProModel import GeminiProModel


@ComponentBase.register_type(VLMBase, "GeminiVLM")
class GeminiVLM(VLMBase):
    """
    GeminiVLM is a compatibility VLM facade over ``GeminiProModel`` for
    multimodal image-first workflows.
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        *GeminiProModel.model_fields["allowed_models"].default
    ]
    name: str = GeminiProModel.model_fields["allowed_models"].default[0]
    type: Literal["GeminiVLM"] = "GeminiVLM"
    timeout: float = 600.0

    def _delegate(self) -> GeminiProModel:
        return GeminiProModel(
            api_key=self.api_key,
            name=self.name,
            timeout=self.timeout,
        )

    def predict_vision(
        self,
        conversation: Conversation,
        temperature: float = 1.0,
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
        temperature: float = 1.0,
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
        temperature: float = 1.0,
        max_tokens: int = 256,
    ) -> List[Conversation]:
        return [
            self._delegate().predict(
                conversation=conversation,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conversation in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 1.0,
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
        temperature: float = 1.0,
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
        temperature: float = 1.0,
        max_tokens: int = 256,
    ):
        async for chunk in self._delegate().astream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk
