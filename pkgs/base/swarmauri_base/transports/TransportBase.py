"""Capability-aware base transport implementation."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Any, Literal

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.ITransport import ITransport
from swarmauri_core.transports.enums import Cast, Feature


class CapabilityError(RuntimeError):
    """Raised when a transport is used without the required capabilities."""


def _require_caps(
    caps: TransportCapabilities,
    casts: set[Cast] | None = None,
    features: set[Feature] | None = None,
) -> None:
    """Validate that the capability set contains the requested features."""

    if casts and not casts.issubset(caps.casts):
        missing = casts - caps.casts
        raise CapabilityError(f"missing casts: {missing}")
    if features and not features.issubset(caps.features):
        missing = features - caps.features
        raise CapabilityError(f"missing features: {missing}")


@ComponentBase.register_model()
class TransportBase(ComponentBase, ITransport):
    """Base class providing capability-safe server/client context managers."""

    allowed_protocols: list[str] = []
    resource: str = Field(default=ResourceTypes.TRANSPORT.value, frozen=True)
    type: Literal["TransportBase"] = "TransportBase"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    _server_bind_kwargs: dict[str, Any] = PrivateAttr(default_factory=dict)
    _client_connect_kwargs: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        if data.get("name") is None:
            data["name"] = self.__class__.__name__
        super().__init__(**data)

    # ------------------------------------------------------------------
    # Core capability advertisement
    # ------------------------------------------------------------------
    def supports(self) -> TransportCapabilities:
        """Advertise the capabilities of the concrete transport."""

        raise NotImplementedError

    # ------------------------------------------------------------------
    # server/client context wrappers that *ride with* the transport
    # ------------------------------------------------------------------
    def server(
        self, **bind_kwargs: Any
    ) -> AbstractAsyncContextManager["TransportBase"]:
        """Create a context manager that starts the transport's server side."""

        caps = self.supports()
        self._server_bind_kwargs = dict(bind_kwargs)
        _require_caps(caps, casts={Cast.UNICAST})
        transport = self

        class _ServerCtx(AbstractAsyncContextManager[TransportBase]):
            async def __aenter__(self) -> TransportBase:
                await transport._start_server(**bind_kwargs)
                return transport

            async def __aexit__(self, exc_type, exc, tb) -> None:
                await transport._stop_server()

        return _ServerCtx()

    def client(
        self, **connect_kwargs: Any
    ) -> AbstractAsyncContextManager["TransportBase"]:
        """Create a context manager that opens the transport's client side."""

        caps = self.supports()
        self._client_connect_kwargs = dict(connect_kwargs)
        _require_caps(caps, casts={Cast.UNICAST})
        transport = self

        class _ClientCtx(AbstractAsyncContextManager[TransportBase]):
            async def __aenter__(self) -> TransportBase:
                await transport._open_client(**connect_kwargs)
                return transport

            async def __aexit__(self, exc_type, exc, tb) -> None:
                await transport._close_client()

        return _ClientCtx()

    # ------------------------------------------------------------------
    # lifecycle hooks implemented by concrete transports
    # ------------------------------------------------------------------
    async def _start_server(self, **bind_kwargs: Any) -> None:
        raise NotImplementedError

    async def _stop_server(self) -> None:
        raise NotImplementedError

    async def _open_client(self, **connect_kwargs: Any) -> None:
        raise NotImplementedError

    async def _close_client(self) -> None:
        raise NotImplementedError
