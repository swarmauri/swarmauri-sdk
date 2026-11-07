import pytest

from swarmauri_base.live_models.events.TextDeltaEvent import TextDeltaEvent
from swarmauri_base.live_models.inputs.TextInput import TextInput
from swarmauri_base.live_models.LiveSessionBase import LiveSessionBase
from swarmauri_base.live_models.LiveSessionState import LiveSessionState


class _Session(LiveSessionBase):
    sent: list[str] = []

    async def _asend_impl(self, input_data: TextInput) -> None:
        self.sent.append(input_data.payload)

    async def _aclose_impl(self) -> None:
        return None


@pytest.mark.asyncio
async def test_live_session_lifecycle_and_event_delivery() -> None:
    session = _Session(sent=[])
    session.mark_open()

    await session.asend(TextInput(payload="hello"))
    await session.emit(TextDeltaEvent(payload="world"))
    event = await anext(session.astream())
    await session.aclose()

    assert session.sent == ["hello"]
    assert event.payload == "world"
    assert session.state == LiveSessionState.CLOSED.value


@pytest.mark.asyncio
async def test_live_session_rejects_send_before_open() -> None:
    session = _Session(sent=[])

    with pytest.raises(RuntimeError, match="not open"):
        await session.asend(TextInput(payload="hello"))
