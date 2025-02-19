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
            # Check for a running loop without assignment.
            asyncio.get_running_loop()
            return func(*args, **kwargs)
        except RuntimeError:
            return asyncio.run(func(*args, **kwargs))

    return wrapper
