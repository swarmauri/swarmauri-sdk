from httpx import ASGITransport, Client
from sqlalchemy import Column, String
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk


def _build_app():
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_openrpc"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app, Widget


def test_openrpc_endpoint_exposed():
    app, _ = _build_app()
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        response = client.get("/rpc/openrpc.json")

        assert response.status_code == 200
        payload = response.json()
        assert payload["openrpc"] == "1.2.6"
        assert "methods" in payload


def test_openrpc_includes_method_schema():
    app, model = _build_app()
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/rpc/openrpc.json").json()
        methods = {method["name"]: method for method in payload["methods"]}

        create_method = methods[f"{model.__name__}.create"]
        assert create_method["paramStructure"] == "by-name"

        params = create_method["params"][0]["schema"]
        assert params["title"].startswith(model.__name__)
        assert "Create" in params["title"]

        result = create_method["result"]["schema"]
        assert result["title"].startswith(model.__name__)
        assert "Response" in result["title"]
