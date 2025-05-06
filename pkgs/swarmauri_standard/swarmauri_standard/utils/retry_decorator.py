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
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            attempt = 0
            while attempt < max_retries:
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in status_codes:
                        attempt += 1
                        last_exception = e
                        if attempt == max_retries:
                            break
                        backoff_time = retry_delay * (2 ** (attempt - 1))
                        logging.warning(
                            f"Retry attempt {attempt}/{max_retries}: "
                            f"Received HTTP {e.response.status_code} for {func.__name__}. "
                            f"Retrying in {backoff_time:.2f} seconds. "
                            f"Original error: {str(e)}"
                        )
                        await asyncio.sleep(backoff_time)
                    else:
                        raise

            if last_exception:
                error_message = (
                    f"Request to {func.__name__} failed after {max_retries} retries. "
                    f"Last encountered status code: {last_exception.response.status_code}. "
                    f"Last error details: {str(last_exception)}"
                )
                logging.error(error_message)
                raise Exception(error_message)
            raise RuntimeError(
                f"Unexpected error in retry mechanism for {func.__name__}"
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            attempt = 0
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in status_codes:
                        attempt += 1
                        last_exception = e
                        if attempt == max_retries:
                            break
                        backoff_time = retry_delay * (2 ** (attempt - 1))
                        logging.warning(
                            f"Retry attempt {attempt}/{max_retries}: "
                            f"Received HTTP {e.response.status_code} for {func.__name__}. "
                            f"Retrying in {backoff_time:.2f} seconds. "
                            f"Original error: {str(e)}"
                        )
                        time.sleep(backoff_time)
                    else:
                        raise

            if last_exception:
                error_message = (
                    f"Request to {func.__name__} failed after {max_retries} retries. "
                    f"Last encountered status code: {last_exception.response.status_code}. "
                    f"Last error details: {str(last_exception)}"
                )
                logging.error(error_message)
                raise Exception(error_message)
            raise RuntimeError(
                f"Unexpected error in retry mechanism for {func.__name__}"
            )

        # Check if the function is async or sync and return appropriate wrapper
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
