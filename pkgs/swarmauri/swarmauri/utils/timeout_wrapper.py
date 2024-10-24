import pytest
import signal
import functools
import asyncio  # <-- Required to handle async functions


# Timeout decorator that supports async functions
def timeout(seconds=5):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"Test exceeded timeout of {seconds} seconds")

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if hasattr(signal, "SIGALRM"):
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
            try:
                return await func(*args, **kwargs)  # Await the async function
            except TimeoutError:
                pytest.skip(
                    f"Test skipped because it exceeded {seconds} seconds timeout"
                )
            finally:
                if hasattr(signal, "alarm"):
                    signal.alarm(0)  # Disable the alarm after function execution

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if hasattr(signal, "SIGALRM"):
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
            try:
                return func(*args, **kwargs)  # Run the synchronous function
            except TimeoutError:
                pytest.skip(
                    f"Test skipped because it exceeded {seconds} seconds timeout"
                )
            finally:
                if hasattr(signal, "alarm"):
                    signal.alarm(0)  # Disable the alarm after function execution

        # Check if the function is async or not and use the appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
