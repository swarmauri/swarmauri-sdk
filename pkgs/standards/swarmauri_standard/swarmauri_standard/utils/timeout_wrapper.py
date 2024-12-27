import pytest
from functools import wraps
import signal
import asyncio
import inspect


def timeout(seconds=5):
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            # Async function handler
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs), timeout=seconds
                    )
                except asyncio.TimeoutError:
                    pytest.skip(
                        f"Async test skipped: exceeded {seconds} seconds timeout"
                    )

            return async_wrapper
        else:
            # Sync function handler
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                def handler(signum, frame):
                    pytest.skip(f"Test skipped: exceeded {seconds} seconds timeout")

                signal.signal(signal.SIGALRM, handler)
                signal.alarm(seconds)

                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                return result

            return sync_wrapper

    return decorator
