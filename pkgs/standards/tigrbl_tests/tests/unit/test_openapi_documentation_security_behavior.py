from __future__ import annotations

from httpx import ASGITransport, Client
from sqlalchemy import Column, String

from tigrbl import (
    APIKey,
    HTTPBearer,
    MutualTLS,
    OAuth2,
    OpenIdConnect,
    TigrblApp,
    TigrblRouter,
)
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.shortcuts.engine import mem
from tigrbl.types import Security


def _bearer_dep(cred=Security(HTTPBearer(scheme_name="BearerAuth"))):
    return cred


def _api_key_dep(cred=Security(APIKey(scheme_name="ApiKeyAuth", name="X-API-Key"))):
    return cred


def _oauth2_dep(
    cred=Security(
        OAuth2(
            scheme_name="OAuth2Auth",
            flows={"clientCredentials": {"tokenUrl": "https://issuer.example/token"}},
        )
    ),
):
    return cred


def _openid_dep(
    cred=Security(
        OpenIdConnect(
            scheme_name="OpenIdAuth",
            openid_connect_url="https://issuer.example/.well-known/openid-configuration",
        )
    ),
):
    return cred


def _mtls_dep(cred=Security(MutualTLS(scheme_name="MutualTLSAuth"))):
    return cred


class AppDocsTable(TableBase, GUIDPk):
    __tablename__ = "app_docs_table_openapi"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias="read", target="read", secdeps=(_bearer_dep,)),)


class RouterDocsTable(TableBase, GUIDPk):
    __tablename__ = "router_docs_table_openapi"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias="read", target="read", secdeps=(_api_key_dep,)),)


class TableDocsTable(TableBase, GUIDPk):
    __tablename__ = "table_docs_table_openapi"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(
            alias="read",
            target="read",
            secdeps=(_oauth2_dep, _openid_dep, _mtls_dep),
        ),
    )


def test_openapi_docs_cover_app_router_table_and_all_security_schemes() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(AppDocsTable)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(RouterDocsTable)
    router.include_table(TableDocsTable)
    app.include_router(router)

    app.initialize()

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        openapi = client.get("/openapi.json").json()

    documented_security = [
        security
        for path_item in openapi["paths"].values()
        for op in path_item.values()
        if isinstance(op, dict)
        for security in op.get("security", [])
    ]

    assert {"BearerAuth": []} in documented_security
    assert {"ApiKeyAuth": []} in documented_security
    assert {"OAuth2Auth": []} in documented_security
    assert {"OpenIdAuth": []} in documented_security
    assert {"MutualTLSAuth": []} in documented_security

    security_schemes = openapi["components"].get("securitySchemes", {})
    assert security_schemes == {
        "BearerAuth": {"type": "http", "scheme": "bearer"},
        "ApiKeyAuth": {"type": "apiKey", "name": "X-API-Key", "in": "header"},
        "OAuth2Auth": {
            "type": "oauth2",
            "flows": {
                "clientCredentials": {"tokenUrl": "https://issuer.example/token"}
            },
        },
        "OpenIdAuth": {
            "type": "openIdConnect",
            "openIdConnectUrl": "https://issuer.example/.well-known/openid-configuration",
        },
        "MutualTLSAuth": {"type": "mutualTLS"},
    }
