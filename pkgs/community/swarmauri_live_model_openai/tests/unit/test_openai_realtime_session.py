import pytest

from swarmauri_live_model_openai import OpenAIRealtimeSession


class ExhaustedConnection:
    async def aiter_messages(self):
        if False:
            yield ""

    async def asend(self, message):
        return None

    async def aclose(self):
        return None


@pytest.mark.asyncio
async def test_receiver_eof_closes_session_and_stream() -> None:
    session = await OpenAIRealtimeSession.create(ExhaustedConnection())

    await session.await_closed()
    events = [event async for event in session.astream()]

    assert events == []
    assert session.state == "closed"
