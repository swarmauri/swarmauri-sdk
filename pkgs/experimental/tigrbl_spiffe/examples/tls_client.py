import asyncio
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tls.adapters import httpx_client_with_tls

async def main():
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="uds", address="unix:///tmp/spire-agent/public/api.sock"))
    tls = plugin.ctx_extras()["tls_helper"]
    client = await httpx_client_with_tls("https://example.com", tls)
    try:
        r = await client.get("/")
        print("Status:", r.status_code)
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
