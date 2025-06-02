import asyncio, asyncpg
from dqueue.config import settings

async def probe():
    conn = await asyncpg.connect(
        settings.pg_dsn,
        timeout=10         # fail fast
    )
    print(await conn.fetchval("SELECT version();"))
    await conn.close()

asyncio.run(probe())
