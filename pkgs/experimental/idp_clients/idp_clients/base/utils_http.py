from __future__ import annotations
import asyncio, httpx, random

class RetryingAsyncClient(httpx.AsyncClient):
    def __init__(self, *, timeout_sec: float = 30.0, **kw):
        super().__init__(timeout=httpx.Timeout(timeout_sec), **kw)

    async def _sleep(self, try_i: int, base: float = 0.25, cap: float = 4.0) -> None:
        delay = min(cap, base * (2 ** try_i)) * (1.0 + 0.1 * random.random())
        await asyncio.sleep(delay)

    async def post_retry(self, url: str, *, max_retries: int = 4, **kw) -> httpx.Response:
        for i in range(max_retries + 1):
            r = await self.post(url, **kw)
            if r.status_code < 500 and r.status_code not in (429,):
                return r
            await self._sleep(i)
        r.raise_for_status()
        return r

    async def get_retry(self, url: str, *, max_retries: int = 4, **kw) -> httpx.Response:
        for i in range(max_retries + 1):
            r = await self.get(url, **kw)
            if r.status_code < 500 and r.status_code not in (429,):
                return r
            await self._sleep(i)
        r.raise_for_status()
        return r
