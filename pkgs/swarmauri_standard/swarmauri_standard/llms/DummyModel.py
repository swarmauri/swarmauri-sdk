from typing import AsyncIterator, Iterator, List
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_standard.messages.AgentMessage import AgentMessage


@ComponentBase.register_type(LLMBase, "DummyModel")
class DummyModel(LLMBase):
    """A no-op LLM provider for testing."""

    def predict(
        self,
        conversation,
        temperature: float = 0.0,
        max_tokens: int = 0,
        enable_json: bool = False,
        stop: List[str] | None = None,
    ):
        conversation.add_message(AgentMessage(content="dummy"))
        return conversation

    async def apredict(
        self,
        conversation,
        temperature: float = 0.0,
        max_tokens: int = 0,
        enable_json: bool = False,
        stop: List[str] | None = None,
    ):
        conversation.add_message(AgentMessage(content="dummy"))
        return conversation

    def stream(
        self,
        conversation,
        temperature: float = 0.0,
        max_tokens: int = 0,
        stop: List[str] | None = None,
    ) -> Iterator[str]:
        yield "dummy"

    async def astream(
        self,
        conversation,
        temperature: float = 0.0,
        max_tokens: int = 0,
        stop: List[str] | None = None,
    ) -> AsyncIterator[str]:
        yield "dummy"

    def batch(self, *args, **kwargs):
        return ["dummy"]

    async def abatch(self, *args, **kwargs):
        return ["dummy"]
