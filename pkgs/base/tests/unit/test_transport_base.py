import asyncio

import pytest

from swarmauri_base.transports import CapabilityError, TransportBase, _require_caps
from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
    TransportCapabilities,
)


class DummyTransport(TransportBase):
    def __init__(self) -> None:
        super().__init__(name="dummy")
        self.started: list[dict[str, object]] = []
        self.stopped = 0
        self.opened: list[dict[str, object]] = []
        self.closed = 0

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.UDP}),
            io=IOModel.DATAGRAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE}),
            security=SecurityMode.NONE,
            schemes=frozenset({AddressScheme.UDP}),
        )

    async def _start_server(self, **bind_kwargs: object) -> None:  # noqa: D401, ANN001
        self.started.append(dict(bind_kwargs))

    async def _stop_server(self) -> None:  # noqa: D401
        self.stopped += 1

    async def _open_client(self, **connect_kwargs: object) -> None:  # noqa: D401, ANN001
        self.opened.append(dict(connect_kwargs))

    async def _close_client(self) -> None:  # noqa: D401
        self.closed += 1


@pytest.mark.asyncio
async def test_server_context_invokes_lifecycle_hooks() -> None:
    transport = DummyTransport()

    async with transport.server(host="localhost", port=1234):
        assert transport.started == [{"host": "localhost", "port": 1234}]
        await asyncio.sleep(0)

    assert transport.stopped == 1
    assert transport._server_bind_kwargs == {"host": "localhost", "port": 1234}


@pytest.mark.asyncio
async def test_client_context_invokes_lifecycle_hooks() -> None:
    transport = DummyTransport()

    async with transport.client(endpoint="localhost:1234"):
        assert transport.opened == [{"endpoint": "localhost:1234"}]
        await asyncio.sleep(0)

    assert transport.closed == 1
    assert transport._client_connect_kwargs == {"endpoint": "localhost:1234"}


def test_require_caps_enforces_casts_and_features() -> None:
    capabilities = DummyTransport().supports()

    _require_caps(capabilities, casts={Cast.UNICAST})
    _require_caps(capabilities, features={Feature.RELIABLE})

    with pytest.raises(CapabilityError):
        _require_caps(capabilities, casts={Cast.BROADCAST})

    with pytest.raises(CapabilityError):
        _require_caps(capabilities, features={Feature.ORDERED})
