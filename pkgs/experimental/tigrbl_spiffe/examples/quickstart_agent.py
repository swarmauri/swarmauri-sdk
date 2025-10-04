import asyncio
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.svid import Svid

async def main():
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="uds", address="unix:///tmp/spire-agent/public/api.sock"))
    # Construct a minimal ctx with extras from plugin (for demo only)
    ctx = plugin.ctx_extras()
    ctx["payload"] = {"remote": True, "kind": "x509", "aud": []}
    # Call the read override directly (frameworks will call handlers)
    row = await Svid.handlers.read.raw(ctx)
    print("Fetched (remote):", {k: v for k, v in row.items() if k != "material"})

if __name__ == "__main__":
    asyncio.run(main())
