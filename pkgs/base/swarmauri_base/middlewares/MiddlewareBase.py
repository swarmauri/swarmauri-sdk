from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from fastapi import Request, Response

from swarmauri_core.middlewares.IMiddleware import (
    ASGIApp,
    IMiddleware,
    Message,
    ReceiveCallable,
    Scope,
    SendCallable,
)

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class MiddlewareBase(IMiddleware, ComponentBase):
    """Base class for all middleware implementations."""

    resource: Optional[str] = ResourceTypes.MIDDLEWARE.value

    def __init__(self, app: Optional[ASGIApp] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        async def _noop_app(
            scope: Scope, receive: ReceiveCallable, send: SendCallable
        ) -> None:
            return None

        self._app: ASGIApp = app or _noop_app

    def bind(self, app: ASGIApp) -> None:
        """Bind the downstream ASGI application to the middleware."""

        self._app = app

    @property
    def app(self) -> ASGIApp:
        return self._app

    async def call_next(
        self, scope: Scope, receive: ReceiveCallable, send: SendCallable
    ) -> None:
        """Invoke the next ASGI application in the chain."""

        await self.app(scope, receive, send)

    async def on_scope(self, scope: Scope) -> Scope:
        """Hook executed when the middleware receives a scope."""

        return scope

    async def on_receive(self, scope: Scope, message: Message) -> Message:
        """Hook executed for every message received from the client."""

        return message

    async def on_send(self, scope: Scope, message: Message) -> Message:
        """Hook executed before messages are sent to the client."""

        return message

    async def dispatch(
        self, request: Any, call_next: Callable[[Any], Awaitable[Any]]
    ) -> Any:
        """ASGI-compatible dispatch hook.

        Subclasses can override this method to implement traditional request
        processing logic. By default the middleware simply forwards the request
        to the next component in the chain.
        """

        return await call_next(request)

    def _uses_custom_dispatch(self) -> bool:
        return type(self).dispatch is not MiddlewareBase.dispatch

    async def _dispatch_with_request(
        self, scope: Scope, receive: ReceiveCallable, send: SendCallable
    ) -> None:
        try:
            from fastapi import Request, Response
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "FastAPI must be installed to use dispatch-style middleware."
            ) from exc

        request = Request(scope, receive=receive)

        async def call_next(request: Request) -> Response:
            status_code: int = 200
            response_headers: list[tuple[bytes, bytes]] = []
            body_chunks: list[bytes] = []

            async def send_wrapper(message: Message) -> None:
                nonlocal status_code, response_headers
                message_type = message.get("type")
                if message_type == "http.response.start":
                    status_code = message.get("status", 200)
                    response_headers = list(message.get("headers", []))
                elif message_type == "http.response.body":
                    body_chunks.append(message.get("body", b""))
                    if not message.get("more_body", False):
                        return
                else:
                    await send(message)

            await self.app(scope, request.receive, send_wrapper)

            response = Response(content=b"".join(body_chunks), status_code=status_code)
            for key, value in response_headers:
                response.headers[key.decode("latin-1")] = value.decode("latin-1")
            return response

        response = await self.dispatch(request, call_next)
        await response(scope, receive, send)

    async def __call__(
        self, scope: Scope, receive: ReceiveCallable, send: SendCallable
    ) -> None:
        scope = await self.on_scope(scope)

        async def wrapped_receive() -> Message:
            message = await receive()
            return await self.on_receive(scope, message)

        async def wrapped_send(message: Message) -> None:
            filtered = await self.on_send(scope, message)
            await send(filtered)

        if scope.get("type") == "http" and self._uses_custom_dispatch():
            await self._dispatch_with_request(scope, wrapped_receive, wrapped_send)
            return

        await self.call_next(scope, wrapped_receive, wrapped_send)
