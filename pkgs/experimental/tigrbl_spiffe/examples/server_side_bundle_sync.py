import asyncio
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.bundle import Bundle

async def main():
    plugin = TigrblSpiffePlugin(
        workload_endpoint=Endpoint(scheme="http", address="http://localhost:8080"),
        server_endpoint=Endpoint(scheme="https", address="https://spire.example.com"),
    )
    ctx = plugin.ctx_extras()

    # SERVER SIDE: read bundle from server (requires gateway)
    ctx_read = {**ctx, "payload": {"filters": {"trust_domain": "example.org"}, "remote": True}}
    try:
        rows = await Bundle.handlers.read.raw(ctx_read)
        print("server:bundle read ->", rows)
    except Exception as e:
        print("warn: remote bundle read requires gateway:", e)

if __name__ == "__main__":
    asyncio.run(main())
