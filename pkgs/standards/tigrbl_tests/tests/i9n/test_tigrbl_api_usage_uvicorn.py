import httpx
import pytest
import pytest_asyncio
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import App, Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


bearer = HTTPBearer()


def auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(bearer),
) -> HTTPAuthorizationCredentials:
    return credentials


class Alpha(Base, GUIDPk):
    __tablename__ = "alpha_api_usage"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class Beta(Base, GUIDPk):
    __tablename__ = "beta_api_usage"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


@pytest_asyncio.fixture()
async def running_api():
    app = App()
    api = TigrblApi(engine=mem(async_=False))
    api.set_auth(authn=auth_dependency, allow_anon=False)
    api.include_models([Alpha, Beta])
    api.initialize()
    app.include_router(api)

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_api_deploys_and_serves_openapi(running_api) -> None:
    base_url = running_api

    async with httpx.AsyncClient() as client:
        openapi_resp = await client.get(f"{base_url}/openapi.json")

    assert openapi_resp.status_code == 200
    openapi = openapi_resp.json()
    paths = openapi["paths"]

    assert "/alpha" in paths
    assert "/alpha/{item_id}" in paths
    assert "/beta" in paths
    assert "/beta/{item_id}" in paths
    assert {"get", "post", "delete"}.issubset(paths["/alpha"])
    assert {"get", "patch", "put", "delete"}.issubset(paths["/alpha/{item_id}"])

    security_schemes = openapi.get("components", {}).get("securitySchemes", {})
    assert "HTTPBearer" in security_schemes


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_api_handles_authenticated_request(running_api) -> None:
    base_url = running_api
    headers = {"Authorization": "Bearer demo"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/alpha",
            json={"name": "Alpha"},
            headers=headers,
        )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["name"] == "Alpha"
