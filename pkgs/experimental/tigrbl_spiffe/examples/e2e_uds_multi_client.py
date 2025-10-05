import asyncio
from typing import List

from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.svid import Svid

from _e2e_shared import EchoServerASGI, make_client_for_asgi_app

UDS = "unix:///tmp/spire-agent/public/api.sock"

async def make_token(plugin: TigrblSpiffePlugin) -> str:
    ctx_fetch = {**plugin.ctx_extras(), "payload": {"remote": True, "kind": "jwt", "aud": ["echo"]}}
    jwt_row = await Svid.handlers.read.raw(ctx_fetch)
    return jwt_row["material"].decode("utf-8")

async def call_server(client, token: str) -> dict:
    resp = await client.get("/echo", headers={"Authorization": f"Bearer {token}"})
    return resp.json()

async def main():
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="uds", address=UDS))
    app = EchoServerASGI(plugin=plugin)
    client = await make_client_for_asgi_app(app)

    # Acquire tokens concurrently (each client gets its own JWT-SVID over UDS)
    tokens: List[str] = await asyncio.gather(*[make_token(plugin) for _ in range(5)])

    # Make concurrent calls to the server
    results = await asyncio.gather(*[call_server(client, tok) for tok in tokens])

    print("MULTI CLIENTS -> {} responses".format(len(results)))
    for i, r in enumerate(results, 1):
        print(f"[{i}] ok={r.get('ok')} principal={r.get('principal')}")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
