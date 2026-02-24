from __future__ import annotations

from typing import Any

from .raw import GwRawEnvelope


class RawEnvelopeExecutor:
    """Runtime ingress for ASGI3 raw envelopes."""

    def __init__(self, *, app: Any) -> None:
        self.app = app

    async def invoke(self, env: GwRawEnvelope) -> None:
        scope_type = env.scope.get("type")

        if scope_type == "lifespan":
            await self._handle_lifespan(env)
            return

        if scope_type != "http":
            return

        await env.send(
            {
                "type": "http.response.start",
                "status": 501,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await env.send(
            {
                "type": "http.response.body",
                "body": b'{"detail":"runtime raw envelope ingress active"}',
                "more_body": False,
            }
        )

    async def _handle_lifespan(self, env: GwRawEnvelope) -> None:
        while True:
            message = await env.receive()
            message_type = message.get("type")
            if message_type == "lifespan.startup":
                await env.send({"type": "lifespan.startup.complete"})
                continue
            if message_type == "lifespan.shutdown":
                await env.send({"type": "lifespan.shutdown.complete"})
            return
