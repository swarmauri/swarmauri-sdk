import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI as FastAPILib

from tigrbl.api import _api
from tigrbl.api._api import APIRouter


def _build_fastapi():
    app = FastAPILib(title="Parity", version="0.0.1")

    @app.get("/items/{item_id}", tags=["items"], summary="Get item")
    def read_item(item_id: str):
        return {"id": item_id}

    return app


def _build_stdapi():
    app = APIRouter(title="Parity", version="0.0.1", include_docs=True)

    @app.get("/items/{item_id}", tags=["items"], summary="Get item")
    def read_item(item_id: str):
        return {"id": item_id}

    return app


def test_parity_openapi_shapes():
    fastapi_app = _build_fastapi()
    std_app = _build_stdapi()

    fast_schema = fastapi_app.openapi()
    std_schema = std_app.openapi()

    assert "/items/{item_id}" in fast_schema["paths"]
    assert "/items/{item_id}" in std_schema["paths"]

    fast_op = fast_schema["paths"]["/items/{item_id}"]["get"]
    std_op = std_schema["paths"]["/items/{item_id}"]["get"]

    assert fast_op["summary"] == std_op["summary"] == "Get item"
    assert fast_op["tags"] == std_op["tags"] == ["items"]
    assert any(p["name"] == "item_id" for p in fast_op["parameters"])
    assert any(p["name"] == "item_id" for p in std_op["parameters"])


def test_parity_e2e_response():
    fastapi_app = _build_fastapi()
    std_app = _build_stdapi()

    async def _run():
        fast_transport = ASGITransport(app=fastapi_app)
        std_transport = ASGITransport(app=std_app)
        async with AsyncClient(
            transport=fast_transport, base_url="http://test"
        ) as fast_client:
            async with AsyncClient(
                transport=std_transport, base_url="http://test"
            ) as std_client:
                return await fast_client.get("/items/42"), await std_client.get(
                    "/items/42"
                )

    fast_resp, std_resp = asyncio.run(_run())

    assert fast_resp.status_code == std_resp.status_code == 200
    assert fast_resp.json() == std_resp.json() == {"id": "42"}


@pytest.mark.xfail(reason="FastAPI shim removed from tigrbl.api._api", strict=False)
def test_api_module_fastapi_shim_removed():
    assert not hasattr(_api, "FastAPI")
