from httpx import ASGITransport, Client
from sqlalchemy import Column, String

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl.security import HTTPBearer
from tigrbl.types import Security


def _alpha_dep(cred=Security(HTTPBearer(scheme_name="AlphaToken"))):
    return cred


def _beta_dep(cred=Security(HTTPBearer(scheme_name="BetaToken"))):
    return cred


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_docs_security_parity"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(alias="list", target="list"),
        OpSpec(alias="read", target="read", secdeps=(_alpha_dep,)),
        OpSpec(alias="create", target="create", secdeps=(_alpha_dep, _beta_dep)),
    )


def test_openapi_and_openrpc_security_are_derived_from_opspec_secdeps() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        openapi = client.get("/openapi.json").json()
        openrpc = client.get("/openrpc.json").json()

    read_security = openapi["paths"]["/widget/{item_id}"]["get"].get("security")
    create_security = openapi["paths"]["/widget"]["post"].get("security")
    assert read_security == [{"AlphaToken": []}]
    assert create_security == [{"AlphaToken": []}, {"BetaToken": []}]

    method_map = {method["name"]: method for method in openrpc["methods"]}
    assert method_map["Widget.list"].get("security") is None
    assert method_map["Widget.read"]["security"] == [{"AlphaToken": []}]
    assert method_map["Widget.create"]["security"] == [
        {"AlphaToken": []},
        {"BetaToken": []},
    ]

    openapi_schemes = openapi["components"]["securitySchemes"]
    openrpc_schemes = openrpc["components"]["securitySchemes"]
    assert set(openapi_schemes) >= {"AlphaToken", "BetaToken"}
    assert set(openrpc_schemes) >= {"AlphaToken", "BetaToken"}
