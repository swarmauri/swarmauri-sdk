import json
from contextlib import AsyncExitStack, contextmanager
from types import MethodType

import httpx
import pytest

from tigrbl_spiffe.adapters import Endpoint, Txn
from tigrbl_spiffe.middleware.authn import SpiffeAuthn
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.registry import register
from tigrbl_spiffe import registry as registry_module
from tigrbl_spiffe.tables import bundle, registrar, svid, workload
from tigrbl_spiffe.tables.svid import Svid


class EchoServerASGI:
    """Minimal ASGI echo server guarded by SpiffeAuthn."""

    def __init__(self, *, plugin: TigrblSpiffePlugin) -> None:
        self._plugin = plugin
        self._authn = SpiffeAuthn(validator=plugin.ctx_extras()["svid_validator"])

    async def __call__(
        self, scope, receive, send
    ):  # pragma: no cover - invoked via httpx
        if scope["type"] != "http":
            await send({"type": "http.response.start", "status": 500, "headers": []})
            await send({"type": "http.response.body", "body": b"unsupported"})
            return

        # Drain request body (httpx's ASGI transport sends a single event for GET)
        while True:
            event = await receive()
            if event["type"] != "http.request":
                continue
            if not event.get("more_body"):
                break

        headers = {
            k.decode("latin1"): v.decode("latin1") for k, v in scope.get("headers", [])
        }
        ctx = self._plugin.ctx_extras()
        ctx["http"] = {"headers": headers}

        async def endpoint(local_ctx):
            return {"ok": True, "principal": local_ctx.get("principal")}

        result = await self._authn(ctx, endpoint)
        payload = json.dumps(result).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": payload})


@contextmanager
def override_attr(module, name, replacement):
    original = getattr(module, name)
    setattr(module, name, replacement)
    try:
        yield original
    finally:
        setattr(module, name, original)


@pytest.mark.asyncio
async def test_end_to_end_registration_and_jwt_authentication():
    recorded = []

    with override_attr(
        registry_module, "include_model", lambda model: recorded.append(model)
    ):
        register(app=object())

    assert recorded == [
        svid.Svid,
        registrar.Registrar,
        bundle.Bundle,
        workload.Workload,
    ]

    plugin = TigrblSpiffePlugin(
        workload_endpoint=Endpoint(scheme="http", address="http://agent.test")
    )

    token = "header.payload.signature"

    def responder(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/workload/jwtsvid"
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["aud"] == ["echo"]
        return httpx.Response(
            200,
            json={
                "spiffe_id": "spiffe://example/client",
                "jwt": token,
                "aud": ["echo"],
                "nbf": 1,
                "exp": 2,
            },
        )

    transport = httpx.MockTransport(responder)
    mock_client = httpx.AsyncClient(transport=transport, base_url="http://agent.test")
    txn = Txn(kind="http", http=mock_client)

    adapter = plugin.ctx_extras()["spiffe_adapter"]

    validator = plugin.ctx_extras()["svid_validator"]
    calls = []

    async def fake_for_endpoint(self, ep: Endpoint) -> Txn:
        assert ep.scheme == "http"
        assert ep.address == "http://agent.test"
        return txn

    async def tracking_validate(self, *, kind, material, bundle_id, ctx):
        calls.append((kind, material, bundle_id))
        return await original_validate(
            kind=kind, material=material, bundle_id=bundle_id, ctx=ctx
        )

    app = EchoServerASGI(plugin=plugin)
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://asgi.test"
    )
    async with AsyncExitStack() as stack:
        stack.push_async_callback(client.aclose)
        stack.push_async_callback(mock_client.aclose)
        stack.enter_context(
            override_attr(
                adapter,
                "for_endpoint",
                MethodType(fake_for_endpoint, adapter),
            )
        )
        original_validate = stack.enter_context(
            override_attr(
                validator,
                "validate",
                MethodType(tracking_validate, validator),
            )
        )

        ctx_fetch = {
            **plugin.ctx_extras(),
            "payload": {"remote": True, "kind": "jwt", "aud": ["echo"]},
        }
        fetched = await Svid.handlers.read.raw(ctx_fetch)
        assert fetched["spiffe_id"] == "spiffe://example/client"
        assert fetched["kind"] == "jwt"
        assert fetched["audiences"] == ("echo",)
        assert fetched["material"].decode("utf-8") == token

        response = await client.get(
            "/echo",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["ok"] is True
        assert body["principal"] == {
            "spiffe_id": None,
            "token": token,
            "kind": "jwt",
        }

        assert calls == [("jwt", token.encode("utf-8"), None)]
