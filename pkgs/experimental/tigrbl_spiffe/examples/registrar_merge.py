import asyncio
from tigrbl_spiffe.plugin import TigrblSpiffePlugin
from tigrbl_spiffe.adapters import Endpoint
from tigrbl_spiffe.tables.registrar import Registrar

async def main():
    plugin = TigrblSpiffePlugin(workload_endpoint=Endpoint(scheme="http", address="http://localhost:8080"),
                                server_endpoint=Endpoint(scheme="https", address="https://spire.example.com"))
    ctx = plugin.ctx_extras()
    ctx["payload"] = {"remote": True}
    try:
        entries = await Registrar.handlers.read.raw(ctx)
        print("Remote registrar entries:", entries)
    except Exception as e:
        print("Note: remote registrar read requires a gateway:", e)

if __name__ == "__main__":
    asyncio.run(main())
