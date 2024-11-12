import time
import logging
import httpx
from functools import wraps

MAX_RETRIES = 5
RETRY_DELAY = 2  # Initial delay in seconds

def retry_on_status_codes(status_codes):
    """
    A decorator to retry a function call when one of the provided status codes is encountered,
    with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < MAX_RETRIES:
                try:
                    return func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in status_codes:
                        attempt += 1
                        backoff_time = RETRY_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                        logging.warning(f"Received status {e.response.status_code}. Retrying in {backoff_time} seconds... Attempt {attempt}/{MAX_RETRIES}")
                        time.sleep(backoff_time)
                    else:
                        # If the error code is not in the retry list, raise the error
                        raise
            # If retries are exhausted, raise an exception
            logging.error(f"Failed after {MAX_RETRIES} retries due to rate limit or other status codes.")
            raise Exception(f"Failed after {MAX_RETRIES} retries due to {status_codes}.")
        
        return wrapper
    return decorator
