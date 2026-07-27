from typing import Literal

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_base.live_models.LiveSessionBase import LiveSessionBase
from swarmauri_base.live_models.events.TextDeltaEvent import TextDeltaEvent
from swarmauri_base.live_models.events.TurnCompleteEvent import (
    TurnCompleteEvent,
)
from swarmauri_base.live_models.inputs.TextInput import TextInput


class EchoSession(LiveSessionBase):
    type: Literal["EchoSession"] = "EchoSession"

    async def _asend_impl(self, input_data) -> None:
        await self.emit(TextDeltaEvent(payload=input_data.payload))
        await self.emit(TurnCompleteEvent())

    async def _aclose_impl(self) -> None:
        return None


class EchoLiveModel(LiveModelBase):
    type: Literal["EchoLiveModel"] = "EchoLiveModel"

    async def aconnect(self, config):
        session = EchoSession()
        session.mark_open()
        return session


def test_sync_session_uses_one_persistent_runtime() -> None:
    session = EchoLiveModel().connect(LiveConfigBase())

    session.send(TextInput(payload="hello"))
    events = session.stream()
    first = next(events)
    second = next(events)

    assert [first.kind, second.kind] == ["text_delta", "turn_complete"]
    assert first.payload == "hello"
    assert session.state == "open"
    session.close()
    assert session.state == "closed"
