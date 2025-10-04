import asyncio
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tls.adapters import httpx_client_with_tls

async def main():
    # Client builds an mTLS httpx client using TlsHelper, which pulls x509-SVID from Workload API on demand.
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="uds", address="unix:///tmp/spire-agent/public/api.sock"))
    tls = plugin.ctx_extras()["tls_helper"]

    client = await httpx_client_with_tls("https://my-mtls-server.example", tls)
    try:
        r = await client.get("/mtls/echo")
        print("client->server (mtls) status:", r.status_code)
        print("body:", r.text[:200])
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
