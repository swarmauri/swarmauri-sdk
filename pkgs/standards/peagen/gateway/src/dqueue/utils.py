import asyncio, functools


def async_run(coro):
    """Run an async function from sync code (dev helper)."""
    return asyncio.get_event_loop().run_until_complete(coro)


def rate_limited(rate_hz: float):
    def decorator(fn):
        min_delay = 1 / rate_hz

        last = 0.0

        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            nonlocal last
            now = asyncio.get_event_loop().time()
            to_sleep = last + min_delay - now
            if to_sleep > 0:
                await asyncio.sleep(to_sleep)
            last = now
            return await fn(*args, **kwargs)

        return wrapper

    return decorator
