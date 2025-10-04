import json
from typing import Any, Callable, Awaitable, Dict, Tuple

import httpx

from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.middleware.authn import SpiffeAuthn

class EchoServerASGI:
    """Minimal ASGI app that authenticates requests via SpiffeAuthn middleware
    and echoes the materialized principal. No external ASGI frameworks required.
    """
    def __init__(self, *, plugin: TigrblSpiffePlugin):
        self._plugin = plugin
        self._authn = SpiffeAuthn(validator=plugin.ctx_extras()["svid_validator"])

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await send({"type": "http.response.start", "status": 500, "headers": []})
            await send({"type": "http.response.body", "body": b"unsupported scope"})
            return

        # Collect request body (not used) and headers
        body = b""
        while True:
            event = await receive()
            if event["type"] == "http.request" and event.get("body") and not event.get("more_body"):
                body += event["body"]
                break
            if event["type"] == "http.request" and not event.get("more_body"):
                break

        headers = {k.decode("latin1"): v.decode("latin1") for k, v in scope.get("headers", [])}

        # Create a ctx dict per request, as expected by Tigrbl-style middlewares
        ctx: Dict[str, Any] = self._plugin.ctx_extras()
        ctx["http"] = {"headers": headers}

        async def endpoint(c: Dict[str, Any]) -> Dict[str, Any]:
            principal = c.get("principal") or {}
            return {"ok": True, "principal": principal}

        try:
            result = await self._authn(ctx, endpoint)
            if not isinstance(result, dict):
                result = {"ok": True, "result": str(result)}
            payload = json.dumps(result).encode("utf-8")
            await send({"type": "http.response.start", "status": 200, "headers": [
                (b"content-type", b"application/json"),
            ]})
            await send({"type": "http.response.body", "body": payload})
        except Exception as e:
            payload = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
            await send({"type": "http.response.start", "status": 401, "headers": [
                (b"content-type", b"application/json"),
            ]})
            await send({"type": "http.response.body", "body": payload})


async def make_client_for_asgi_app(app) -> httpx.AsyncClient:
    """Create an httpx client bound to the in-process ASGI app (no network needed)."""
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://app.local")
