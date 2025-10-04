import asyncio
import httpx
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.svid import Svid

async def main():
    # Client obtains a JWT-SVID from agent/gateway
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="http", address="http://localhost:8080"))
    ctx = plugin.ctx_extras()

    # Remote read to fetch JWT-SVID
    ctx_jwt = {**ctx, "payload": {"remote": True, "kind": "jwt", "aud": ["my-api"]}}
    jwt_row = await Svid.handlers.read.raw(ctx_jwt)
    token = jwt_row["material"].decode("utf-8")

    # Client calls a server endpoint using Authorization: Bearer <JWT-SVID>
    async with httpx.AsyncClient(base_url="https://my-server.example") as client:
        r = await client.get("/protected/echo", headers={"Authorization": f"Bearer {token}"})
        print("client->server (jwt) status:", r.status_code)
        print("body:", r.text[:200])

if __name__ == "__main__":
    asyncio.run(main())
