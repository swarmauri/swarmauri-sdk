import pytest
import httpx

from tigrbl_spiffe.adapters import Endpoint, TigrblClientAdapter, Txn


@pytest.mark.asyncio
async def test_for_endpoint_uds_returns_transaction():
    adapter = TigrblClientAdapter()
    txn = await adapter.for_endpoint(
        Endpoint(scheme="uds", address="unix:///var/run/workload.sock")
    )
    assert isinstance(txn, Txn)
    assert txn.kind == "uds"
    assert txn.uds_path == "/var/run/workload.sock"
    assert txn.http is None


@pytest.mark.asyncio
async def test_for_endpoint_http_creates_async_client():
    adapter = TigrblClientAdapter()
    txn = await adapter.for_endpoint(
        Endpoint(scheme="http", address="http://example.test")
    )
    assert txn.kind == "http"
    assert isinstance(txn.http, httpx.AsyncClient)
    assert str(txn.http.base_url) == "http://example.test"
    await txn.http.aclose()


@pytest.mark.asyncio
async def test_for_endpoint_https_creates_async_client():
    adapter = TigrblClientAdapter()
    txn = await adapter.for_endpoint(
        Endpoint(scheme="https", address="https://secure.test", timeout_s=9.5)
    )
    assert txn.kind == "https"
    assert isinstance(txn.http, httpx.AsyncClient)
    assert txn.http.timeout.read == 9.5
    await txn.http.aclose()


@pytest.mark.asyncio
async def test_for_endpoint_unknown_scheme_raises():
    adapter = TigrblClientAdapter()
    with pytest.raises(ValueError):
        await adapter.for_endpoint(Endpoint(scheme="smtp", address="smtp://example"))
