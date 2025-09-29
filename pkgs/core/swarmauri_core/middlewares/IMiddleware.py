from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, MutableMapping, Protocol, TypedDict

"""Middleware interface module.
Defines the core interface for all middleware implementations.
"""


Scope = MutableMapping[str, Any]
"""Type alias representing an ASGI scope."""


class Message(TypedDict, total=False):
    """A minimal representation of an ASGI message."""

    type: str
    body: bytes
    more_body: bool
    status: int
    headers: "list[tuple[bytes, bytes]]"


class ReceiveCallable(Protocol):
    """Protocol describing an awaitable callable returning an ASGI message."""

    def __call__(self) -> Awaitable[Message]:  # pragma: no cover - protocol definition
        ...


class SendCallable(Protocol):
    """Protocol describing an awaitable callable accepting an ASGI message."""

    def __call__(
        self, message: Message
    ) -> Awaitable[None]:  # pragma: no cover - protocol
        ...


ASGIApp = Callable[[Scope, ReceiveCallable, SendCallable], Awaitable[None]]


class IMiddleware(ABC):
    """Abstract base class for all middleware implementations."""

    @abstractmethod
    async def on_scope(self, scope: Scope) -> Scope:
        """Hook executed when a new scope is received."""

    @abstractmethod
    async def on_receive(self, scope: Scope, message: Message) -> Message:
        """Hook executed for each message pulled from the receive callable."""

    @abstractmethod
    async def on_send(self, scope: Scope, message: Message) -> Message:
        """Hook executed before messages are forwarded to the downstream send."""

    @abstractmethod
    async def __call__(
        self, scope: Scope, receive: ReceiveCallable, send: SendCallable
    ) -> None:
        """Execute the middleware for the provided ASGI scope."""
