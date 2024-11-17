import time
import logging
import httpx
from functools import wraps
from typing import List, Callable, Any
import asyncio
import inspect


def retry_on_status_codes(
    status_codes: List[int] = [429], max_retries: int = 3, retry_delay: int = 2
):
    """
    A decorator to retry both sync and async functions when specific status codes are encountered,
    with exponential backoff.

    Parameters:
    - status_codes: List of HTTP status codes that should trigger retries (default [429]).
    - max_retries: The maximum number of retries (default 3).
    - retry_delay: The initial delay between retries, in seconds (default 2).
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while attempt < max_retries:
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in status_codes:
                        attempt += 1
                        if attempt == max_retries:
                            break
                        backoff_time = retry_delay * (2 ** (attempt - 1))
                        logging.warning(
                            f"Received status {e.response.status_code}. "
                            f"Retrying in {backoff_time} seconds... "
                            f"Attempt {attempt}/{max_retries}"
                        )
                        await asyncio.sleep(backoff_time)
                    else:
                        raise

            logging.error(
                f"Failed after {max_retries} retries due to rate limit or other status codes."
            )
            raise Exception(
                f"Failed after {max_retries} retries due to {status_codes}."
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in status_codes:
                        attempt += 1
                        if attempt == max_retries:
                            break
                        backoff_time = retry_delay * (2 ** (attempt - 1))
                        logging.warning(
                            f"Received status {e.response.status_code}. "
                            f"Retrying in {backoff_time} seconds... "
                            f"Attempt {attempt}/{max_retries}"
                        )
                        time.sleep(backoff_time)
                    else:
                        raise

            logging.error(
                f"Failed after {max_retries} retries due to rate limit or other status codes."
            )
            raise Exception(
                f"Failed after {max_retries} retries due to {status_codes}."
            )

        # Check if the function is async or sync and return appropriate wrapper
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
