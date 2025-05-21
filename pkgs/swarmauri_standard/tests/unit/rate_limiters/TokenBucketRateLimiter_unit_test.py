import time
import pytest

from swarmauri_standard.rate_limiters import TokenBucketRateLimiter


@pytest.mark.unit
def test_acquire_blocks_until_token_available():
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate=10)

    start = time.time()
    limiter.acquire()
    limiter.acquire()
    elapsed = time.time() - start
    assert elapsed >= 0.09
