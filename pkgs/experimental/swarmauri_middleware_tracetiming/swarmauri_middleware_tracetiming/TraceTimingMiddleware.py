import secrets
import time
from typing import Any, Callable

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.middlewares.IMiddleware import Headers, Message, Scope


class HeaderCollection:
    """Utility for case-insensitive access/update of ASGI byte headers."""

    def __init__(self, headers: Headers | None = None) -> None:
        self._headers: Headers = list(headers or [])

    @property
    def items(self) -> Headers:
        return self._headers

    def get(self, key: bytes) -> bytes | None:
        for header_key, header_value in self._headers:
            if header_key.lower() == key:
                return header_value
        return None

    def set(self, key: str, value: str) -> None:
        key_bytes = key.lower().encode("latin-1")
        value_bytes = value.encode("latin-1")

        for index, (header_key, _) in enumerate(self._headers):
            if header_key.lower() == key_bytes:
                self._headers[index] = (header_key, value_bytes)
                return

        self._headers.append((key_bytes, value_bytes))


def _gen_trace_ids() -> str:
    version = "00"
    trace_id = secrets.token_hex(16)
    parent_id = secrets.token_hex(8)
    flags = "01"
    return f"{version}-{trace_id}-{parent_id}-{flags}"


@ComponentBase.register_type(MiddlewareBase, "TraceTimingMiddleware")
class TraceTimingMiddleware(MiddlewareBase):
    """ASGI middleware for trace propagation and Server-Timing instrumentation."""

    def __init__(
        self,
        app: Any = None,
        edge_ms_getter: Callable[[Scope], float | None] | None = None,
        timing_allow_origin: str = "*",
        **kwargs: Any,
    ) -> None:
        super().__init__(app=app, **kwargs)
        self.edge_ms_getter = edge_ms_getter or (lambda scope: None)
        self.timing_allow_origin = timing_allow_origin

    async def on_scope(self, scope: Scope) -> Scope:
        if scope.get("type") != "http":
            return scope

        request_headers = HeaderCollection(scope.get("headers"))

        traceparent_bytes = request_headers.get(b"traceparent")
        tracestate_bytes = request_headers.get(b"tracestate")

        if not traceparent_bytes:
            traceparent_bytes = _gen_trace_ids().encode("latin-1")
            request_headers.items.append((b"traceparent", traceparent_bytes))
            scope["headers"] = request_headers.items

        scope["_swarmauri_traceparent"] = traceparent_bytes.decode("latin-1")
        scope["_swarmauri_tracestate"] = (
            tracestate_bytes.decode("latin-1") if tracestate_bytes else None
        )
        scope["_swarmauri_start_time"] = time.perf_counter()
        scope["_swarmauri_edge_duration_ms"] = self.edge_ms_getter(scope)

        return scope

    async def on_send(self, scope: Scope, message: Message) -> Message:
        if scope.get("type") != "http" or message.get("type") != "http.response.start":
            return message

        response_headers = HeaderCollection(message.get("headers"))
        start_time = scope.get("_swarmauri_start_time", time.perf_counter())
        app_duration_ms = (time.perf_counter() - start_time) * 1000.0

        server_timing_parts = [f"app;dur={app_duration_ms:.1f}"]
        edge_duration_ms = scope.get("_swarmauri_edge_duration_ms")
        if edge_duration_ms is not None:
            server_timing_parts.append(f"edge;dur={edge_duration_ms:.1f}")

        response_headers.set("server-timing", ",".join(server_timing_parts))
        response_headers.set("timing-allow-origin", self.timing_allow_origin)

        traceparent = scope.get("_swarmauri_traceparent")
        if traceparent:
            response_headers.set("traceparent", traceparent)

        tracestate = scope.get("_swarmauri_tracestate")
        if tracestate:
            response_headers.set("tracestate", tracestate)

        message["headers"] = response_headers.items
        return message
