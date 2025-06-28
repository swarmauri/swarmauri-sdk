import pytest
import httpx
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@pytest.mark.asyncio
@pytest.mark.unit
async def test_retry_async_exhausts_retries():
    call_count = 0

    @retry_on_status_codes([429], max_retries=3, retry_delay=0)
    async def failing():
        nonlocal call_count
        call_count += 1
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(status_code=429, request=request)
        raise httpx.HTTPStatusError(
            "Too Many Requests", request=request, response=response
        )

    with pytest.raises(Exception) as exc_info:
        await failing()

    assert call_count == 3
    assert "failed after 3 retries" in str(exc_info.value)


@pytest.mark.unit
def test_retry_sync_eventual_success():
    call_count = 0

    @retry_on_status_codes([429], max_retries=3, retry_delay=0)
    def sometimes_fails():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            request = httpx.Request("GET", "http://test")
            response = httpx.Response(status_code=429, request=request)
            raise httpx.HTTPStatusError(
                "Too Many Requests", request=request, response=response
            )
        return "ok"

    assert sometimes_fails() == "ok"
    assert call_count == 3


@pytest.mark.unit
def test_retry_sync_unhandled_status():
    call_count = 0

    @retry_on_status_codes([429], max_retries=3, retry_delay=0)
    def fail():
        nonlocal call_count
        call_count += 1
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(status_code=500, request=request)
        raise httpx.HTTPStatusError("Server Error", request=request, response=response)

    with pytest.raises(httpx.HTTPStatusError):
        fail()

    assert call_count == 1
