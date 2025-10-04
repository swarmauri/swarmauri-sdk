import asyncio
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.registrar import Registrar

async def main():
    plugin = TigrblSpiffePlugin(
        workload_endpoint=Endpoint(scheme="http", address="http://localhost:8080"),
        server_endpoint=Endpoint(scheme="https", address="https://spire.example.com"),
    )
    ctx = plugin.ctx_extras()

    # SERVER SIDE: list existing registration entries (via HTTPS gateway)
    ctx_list = {**ctx, "payload": {"remote": True}}
    try:
        entries = await Registrar.handlers.read.raw(ctx_list)
        print("server:list entries ->", entries)
    except Exception as e:
        print("warn: remote read requires a gateway:", e)

    # SERVER SIDE: upsert (merge) an entry
    ctx_merge = {
        **ctx,
        "path_params": {"id": "example-entry"},
        "payload": {"data": {
            "spiffe_id": "spiffe://example.org/ns/default/sa/demo",
            "parent_id": "spiffe://example.org/spire/server",
            "selectors": [["k8s", "ns:default"], ["k8s", "sa:demo"]],
            "ttl_s": 600,
        }},
    }
    try:
        merged = await Registrar.handlers.merge.raw(ctx_merge)
        print("server:merge entry ->", merged)
    except Exception as e:
        print("warn: merge requires server-side gateway or stubs:", e)

if __name__ == "__main__":
    asyncio.run(main())
