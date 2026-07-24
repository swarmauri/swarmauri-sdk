import asyncio
import inspect
import logging
import time
from collections.abc import Collection
from functools import wraps
from typing import Any, Callable, Optional, Union

import httpx


RetryCodes = Union[Collection[int], Callable[[Any], Collection[int]]]
RetryValue = Union[int, float, Callable[[Any], int | float]]


def _resolve(value: Any, instance: Any, fallback: Any) -> Any:
    if callable(value):
        return value(instance)
    if value is not None:
        return value
    return fallback


def retry_on_status_codes(
    status_codes: Optional[RetryCodes] = None,
    max_retries: Optional[RetryValue] = None,
    retry_delay: Optional[RetryValue] = None,
):
    """
    A decorator to retry both sync and async functions when specific status
    codes are encountered,
    with exponential backoff.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = args[0] if args else None
            resolved_codes = set(
                _resolve(
                    status_codes,
                    instance,
                    getattr(instance, "retryable_status_codes", {429}),
                )
            )
            resolved_retries = int(
                _resolve(
                    max_retries,
                    instance,
                    getattr(instance, "max_retries", 3),
                )
            )
            resolved_delay = float(
                _resolve(
                    retry_delay,
                    instance,
                    getattr(instance, "retry_delay", 2),
                )
            )
            last_exception = None
            attempt = 0
            while attempt < resolved_retries:
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in resolved_codes:
                        attempt += 1
                        last_exception = e
                        if attempt == resolved_retries:
                            break
                        backoff_time = resolved_delay * (2 ** (attempt - 1))
                        logging.warning(
                            f"Retry attempt {attempt}/{resolved_retries}: "
                            f"Received HTTP {e.response.status_code} for "
                            f"{func.__name__}. "
                            f"Retrying in {backoff_time:.2f} seconds. "
                            f"Original error: {str(e)}"
                        )
                        await asyncio.sleep(backoff_time)
                    else:
                        raise

            if last_exception:
                error_message = (
                    f"Request to {func.__name__} failed after "
                    f"{resolved_retries} retries. Last encountered status "
                    f"code: {last_exception.response.status_code}. Last "
                    f"error details: {last_exception}"
                )
                logging.error(error_message)
                raise Exception(error_message) from last_exception
            raise RuntimeError(
                f"Unexpected error in retry mechanism for {func.__name__}"
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = args[0] if args else None
            resolved_codes = set(
                _resolve(
                    status_codes,
                    instance,
                    getattr(instance, "retryable_status_codes", {429}),
                )
            )
            resolved_retries = int(
                _resolve(
                    max_retries,
                    instance,
                    getattr(instance, "max_retries", 3),
                )
            )
            resolved_delay = float(
                _resolve(
                    retry_delay,
                    instance,
                    getattr(instance, "retry_delay", 2),
                )
            )
            last_exception = None
            attempt = 0
            while attempt < resolved_retries:
                try:
                    return func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in resolved_codes:
                        attempt += 1
                        last_exception = e
                        if attempt == resolved_retries:
                            break
                        backoff_time = resolved_delay * (2 ** (attempt - 1))
                        logging.warning(
                            f"Retry attempt {attempt}/{resolved_retries}: "
                            f"Received HTTP {e.response.status_code} for "
                            f"{func.__name__}. "
                            f"Retrying in {backoff_time:.2f} seconds. "
                            f"Original error: {str(e)}"
                        )
                        time.sleep(backoff_time)
                    else:
                        raise

            if last_exception:
                error_message = (
                    f"Request to {func.__name__} failed after "
                    f"{resolved_retries} retries. Last encountered status "
                    f"code: {last_exception.response.status_code}. Last "
                    f"error details: {last_exception}"
                )
                logging.error(error_message)
                raise Exception(error_message) from last_exception
            raise RuntimeError(
                f"Unexpected error in retry mechanism for {func.__name__}"
            )

        # Check if the function is async or sync and return appropriate wrapper
        return (
            async_wrapper
            if inspect.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator
