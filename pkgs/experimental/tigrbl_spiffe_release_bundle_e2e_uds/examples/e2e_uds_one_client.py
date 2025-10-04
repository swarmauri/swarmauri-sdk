import asyncio

from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.svid import Svid

from _e2e_shared import EchoServerASGI, make_client_for_asgi_app

UDS = "unix:///tmp/spire-agent/public/api.sock"

async def main():
    # Configure plugin: both server and client consult the same agent over UDS when needed
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="uds", address=UDS))

    # Start in-process ASGI server using SpiffeAuthn (server-side)
    app = EchoServerASGI(plugin=plugin)
    client = await make_client_for_asgi_app(app)

    # Client side: fetch a JWT-SVID from the agent over UDS, then call server with Bearer token
    ctx_fetch = {**plugin.ctx_extras(), "payload": {"remote": True, "kind": "jwt", "aud": ["echo"]}}
    jwt_row = await Svid.handlers.read.raw(ctx_fetch)
    token = jwt_row["material"].decode("utf-8")

    # Invoke server endpoint
    resp = await client.get("/echo", headers={"Authorization": f"Bearer {token}"})
    print("ONE CLIENT -> status:", resp.status_code)
    print(resp.json())

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
