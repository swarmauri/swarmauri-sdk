from typing import List, Literal

from pydantic import SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.MistralModel import MistralModel


@ComponentBase.register_type(VLMBase, "MistralVLM")
class MistralVLM(VLMBase):
    """
    MistralVLM is a compatibility VLM facade over ``MistralModel`` for
    multimodal workflows.
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        *MistralModel.model_fields["allowed_models"].default
    ]
    name: str = MistralModel.model_fields["allowed_models"].default[0]
    type: Literal["MistralVLM"] = "MistralVLM"
    timeout: float = 600.0

    def _delegate(self) -> MistralModel:
        return MistralModel(
            api_key=self.api_key,
            name=self.name,
            timeout=self.timeout,
        )

    def predict_vision(
        self,
        conversation: Conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> Conversation:
        return self._delegate().predict(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            safe_prompt=safe_prompt,
        )

    async def apredict_vision(
        self,
        conversation: Conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> Conversation:
        return await self._delegate().apredict(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            safe_prompt=safe_prompt,
        )

    def batch(
        self,
        conversations: List[Conversation],
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> List[Conversation]:
        return self._delegate().batch(
            conversations=conversations,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            safe_prompt=safe_prompt,
        )

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        return await self._delegate().abatch(
            conversations=conversations,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            safe_prompt=safe_prompt,
            max_concurrent=max_concurrent,
        )

    def stream(
        self,
        conversation: Conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        safe_prompt: bool = False,
    ):
        yield from self._delegate().stream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safe_prompt=safe_prompt,
        )

    async def astream(
        self,
        conversation: Conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        safe_prompt: bool = False,
    ):
        async for chunk in self._delegate().astream(
            conversation=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safe_prompt=safe_prompt,
        ):
            yield chunk
