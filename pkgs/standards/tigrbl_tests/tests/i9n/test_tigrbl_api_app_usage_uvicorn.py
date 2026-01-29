import httpx
import pytest
import pytest_asyncio
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tigrbl import Base, TigrblApi, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


bearer = HTTPBearer()


def auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(bearer),
) -> HTTPAuthorizationCredentials:
    return credentials


class Kappa(Base, GUIDPk):
    __tablename__ = "kappa_api_app_usage"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class KappaApi(TigrblApi):
    MODELS = (Kappa,)


@pytest_asyncio.fixture()
async def running_api_app():
    api = KappaApi(engine=mem(async_=False))
    api.set_auth(authn=auth_dependency, allow_anon=False)
    api.include_models([Kappa])
    api.initialize()

    class KappaApp(TigrblApp):
        APIS = (api,)

    app = KappaApp(engine=mem(async_=False))
    app.include_router(api)

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_api_app_deploys_and_serves_openapi(running_api_app) -> None:
    base_url = running_api_app

    async with httpx.AsyncClient() as client:
        openapi_resp = await client.get(f"{base_url}/openapi.json")

    assert openapi_resp.status_code == 200
    openapi = openapi_resp.json()
    paths = openapi["paths"]

    assert "/kappa" in paths
    assert "/kappa/{item_id}" in paths
    assert {"get", "post", "delete"}.issubset(paths["/kappa"])
    assert {"get", "patch", "put", "delete"}.issubset(paths["/kappa/{item_id}"])

    security_schemes = openapi.get("components", {}).get("securitySchemes", {})
    assert "HTTPBearer" in security_schemes


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_api_app_handles_authenticated_request(running_api_app) -> None:
    base_url = running_api_app
    headers = {"Authorization": "Bearer demo"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/kappa",
            json={"name": "Kappa"},
            headers=headers,
        )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["name"] == "Kappa"
