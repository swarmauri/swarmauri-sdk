import time
import logging
import httpx
from functools import wraps
from typing import List
import asyncio  # Import asyncio to use async sleep

def retry_on_status_codes(
    status_codes: List[int] = [429], 
    max_retries: int = 3, 
    retry_delay: int = 2
):
    """
    A decorator to retry a function call when one of the provided status codes is encountered,
    with exponential backoff.

    Parameters:
    - status_codes: List of HTTP status codes that should trigger retries (default [429]).
    - max_retries: The maximum number of retries (default 3).
    - retry_delay: The initial delay between retries, in seconds (default 2).
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):  # Make the wrapper async
            attempt = 0
            while attempt < max_retries:
                try:
                    return await func(*args, **kwargs)  # Use await to call the async function
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in status_codes:
                        attempt += 1
                        backoff_time = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                        logging.warning(f"Received status {e.response.status_code}. Retrying in {backoff_time} seconds... Attempt {attempt}/{max_retries}")
                        await asyncio.sleep(backoff_time)  # Use asyncio.sleep for async functions
                    else:
                        # If the error code is not in the retry list, raise the error
                        raise
            # If retries are exhausted, raise an exception
            logging.error(f"Failed after {max_retries} retries due to rate limit or other status codes.")
            raise Exception(f"Failed after {max_retries} retries due to {status_codes}.")
        
        return wrapper
    return decorator
