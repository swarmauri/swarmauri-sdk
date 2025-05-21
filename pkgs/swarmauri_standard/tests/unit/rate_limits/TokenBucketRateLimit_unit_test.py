import time
import pytest
from swarmauri_standard.rate_limits.TokenBucketRateLimit import TokenBucketRateLimit
from swarmauri_base.ComponentBase import ResourceTypes


@pytest.fixture
def rate_limit():
    return TokenBucketRateLimit(capacity=2, refill_rate=1)


@pytest.mark.unit
def test_ubc_resource(rate_limit):
    assert rate_limit.resource == ResourceTypes.RATE_LIMIT.value


@pytest.mark.unit
def test_ubc_type(rate_limit):
    assert rate_limit.type == "TokenBucketRateLimit"


@pytest.mark.unit
def test_serialization(rate_limit):
    assert (
        rate_limit.id
        == TokenBucketRateLimit.model_validate_json(rate_limit.model_dump_json()).id
    )


@pytest.mark.unit
def test_allow_tokens(rate_limit):
    assert rate_limit.allow()
    assert rate_limit.available_tokens() <= 1
    assert not rate_limit.allow(2)
    time.sleep(1.1)
    assert rate_limit.allow(2)
