from unittest.mock import AsyncMock, patch

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_base.live_models.LiveSessionBase import LiveSessionBase
from swarmauri_base.live_models.SyncLiveSessionBase import SyncLiveSessionBase
from swarmauri_live_model_amazon_nova import (
    NovaSonicLiveModel,
    NovaSonicLiveSession,
)
from swarmauri_tests_component import (
    ComponentSpec,
    MethodSpec,
    live_session_method_specs,
)


class _Transport:
    async def aconnect(self, *args, **kwargs):
        return object()


class _Session:
    session_id = "test"
    state = "open"
    terminal_error = None

    async def aclose(self):
        self.state = "closed"


def _connect(model):
    model.aconnect = AsyncMock(return_value=_Session())
    session = model.connect(LiveConfigBase())
    assert isinstance(session, SyncLiveSessionBase)
    session.close()


async def _aconnect(model):
    model.transport = _Transport()
    with patch(
        "swarmauri_live_model_amazon_nova.NovaSonicLiveModel.NovaSonicLiveSession.create",
        new=AsyncMock(return_value="session"),
    ):
        assert await model.aconnect(LiveConfigBase()) == "session"


class _EventStreamConnection:
    def __init__(self):
        self.sent = []

    async def asend(self, event):
        self.sent.append(event)

    async def aiter_events(self):
        if False:
            yield None

    async def aclose(self):
        pass


async def _create_session(_session):
    connection = _EventStreamConnection()
    session = await NovaSonicLiveSession.create(
        connection, [{"event": {"sessionStart": {}}}]
    )
    await session.await_closed()
    assert connection.sent
    assert session.state == "closed"


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            NovaSonicLiveModel,
            {},
            "LiveModel",
            "amazon.nova-sonic-v1:0",
            LiveModelBase,
            excluded_fields=("transport",),
            method_specs=(
                MethodSpec("connect", _connect),
                MethodSpec("aconnect", _aconnect),
            ),
        ),
        ComponentSpec(
            NovaSonicLiveSession,
            {},
            "LiveSession",
            None,
            LiveSessionBase,
            method_specs=live_session_method_specs(_create_session),
        ),
    ]
