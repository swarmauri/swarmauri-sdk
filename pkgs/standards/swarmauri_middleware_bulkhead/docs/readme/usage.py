import asyncio

from starlette.requests import Request

from swarmauri_middleware_bulkhead import BulkheadMiddleware


async def main() -> None:
    bulkhead = BulkheadMiddleware(max_concurrency=2)
    active_requests = 0
    peak_active_requests = 0
    lock = asyncio.Lock()

    async def call_next(request: Request):
        nonlocal active_requests, peak_active_requests
        async with lock:
            active_requests += 1
            peak_active_requests = max(peak_active_requests, active_requests)

        try:
            await asyncio.sleep(0.05)
            return {"path": request.scope.get("path"), "handled": True}
        finally:
            async with lock:
                active_requests -= 1

    async def simulate_request(idx: int):
        request = Request(scope={"type": "http", "path": f"/task/{idx}"})
        return await bulkhead.dispatch(request, call_next)

    responses = await asyncio.gather(*(simulate_request(i) for i in range(5)))

    assert peak_active_requests <= bulkhead.max_concurrency
    print("Peak concurrent requests:", peak_active_requests)
    print("Responses:", responses)


if __name__ == "__main__":
    asyncio.run(main())
