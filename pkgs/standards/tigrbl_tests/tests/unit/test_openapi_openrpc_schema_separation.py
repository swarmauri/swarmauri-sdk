from httpx import ASGITransport, Client

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_openapi_openrpc_separation"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


def _build_app() -> TigrblApp:
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app


def test_openapi_schema_excludes_openrpc_endpoint() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    assert "/openrpc.json" not in payload["paths"]


def test_openrpc_schema_excludes_openapi_endpoint() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    method_names = {method["name"].lower() for method in payload["methods"]}
    assert all("openapi" not in name for name in method_names)
    assert all("openrpc" not in name for name in method_names)
