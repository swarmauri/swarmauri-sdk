import asyncio
from functools import wraps

def maybe_async(func):
    """
    If the decorated function is called within an event loop, run async.
    Otherwise, run sync using asyncio.run.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            # If we have a running loop, assume we can await
            return func(*args, **kwargs)
        except RuntimeError:
            # No running loop, run in a fresh event loop
            return asyncio.run(func(*args, **kwargs))
    return wrapper